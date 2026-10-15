"""Acumatica Authentication."""

from __future__ import annotations

from hotglue_singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from typing_extensions import override


class AcumaticaAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Acumatica."""

    @override
    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the Acumatica API.

        Returns:
            A dict with the request body
        """
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self._tap.config["refresh_token"],
            "grant_type": "refresh_token",
        }
