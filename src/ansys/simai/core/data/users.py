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

from typing import List
from ansys.simai.core.data.base import Directory, DataModel
from ansys.simai.core.errors import InvalidArguments


class User(DataModel):
    """Provides the local representation of a user object."""

    def __repr__(self) -> str:
        return f"<User: {self.id}, {self.email}, {self.role}{', unverified' if not self.verified else ''}>"

    @property
    def email(self) -> str:
        """The email address associated to the user."""
        return self.fields["email"]

    @property
    def role(self) -> str:
        """The role that the user has in the organization.

        The role determines access to some platform functionalities

        Can be one of `"owner"`, `"admin"`, `"member"` or `"guest"`.
        """
        return self.fields["role"]

    @property
    def verified(self) -> bool:
        return self.fields["verified"]

    def promote(self) -> None:
        """Promote a member to admin.

        Only an admin or owner of the organization can promote a user.
        """
        self._client._api.give_admin_rights(self.id)

    def demote(self) -> None:
        """Demote an admin to member.

        Only an admin or owner of the organization can demote another administrator.
        """
        self._client._api.remove_admin_rights(self.id)

    def remove(self) -> None:
        """Remove a user from the organization.

        The user will lose access to the organization and the associated data.

        Only an admin or owner of the organization can remove a user.
        """
        self._client._api.delete_user(self.id)

    def transfer_ownership(self) -> None:
        """Transfer ownership of the organization to another user.

        Only the owner of an organization can transfer ownership.
        """
        self._client._api.transfer_organization_ownership(self.id)


class UserDirectory(Directory[User]):
    """Provides a collection of method to manage users.

    This class is accessed through ``client.users``.

    Example:
        .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.users.list()
    """

    _data_model = User

    def get(self, id: str) -> User:
        return self._model_from(self._client._api.get_user(id))

    def list(self) -> List[User]:
        """Lists the users that belong to your organization."""
        return [self._model_from(user) for user in self._client._api.list_users()]

    def invite(self, email: str, role: str = "member") -> User:
        """Invite an user to the organization.

        If the user does not exist yet, he will receive an email allowing him to create
        an account on the platform.
        If the user already exists, he will be simply be added to the organization.

        Only owners and admins of an organization can invite users.

        Args:
            email: the address of the user to add to the organization
            role: the role to give to the user inside the organization,
                can be one of `"admin"`, `"member"` or `"guest"`.
        """
        if role not in ["admin", "member", "guest"]:
            raise InvalidArguments(
                f"{role} is not a valid role. Must be one of admin, member or guest."
            )
        return self._model_from(self._client._api.invite_user(email, role))
