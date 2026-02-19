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

from datetime import datetime, timezone

import pytest

from ansys.simai.core.data.current_user import Consent
from ansys.simai.core.errors import NotFoundError


def test_list_consents(simai_client, httpx_mock):
    """WHEN listing consents
    THEN the API is called and consents are returned as Consent objects.
    """
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/users/offline-tokens",
        json=[
            {
                "client_id": "sdk",
                "created_date": "2025-01-15T10:30:00+00:00",
                "last_updated_date": "2025-01-16T14:20:00+00:00",
                "granted_scopes": ["openid", "offline_access"],
            },
            {
                "client_id": "webapp",
                "created_date": "2025-01-10T08:00:00+00:00",
                "last_updated_date": "2025-01-10T08:00:00+00:00",
                "granted_scopes": ["openid"],
            },
        ],
        status_code=200,
    )

    consents = simai_client.me.consents.list()

    assert len(consents) == 2
    assert all(isinstance(c, Consent) for c in consents)

    assert consents[0].client_id == "sdk"
    assert consents[0].created_date == datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    assert consents[0].last_updated_date == datetime(2025, 1, 16, 14, 20, 0, tzinfo=timezone.utc)
    assert consents[0].granted_scopes == ["openid", "offline_access"]

    assert consents[1].client_id == "webapp"
    assert consents[1].granted_scopes == ["openid"]


def test_list_consents_empty(simai_client, httpx_mock):
    """WHEN listing consents and user has none
    THEN an empty list is returned.
    """
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/users/offline-tokens",
        json=[],
        status_code=200,
    )

    consents = simai_client.me.consents.list()

    assert consents == []


def test_revoke_consent(simai_client, httpx_mock):
    """WHEN revoking a consent
    THEN the API is called with the correct client_id.
    """
    httpx_mock.add_response(
        method="DELETE",
        url="https://test.test/users/offline-tokens/sdk",
        status_code=204,
    )

    simai_client.me.consents.revoke("sdk")

    request = httpx_mock.get_request()
    assert request.method == "DELETE"
    assert str(request.url) == "https://test.test/users/offline-tokens/sdk"


def test_revoke_consent_not_found(simai_client, httpx_mock):
    """WHEN revoking a non-existent consent
    THEN a NotFoundError is raised.
    """
    httpx_mock.add_response(
        method="DELETE",
        url="https://test.test/users/offline-tokens/nonexistent",
        json={"message": "No consent found for client: nonexistent"},
        status_code=404,
    )

    with pytest.raises(NotFoundError):
        simai_client.me.consents.revoke("nonexistent")
