# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
import threading
import time
import webbrowser
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, ValidationError
from requests.auth import AuthBase

from ansys.simai.core.errors import ConnectionError
from ansys.simai.core.utils.configuration import ClientConfig, Credentials
from ansys.simai.core.utils.files import get_cache_dir
from ansys.simai.core.utils.requests import handle_response

logger = logging.getLogger(__name__)


class _AuthTokens(BaseModel):
    """Represents the OIDC tokens received from the auth server.

    The class can fetch and refresh these tokens.
    It caches the tokens to disk automatically.
    """

    _EXPIRATION_BUFFER = timedelta(seconds=5)

    cache_file: Optional[str] = None
    access_token: str
    expires_in: int
    refresh_expires_in: int
    expiration: datetime = None
    refresh_expiration: datetime = None
    refresh_token: str
    # ...  (unused fields were removed for simplicity)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.expiration is None:
            now = datetime.utcnow()
            self.expiration = now + timedelta(seconds=self.expires_in)
            self.refresh_expiration = now + timedelta(seconds=self.refresh_expires_in)
        if self.cache_file is not None:
            with open(self.cache_file, "w") as f:
                f.write(self.model_dump_json())

    @classmethod
    def from_cache(cls, file_path: Optional[str]) -> "Optional[_AuthTokens]":
        if file_path is None:
            return None
        try:
            auth = cls.parse_file(file_path)
            # don't return expired auth tokens
            if not auth.is_refresh_token_expired():
                return auth
        except (IOError, json.JSONDecodeError) as e:
            logger.debug(f"Could not read auth cache: {e}")
        except ValidationError as e:
            logger.warning(f"ValidationError while reading auth cache: {e}")
        return None

    @classmethod
    def from_request_direct_grant(
        cls, session: requests.Session, token_url, creds: Credentials
    ) -> "_AuthTokens":
        logger.debug("Getting authentication tokens.")
        request_params = {
            "client_id": "sdk",
            "grant_type": "password",
            "scope": "openid",
            **creds.model_dump(),
        }
        return cls(**handle_response(session.post(token_url, data=request_params)))

    @classmethod
    def from_request_device_auth(
        cls, session: requests.Session, device_auth_url, token_url, cache_file=None
    ) -> "_AuthTokens":
        auth_codes = handle_response(
            session.post(device_auth_url, data={"client_id": "sdk", "scope": "openid"})
        )
        print(  # noqa: T201
            f"Go to {auth_codes['verification_uri']} and enter the code {auth_codes['user_code']}"
        )
        webbrowser.open(auth_codes["verification_uri_complete"])
        while True:
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
                return cls(**handle_response(validation), cache_file=cache_file)
            # polling can't be faster or auth server returns HTTP 400 Slow down
            time.sleep(5)

    def is_token_expired(self):
        return datetime.utcnow() > (self.expiration - self._EXPIRATION_BUFFER)

    def is_refresh_token_expired(self):
        return datetime.utcnow() > (self.refresh_expiration - self._EXPIRATION_BUFFER)

    def refresh(self, session: requests.Session, token_url: str) -> "_AuthTokens":
        logger.debug("Refreshing authentication tokens.")
        request_params = {
            "client_id": "sdk",
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        try:
            return _AuthTokens(
                **handle_response(session.post(token_url, data=request_params)),
                cache_file=self.cache_file,
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(e) from None


def _get_cached_or_request_device_auth(
    session: requests.Session,
    device_auth_url: str,
    token_url: str,
    auth_cache_hash: Optional[str],
):
    auth = None
    auth_cache_path = None
    if auth_cache_hash:  # Try to fetch auth from cache
        auth_cache_path = str(get_cache_dir() / f"tokens-{auth_cache_hash}.json")
        auth = _AuthTokens.from_cache(auth_cache_path)
        if auth:
            try:
                auth = auth.refresh(session, token_url)
            except Exception as e:
                logger.debug(f"Auth refresh error: {e}")
                auth = None
    if auth is None:  # Otherwise request the user to authenticate
        auth = _AuthTokens.from_request_device_auth(
            session, device_auth_url, token_url, auth_cache_path
        )
    return auth


class Authenticator(AuthBase):
    def __init__(self, config: ClientConfig, session: requests.Session) -> None:
        self._session = session
        self._enabled = not getattr(config, "_disable_authentication", False)
        if not self._enabled:
            logger.debug("Disabling authentication logic.")
            return
        self._url_prefix = config.url
        # HACK: start with a slash to override the /v2/ on the api url
        realm_url = urljoin(str(config.url), "/auth/realms/simai")
        self._token_url = f"{realm_url}/protocol/openid-connect/token"
        self._organization_name = config.organization
        self._refresh_timer = None
        if config.credentials:
            auth = _AuthTokens.from_request_direct_grant(
                self._session, self._token_url, config.credentials
            )
        else:
            device_auth_url = f"{realm_url}/protocol/openid-connect/auth/device"
            auth_hash = None if config.disable_cache else config._auth_hash()
            auth = _get_cached_or_request_device_auth(
                self._session, device_auth_url, self._token_url, auth_hash
            )
        self._authentication = auth
        self._schedule_auth_refresh()

    def __call__(self, request: requests.Request) -> requests.Request:
        """Call to prepare the requests.

        Args:
            request: Request to authenticate.

        Returns:
            Request with the authentication.
        """
        request_host = request.url.split("://", 1)[-1]  # ignore protocol part
        if self._enabled and request_host.startswith(self._url_prefix.host):
            is_token_expired = self._authentication.is_token_expired()
            # So the token doesn't expire during requests that upload a large amount of data
            is_request_multipart_data = "multipart/form_data" in request.headers.get(
                "Content-Type", ""
            )
            if is_token_expired or is_request_multipart_data:
                self._refresh_auth()
            request.headers["Authorization"] = f"Bearer {self._authentication.access_token}"
            request.headers["X-Org"] = self._organization_name
        return request

    def _refresh_auth(self):
        """Refresh the authentication."""
        self._authentication = self._authentication.refresh(self._session, self._token_url)
        self._schedule_auth_refresh()

    def _schedule_auth_refresh(self):
        """Schedule authentication refresh to avoids refresh token expiring if the client is idle for a long time."""
        if self._refresh_timer:
            self._refresh_timer.cancel()
        self._refresh_timer = threading.Timer(
            self._authentication.refresh_expires_in - 30, self._refresh_auth
        )
        self._refresh_timer.daemon = True
        self._refresh_timer.start()
