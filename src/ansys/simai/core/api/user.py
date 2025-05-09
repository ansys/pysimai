# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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
from ansys.simai.core.data.types import APIResponse


class UserClientMixin(ApiClientMixin):
    """Provides the client for the User ("/users") part of the API."""

    def list_users(self) -> APIResponse:
        return self._get("users")

    def get_user(self, id: str) -> APIResponse:
        return self._get(f"users/{id}")

    def invite_user(self, email: str, role: str) -> APIResponse:
        return self._post("users", json={"email": email, "role": role})

    def delete_user(self, id: str) -> None:
        self._delete(f"users/{id}", return_json=False)

    def give_admin_rights(self, id: str) -> None:
        self._put(f"users/{id}/administrative-rights", return_json=False)

    def remove_admin_rights(self, id: str) -> None:
        self._delete(f"users/{id}/administrative-rights", return_json=False)

    def transfer_organization_ownership(self, id: str) -> None:
        self._post(f"users/{id}/ownership-transfer", return_json=False)
