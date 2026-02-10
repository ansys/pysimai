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

from ansys.simai.core.api.mixin import ApiClientMixin


class UserClientMixin(ApiClientMixin):
    """Provides the client for the User ("/users") part of the API."""

    def get_offline_tokens(self):
        """List all offline tokens for the current user.

        Returns:
            List of offline token representations.
        """
        return self._get("users/offline-tokens")

    def revoke_offline_token(self, client_id: str) -> None:
        """Revoke an offline token for the current user.

        Args:
            client_id: The client ID of the token to revoke.

        Raises:
            ansys.simai.core.errors.NotFoundError: If no token with that client ID exists.
            ansys.simai.core.errors.ApiClientError: On other HTTP errors.
        """
        self._delete(f"users/offline-tokens/{client_id}", return_json=False)
