"""Acumatica tap class."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from hotglue_singer_sdk import Stream, Tap
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers
from hotglue_singer_sdk.authenticators import OAuthAuthenticator
from typing_extensions import override

from tap_acumatica.auth import AcumaticaAuthenticator
from tap_acumatica.client import fetch_default_endpoint_version, instance_url
from tap_acumatica.streams import (
    AccountsStream,
    CompaniesStream,
    VendorsStream,
)

STREAM_TYPES = [
    AccountsStream,
    CompaniesStream,
    VendorsStream,
]


class TapAcumatica(Tap):
    """Singer tap for Acumatica."""

    name = "tap-acumatica"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
            default="2000-01-01T00:00:00Z",
        ),
        th.Property(
            "api_url",
            th.StringType,
            required=True,
            description="Acumatica site URL, such as http://host/AcumaticaSandbox",
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="OAuth client ID for the Acumatica OAuth app",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            description="OAuth client secret for the Acumatica OAuth app",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            description="OAuth refresh token for the Acumatica OAuth app",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]

    @cached_property
    def default_endpoint_version(self) -> str:
        """Return the latest Default endpoint version, fetched once per tap."""
        return fetch_default_endpoint_version(self.config["api_url"])

    @classmethod
    def access_token_support(
        cls,
        connector: Any = None,
    ) -> tuple[type[OAuthAuthenticator], str]:
        """Return the authenticator class and OAuth token endpoint.

        Returns:
            A tuple with the authenticator class and the OAuth token endpoint URL.
        """
        if connector is None:
            return AcumaticaAuthenticator, ""
        return (
            AcumaticaAuthenticator,
            f"{instance_url(connector.config['api_url'])}/identity/connect/token",
        )


if __name__ == "__main__":
    TapAcumatica.cli()
