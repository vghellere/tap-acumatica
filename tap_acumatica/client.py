"""HTTP API client (REST), including AcumaticaStream base class."""

from __future__ import annotations

from functools import cached_property
from typing import Any

import requests
from hotglue_singer_sdk.authenticators import APIAuthenticatorBase
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override


def instance_url(api_url: str) -> str:
    """Return the Acumatica site root, ignoring a trailing slash."""
    return api_url.rstrip("/")


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def fetch_default_endpoint_version(api_url: str) -> str:
    """Return the newest ``Default`` contract version published at ``/entity``."""
    root = instance_url(api_url)
    response = requests.get(f"{root}/entity", timeout=300)
    response.raise_for_status()
    versions = [
        endpoint["version"]
        for endpoint in response.json()["endpoints"]
        if endpoint["name"] == "Default"
    ]
    return max(versions, key=_version_key)


def _unwrap_value(value: Any) -> Any:
    """Return the inner ``value`` from an Acumatica field wrapper."""
    if isinstance(value, dict) and set(value) <= {"value", "error"}:
        return _unwrap_value(value.get("value"))
    if isinstance(value, list):
        return [_unwrap_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _unwrap_value(item) for key, item in value.items()}
    return value


class AcumaticaStream(RESTStream):
    """Acumatica stream class."""

    records_jsonpath = "$[*]"
    next_page_token_jsonpath = None
    page_size = 100
    expand: str | None = None

    @override
    @property
    def url_base(self) -> str:
        """Return the Default entity URL for the configured Acumatica site."""
        root = instance_url(self.config["api_url"])
        version = self._tap.default_endpoint_version
        return f"{root}/entity/Default/{version}"

    @override
    @cached_property
    def authenticator(self) -> APIAuthenticatorBase:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        authenticator_cls, auth_endpoint = self._tap.access_token_support(self._tap)
        return authenticator_cls(self, auth_endpoint=auth_endpoint)

    @override
    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = super().http_headers
        headers["Accept"] = "application/json"
        return headers

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        """Return the next ``$skip`` value, or None when this page is the last."""
        records = response.json()
        if len(records) < self.page_size:
            return None
        skip = 0 if previous_token is None else previous_token
        return skip + len(records)

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return ``$top``/``$skip`` paging and an incremental ``$filter``."""
        params: dict[str, Any] = {
            "$top": self.page_size,
            "$skip": 0 if next_page_token is None else next_page_token,
        }
        if self.replication_key:
            start = self.get_starting_timestamp(context)
            if start is not None:
                params["$filter"] = f"{self.replication_key} ge {start.isoformat()}"
        if self.expand:
            params["$expand"] = self.expand
        return params

    @override
    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        """Unwrap Acumatica ``{"value": ...}`` fields before the record is emitted."""
        return _unwrap_value(row)
