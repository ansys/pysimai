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

import io
import json

import pytest

from ansys.simai.core.errors import InvalidArguments


def test_get_geomai_geometry_by_id(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/geom-123",
        json={"id": "geom-123", "name": "my_geometry.vtp", "state": "successful"},
        status_code=200,
    )
    geometry = simai_client.geomai.geometries.get(id="geom-123")
    assert geometry.id == "geom-123"
    assert geometry.name == "my_geometry.vtp"


def test_get_geomai_geometry_by_name(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/name/my%20geometry.vtp",
        json={"id": "geom-456", "name": "my geometry.vtp", "state": "successful"},
        status_code=200,
    )
    geometry = simai_client.geomai.geometries.get(name="my geometry.vtp")
    assert geometry.id == "geom-456"


def test_get_geomai_geometry_invalid_arguments(simai_client):
    with pytest.raises(InvalidArguments) as e:
        simai_client.geomai.geometries.get()
    assert str(e.value) == "Either 'id' or 'name' argument must be specified."

    with pytest.raises(InvalidArguments) as e:
        simai_client.geomai.geometries.get(id="geom-123", name="my_geometry.vtp")
    assert str(e.value) == "Cannot specify both 'id' and 'name' arguments."


def test_list_geomai_geometries(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/",
        json=[
            {"id": "geom-1", "name": "alpha.vtp", "state": "successful"},
            {"id": "geom-2", "name": "beta.stl", "state": "successful"},
        ],
        status_code=200,
    )
    geometries = simai_client.geomai.geometries.list()
    assert [geometry.id for geometry in geometries] == ["geom-1", "geom-2"]


def test_upload_geomai_geometry(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geomai/geometries/",
        json={
            "geometry": {"id": "geom-123", "name": "my_geometry.vtp", "state": "queued"},
            "upload_id": "upload-1",
        },
        status_code=201,
    )
    httpx_mock.add_response(
        method="PUT",
        url="https://test.test/geomai/geometries/geom-123/part",
        json={"url": "https://s3.test/part-1"},
        status_code=200,
    )
    httpx_mock.add_response(
        method="PUT",
        url="https://s3.test/part-1",
        headers={"ETag": "etag-1"},
        status_code=200,
    )
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geomai/geometries/geom-123/complete",
        status_code=200,
    )

    geometry = simai_client.geomai.geometries.upload((io.BytesIO(b"geometry"), "my_geometry.vtp"))

    assert geometry.id == "geom-123"
    assert geometry.name == "my_geometry.vtp"

    requests = httpx_mock.get_requests()
    assert json.loads(requests[0].content) == {"name": "my_geometry", "file_extension": "vtp"}
    assert json.loads(requests[-1].content) == {
        "upload_id": "upload-1",
        "parts": [{"PartNumber": 1, "ETag": "etag-1"}],
    }


def test_upload_geomai_geometry_unsupported_extension(simai_client):
    with pytest.raises(InvalidArguments) as e:
        simai_client.geomai.geometries.upload((io.BytesIO(b"geometry"), "my_geometry.txt"))
    assert "Unsupported file extension 'txt'" in str(e.value)


def test_rename_geomai_geometry(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/geom-123",
        json={"id": "geom-123", "name": "my_geometry.vtp", "state": "successful"},
        status_code=200,
    )
    geometry = simai_client.geomai.geometries.get(id="geom-123")

    httpx_mock.add_response(
        method="PATCH",
        url="https://test.test/geomai/geometries/geom-123",
        status_code=204,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/geom-123",
        json={"id": "geom-123", "name": "renamed.vtp", "state": "successful"},
        status_code=200,
    )

    geometry.rename("renamed.vtp")
    assert geometry.name == "renamed.vtp"


def test_delete_geomai_geometry(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/geom-123",
        json={"id": "geom-123", "name": "my_geometry.vtp", "state": "successful"},
        status_code=200,
    )
    geometry = simai_client.geomai.geometries.get(id="geom-123")
    assert "geom-123" in simai_client.geomai.geometries._registry

    httpx_mock.add_response(
        method="DELETE",
        url="https://test.test/geomai/geometries/geom-123",
        status_code=202,
    )
    geometry.delete()
    assert "geom-123" not in simai_client.geomai.geometries._registry


def test_geomai_geometry_failure_reason(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/geom-123",
        json={
            "id": "geom-123",
            "name": "my_geometry.vtp",
            "state": "failure",
            "error": "Invalid geometry",
        },
        status_code=200,
    )
    geometry = simai_client.geomai.geometries.get(id="geom-123")
    assert geometry.has_failed is True
    assert geometry.failure_reason == "Invalid geometry"
