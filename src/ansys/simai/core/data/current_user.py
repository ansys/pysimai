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

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from ansys.simai.core.utils.auth import get_offline_token

if TYPE_CHECKING:
    from ansys.simai.core.client import SimAIClient


@dataclass
class OfflineToken:
    """Represents an offline token (persistent app access) for the current user."""

    client_id: str
    """The client ID that has been granted offline access."""
    created_date: datetime
    """When the consent was originally granted."""
    last_updated_date: datetime
    """When the consent was last updated."""
    granted_scopes: List[str]
    """List of scopes granted to this client."""

    def __repr__(self) -> str:
        return f"<OfflineToken: {self.client_id}, created: {self.created_date!s}, last updated: {self.last_updated_date!s}>"


class OfflineTokenDirectory:
    """Provides access to offline token management operations.

    This class allows users to list, generate, and revoke offline tokens.

    Example:
        .. code-block:: python

            import ansys.simai.core as asc

            simai_client = asc.from_config()

            # List all offline tokens
            tokens = simai_client.me.offline_tokens.list()
            for token in tokens:
                print(f"Client: {token.client_id}, Created: {token.created_date}")

            # Generate a new offline token
            token = simai_client.me.offline_tokens.generate()

            # Revoke a specific token
            simai_client.me.offline_tokens.revoke("my-client-id")
    """

    def __init__(self, client: "SimAIClient"):
        self._client = client

    def list(self) -> List[OfflineToken]:
        """List all offline tokens for the current user.

        Returns:
            List of :class:`OfflineToken` objects representing the user's offline tokens.

        Example:
            .. code-block:: python

                tokens = simai_client.me.offline_tokens.list()
                for token in tokens:
                    print(f"Client: {token.client_id}")
                    print(f"  Created: {token.created_date}")
                    print(f"  Scopes: {token.granted_scopes}")
        """
        raw_tokens = self._client._api.get_offline_tokens()
        return [
            OfflineToken(
                client_id=token["client_id"],
                created_date=datetime.fromisoformat(token["created_date"]),
                last_updated_date=datetime.fromisoformat(token["last_updated_date"]),
                granted_scopes=token.get("granted_scopes", []),
            )
            for token in raw_tokens
        ]

    def revoke(self, client_id: str) -> None:
        """Revoke an offline token for the current user.

        This will invalidate the offline token associated with the given client ID,
        preventing any further use of that token for authentication.

        Args:
            client_id: The client ID of the token to revoke.

        Raises:
            NotFoundError: If no offline token exists for the given client ID.

        Example:
            .. code-block:: python

                # Revoke a specific offline token
                simai_client.me.offline_tokens.revoke("sdk")

        Warning:
            Revoking an offline token that is used by a server-side workflow will
                prevent that workflow from continuing.
        """
        self._client._api.revoke_offline_token(client_id)

    def generate(self) -> str:
        """Generate a new offline token for the current user.

        This creates a long-lived refresh token that can be used for authentication
        without requiring interactive login. The token is associated with the "sdk"
        client ID.

        Returns:
            The offline token string that can be stored and used for future authentication.

        Example:
            .. code-block:: python

                # Generate an offline token
                token = simai_client.me.offline_tokens.generate()
                print(f"Store this token securely: {token}")
        """
        config = self._client._config
        https_proxy: Optional[str] = str(config.https_proxy) if config.https_proxy else None
        tls_ca_bundle: Optional[str] = None
        if config.tls_ca_bundle is not None:
            if isinstance(config.tls_ca_bundle, str):
                tls_ca_bundle = config.tls_ca_bundle
            else:
                tls_ca_bundle = str(config.tls_ca_bundle)

        return get_offline_token(
            url=str(config.url),
            credentials=config.credentials,
            https_proxy=https_proxy,
            tls_ca_bundle=tls_ca_bundle,
        )


class CurrentUser:
    """Provides access to current user self-management operations.

    This class allows users to manage their own account settings and tokens.

    Example:
        .. code-block:: python

            import ansys.simai.core as asc

            simai_client = asc.from_config()

            # List all offline tokens
            tokens = simai_client.me.offline_tokens.list()
            for token in tokens:
                print(f"Client: {token.client_id}, Created: {token.created_date}")

            # Generate a new offline token
            token = simai_client.me.offline_tokens.generate()

            # Revoke a specific token
            simai_client.me.offline_tokens.revoke("my-client-id")
    """

    def __init__(self, client: "SimAIClient"):
        self._client = client
        self._offline_tokens = OfflineTokenDirectory(client)

    @property
    def offline_tokens(self) -> OfflineTokenDirectory:
        """Access offline token management operations.

        Returns:
            :class:`OfflineTokenDirectory` for managing offline tokens.
        """
        return self._offline_tokens
