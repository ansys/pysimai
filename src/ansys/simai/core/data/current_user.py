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
class Consent:
    """Represents a consent granted by the current user to a client (like the SDK)."""

    client_id: str
    """The client ID that has been granted offline access."""
    created_date: datetime
    """When the consent was originally granted."""
    last_updated_date: datetime
    """When the consent was last updated."""
    granted_scopes: List[str]
    """List of scopes granted to this client."""

    def __repr__(self) -> str:
        return f"<Consent: {self.client_id}, created: {self.created_date!s}, last updated: {self.last_updated_date!s}>"


class ConsentDirectory:
    """Provides access to consent management operations.

    Consents represent the authorization records that grant a client (like the SDK)
    permission to use offline tokens for authentication.

    Example:
        .. code-block:: python

            import ansys.simai.core as asc

            simai_client = asc.from_config()

            # List all consents
            consents = simai_client.me.consents.list()
            for consent in consents:
                print(f"Client: {consent.client_id}, Created: {consent.created_date}")

            # Revoke a specific consent
            simai_client.me.consents.revoke("sdk")
    """

    def __init__(self, client: "SimAIClient"):
        self._client = client

    def list(self) -> List[Consent]:
        """List all offline access consents for the current user.

        Returns:
            List of :class:`Consent` objects representing the user's offline access consents.

        Example:
            .. code-block:: python

                consents = simai_client.me.consents.list()
                for consent in consents:
                    print(f"Client: {consent.client_id}")
                    print(f"  Created: {consent.created_date}")
                    print(f"  Scopes: {consent.granted_scopes}")
        """
        raw_consents = self._client._api.get_offline_tokens()
        return [
            Consent(
                client_id=consent["client_id"],
                created_date=datetime.fromisoformat(consent["created_date"]),
                last_updated_date=datetime.fromisoformat(consent["last_updated_date"]),
                granted_scopes=consent.get("granted_scopes", []),
            )
            for consent in raw_consents
        ]

    def revoke(self, client_id: str) -> None:
        """Revoke an offline access consent for the current user.

        This will invalidate the consent associated with the given client ID,
        preventing any further use of offline tokens for that client.

        Args:
            client_id: The client ID of the consent to revoke.

        Raises:
            NotFoundError: If no consent exists for the given client ID.

        Example:
            .. code-block:: python

                # Revoke consent for the SDK client
                simai_client.me.consents.revoke("sdk")

        Warning:
            Revoking a consent will invalidate any offline tokens associated with
            that client. Server-side workflows using those tokens will stop working.
        """
        self._client._api.revoke_offline_token(client_id)


class CurrentUser:
    """Provides access to current user self-management operations.

    This class allows users to manage their own account settings, generate
    offline tokens, and manage consents.

    Example:
        .. code-block:: python

            import ansys.simai.core as asc

            simai_client = asc.from_config()

            # Generate an offline token
            token = simai_client.me.generate_offline_token()

            # List all consents
            consents = simai_client.me.consents.list()
            for consent in consents:
                print(f"Client: {consent.client_id}, Created: {consent.created_date}")

            # Revoke a specific consent
            simai_client.me.consents.revoke("sdk")
    """

    def __init__(self, client: "SimAIClient"):
        self._client = client
        self._consents = ConsentDirectory(client)

    @property
    def consents(self) -> ConsentDirectory:
        """Access consent management operations.

        Returns:
            :class:`ConsentDirectory` for managing offline access consents.
        """
        return self._consents

    def generate_offline_token(self) -> str:
        """Generate a new offline token for the current user.

        This creates a long-lived refresh token that can be used for authentication
        without requiring interactive login. The token is associated with the "sdk"
        client ID.

        Returns:
            The offline token string that can be stored and used for future authentication.

        Example:
            .. code-block:: python

                # Generate an offline token
                token = simai_client.me.generate_offline_token()
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
