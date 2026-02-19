# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import logging
import os
import random
import threading
import time
import webbrowser
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from filelock import FileLock
from pydantic import BaseModel, ValidationError, model_validator

from ansys.simai.core.errors import ApiClientError
from ansys.simai.core.utils.configuration import ClientConfig, Credentials
from ansys.simai.core.utils.files import get_cache_dir
from ansys.simai.core.utils.requests import handle_response

logger = logging.getLogger(__name__)

# polling can't be faster or auth server returns HTTP 400 Slow down
DEVICE_AUTH_POLLING_INTERVAL = 5
# Try to refresh tokens 300-400 secs before they go bad
# - Randomized to prevent thundering herd
# - Accounts for network latency and clock skew
TOKEN_REFRESH_BUFFER = random.randrange(300, 400)  # noqa: S311 # nosec
TOKEN_EXPIRATION_BUFFER = random.randrange(5, 15)  # noqa: S311 # nosec


class _AuthTokens(BaseModel):
    """Represents the OIDC tokens received from the auth server."""

    access_token: str
    expiration: datetime
    refresh_expiration: datetime
    refresh_token: str
    # ...  (unused fields removed)

    @model_validator(mode="before")
    @classmethod
    def expires_in_to_datetime(cls, data: Any) -> dict:
        if not isinstance(data, dict):
            raise TypeError(f"Expected data to be a dict, got {type(data).__name__}")
        if "expiration" not in data:
            # We want to store "expiration" but API responses contains "expires_in"
            now = datetime.now(timezone.utc)
            data["expiration"] = now + timedelta(seconds=int(data.pop("expires_in")))
            data["refresh_expiration"] = now + timedelta(
                seconds=int(data.pop("refresh_expires_in"))
            )
        return data

    def must_refresh_tokens(self):
        return self.expires_in < TOKEN_REFRESH_BUFFER

    def is_refresh_token_expired(self):
        return self.refresh_expires_in < TOKEN_EXPIRATION_BUFFER

    @property
    def expires_in(self) -> float:
        return (self.expiration - datetime.now(timezone.utc)).total_seconds()

    @property
    def refresh_expires_in(self) -> float:
        return (self.refresh_expiration - datetime.now(timezone.utc)).total_seconds()


def _request_tokens_direct_grant(
    session: httpx.Client,
    token_url: str,
    credentials: Credentials,
    scope: str = "openid",
) -> _AuthTokens:
    """Request tokens via username/password (direct grant)."""
    logger.debug(f"request authentication tokens via direct grant (scope={scope})")
    request_params = {
        "client_id": "sdk",
        "grant_type": "password",
        "scope": scope,
        **credentials.model_dump(),
    }
    return _AuthTokens(**handle_response(session.post(token_url, data=request_params)))


def _request_tokens_device_auth(
    session: httpx.Client,
    token_url: str,
    device_auth_url: str,
    scope: str = "openid",
) -> _AuthTokens:
    """Request tokens via device auth flow (browser-based)."""
    logger.debug(f"request authentication tokens via device auth (scope={scope})")
    auth_codes = handle_response(
        session.post(device_auth_url, data={"client_id": "sdk", "scope": scope})
    )
    print(  # noqa: T201
        f"Go to {auth_codes['verification_uri']} and enter the code {auth_codes['user_code']}"
    )
    webbrowser.open(auth_codes["verification_uri_complete"])
    while True:
        time.sleep(DEVICE_AUTH_POLLING_INTERVAL)
        validation = session.post(
            token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": "sdk",
                "device_code": auth_codes["device_code"],
            },
        )
        if b"authorization_pending" not in validation.content:
            return _AuthTokens(**handle_response(validation))


class _AuthTokensRetriever:
    """Retrieve tokens via ``get_tokens()``.
    It handles caching and the various auth token sources.
    """

    def __init__(
        self,
        credentials: Optional["Credentials"],
        session: httpx.Client,
        auth_cache_hash: str,
        realm_url: str,
        offline_token: Optional[str] = None,
    ) -> None:
        self.credentials = credentials
        self.offline_token = offline_token
        self.session = session
        self.token_url = f"{realm_url}/protocol/openid-connect/token"
        self.device_auth_url = f"{realm_url}/protocol/openid-connect/auth/device"
        self.refresh_timer = threading.Timer(0, lambda: None)
        self.cache_file_path = str(get_cache_dir() / f"tokens-{auth_cache_hash}.json")

    def _get_token_from_cache(self) -> Optional[_AuthTokens]:
        try:
            with open(self.cache_file_path, "r") as f:
                return _AuthTokens.model_validate_json(f.read())
        except FileNotFoundError:
            pass
        except (IOError, json.JSONDecodeError, ValidationError, TypeError) as e:
            logger.info(f"Could not read auth token from cache: {e}")
        return None

    def _request_tokens_direct_grant(self) -> "_AuthTokens":
        if not self.credentials:
            raise RuntimeError("Authentication credentials are missing")
        return _request_tokens_direct_grant(self.session, self.token_url, self.credentials)

    def _request_tokens_device_auth(self) -> "_AuthTokens":
        return _request_tokens_device_auth(self.session, self.token_url, self.device_auth_url)

    def _refresh_auth_tokens(self, refresh_token: str) -> Optional[_AuthTokens]:
        logger.debug("Refreshing authentication tokens.")
        request_params = {
            "client_id": "sdk",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        try:
            return _AuthTokens(
                **handle_response(self.session.post(self.token_url, data=request_params))
            )
        except (httpx.ConnectError, ApiClientError) as e:
            logger.error(f"Could not refresh authentication tokens: {e}")
            return None

    def _schedule_auth_refresh(self, refresh_expires_in: float):
        """Schedule authentication refresh to avoids refresh token expiring if the client is idle for a long time."""
        if refresh_expires_in <= TOKEN_REFRESH_BUFFER:
            # Skip scheduling: refresh token too close to expiration (max SSO session nearly reached)
            return
        self.refresh_timer.cancel()
        self.refresh_timer = threading.Timer(
            refresh_expires_in - TOKEN_REFRESH_BUFFER,
            self.get_tokens,
            kwargs={"force_refresh": True},
        )
        self.refresh_timer.daemon = True
        self.refresh_timer.start()

    def get_tokens(self, force_refresh: bool = False) -> _AuthTokens:
        auth = self._get_token_from_cache()
        if auth and not auth.must_refresh_tokens() and not force_refresh:
            # fast path: avoid locking the tokens, return early
            self._schedule_auth_refresh(auth.refresh_expires_in)
            return auth
        with FileLock(self.cache_file_path + ".lock", timeout=600):
            # slow path: tokens are locked, will get refreshed
            auth = self._get_token_from_cache()  # might have changed while we waited the lock
            if auth and auth.is_refresh_token_expired():
                logger.info("refresh token is expired")
                auth = None
            if auth and (force_refresh or auth.must_refresh_tokens()):
                auth = self._refresh_auth_tokens(auth.refresh_token)
            if auth is None:
                if self.offline_token:
                    auth = self._refresh_auth_tokens(self.offline_token)
                    if not auth:
                        raise RuntimeError("Could not authenticate user with offline token.")
                elif self.credentials:
                    auth = self._request_tokens_direct_grant()
                else:
                    auth = self._request_tokens_device_auth()
            # Use atomic operation (rename) to avoid avoids partial writes
            with open(self.cache_file_path + "~", "w") as f:
                f.write(auth.model_dump_json())
            os.replace(self.cache_file_path + "~", self.cache_file_path)
        self._schedule_auth_refresh(auth.refresh_expires_in)
        return auth


def get_offline_token(
    url: str,
    credentials: Optional[Credentials] = None,
    https_proxy: Optional[str] = None,
    tls_ca_bundle: Optional[str] = None,
) -> str:
    """Get a Keycloak offline token for the given SimAI instance.

    Args:
        url: The SimAI API URL (e.g., "https://api.simai.ansys.com")
        credentials: Username/password credentials. If None, device auth flow is used.
        https_proxy: Optional HTTPS proxy URL
        tls_ca_bundle: Optional path to TLS CA bundle

    Returns:
        The offline token (a refresh_token that does not expire with sessions)
    """
    realm_url = urljoin(url.rstrip("/") + "/", "/auth/realms/simai")
    token_url = f"{realm_url}/protocol/openid-connect/token"
    device_auth_url = f"{realm_url}/protocol/openid-connect/auth/device"

    transport_kwargs: dict[str, Any] = {}
    if https_proxy:
        transport_kwargs["proxy"] = https_proxy
    if tls_ca_bundle:
        transport_kwargs["verify"] = tls_ca_bundle

    with httpx.Client(**transport_kwargs) as session:
        if credentials:
            tokens = _request_tokens_direct_grant(
                session, token_url, credentials, scope="openid offline_access"
            )
        else:
            tokens = _request_tokens_device_auth(
                session, token_url, device_auth_url, scope="openid offline_access"
            )
        return tokens.refresh_token


class Authenticator(httpx.Auth):
    def __init__(self, config: ClientConfig, session: httpx.Client) -> None:
        self._session = session
        self._enabled = not getattr(config, "_disable_authentication", False)
        if not self._enabled:
            logger.debug("Disabling authentication logic.")
            return
        self._url_prefix = config.url
        # HACK: start with a slash to override the /v2/ on the api url
        self._realm_url = urljoin(str(config.url), "/auth/realms/simai")
        self._organization_name = config.organization
        self._refresh_timer = None
        auth_hash = config._auth_hash()
        self.tokens_retriever = _AuthTokensRetriever(
            config.credentials, session, auth_hash, self._realm_url, config.offline_token
        )
        self.tokens_retriever.get_tokens(
            force_refresh=True
        )  # start fetching/refreshing auth tokens

    def auth_flow(self, request: httpx.Request):
        """Call to prepare the requests.

        Args:
            request: Request to authenticate.

        Returns:
            Request with the authentication.
        """
        if not request.url:
            raise ValueError("Request must have a valid URL")
        request_host = request.url.host
        if (
            self._enabled
            and request_host.startswith(self._url_prefix.host)
            and self._realm_url not in str(request.url)
        ):
            # So the token doesn't expire during requests that upload a large amount of data
            is_request_multipart_data = "multipart/form_data" in request.headers.get(
                "Content-Type", ""
            )
            auth = self.tokens_retriever.get_tokens(force_refresh=is_request_multipart_data)
            request.headers["Authorization"] = f"Bearer {auth.access_token}"
            request.headers["X-Org"] = self._organization_name
        yield request
