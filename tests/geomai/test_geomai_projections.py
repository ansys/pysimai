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

import pytest

from ansys.simai.core.errors import InvalidArguments, ProcessingError

SUCCESSFUL_PROJECTION = {
    "id": "proj-123",
    "geometry_id": "geom-1",
    "model_id": "model-1",
    "workspace_id": "ws-1",
    "latent_code": [0.1, 0.2, 0.3, 0.4],
    "error": None,
    "state": "successful",
}


def _mock_geometry(httpx_mock, state="successful"):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/geometries/geom-1",
        json={"id": "geom-1", "name": "my_geometry.vtp", "state": state},
        status_code=200,
    )


def test_run_geomai_projection(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geomai/workspaces/ws-1/projections",
        json=SUCCESSFUL_PROJECTION,
        status_code=201,
    )

    projection = simai_client.geomai.projections.run("geom-1", "ws-1")

    assert projection.id == "proj-123"
    assert projection.geometry_id == "geom-1"
    assert projection.workspace_id == "ws-1"
    assert projection.latent_code == [0.1, 0.2, 0.3, 0.4]
    assert json.loads(httpx_mock.get_requests()[0].content) == {"geometry": "geom-1"}


def test_run_geomai_projection_from_geometry(simai_client, httpx_mock):
    _mock_geometry(httpx_mock)
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geomai/workspaces/ws-1/projections",
        json=SUCCESSFUL_PROJECTION,
        status_code=201,
    )

    geometry = simai_client.geomai.geometries.get(id="geom-1")
    projection = geometry.run_projection("ws-1")

    assert projection.id == "proj-123"
    assert json.loads(httpx_mock.get_requests()[-1].content) == {"geometry": "geom-1"}


def test_list_geomai_projections(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/workspaces/ws-1/projections",
        json=[SUCCESSFUL_PROJECTION],
        status_code=200,
    )
    projections = simai_client.geomai.projections.list(workspace="ws-1")
    assert [projection.id for projection in projections] == ["proj-123"]


def test_list_geomai_projections_for_a_geometry(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/workspaces/ws-1/projections?geometry=geom-1",
        json=[SUCCESSFUL_PROJECTION],
        status_code=200,
    )
    projections = simai_client.geomai.projections.list(workspace="ws-1", geometry="geom-1")
    assert [projection.id for projection in projections] == ["proj-123"]


def test_get_geomai_geometry_projection(simai_client, httpx_mock):
    _mock_geometry(httpx_mock)
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/workspaces/ws-1/projections?geometry=geom-1",
        json=[SUCCESSFUL_PROJECTION],
        status_code=200,
    )
    geometry = simai_client.geomai.geometries.get(id="geom-1")
    assert geometry.get_projection("ws-1").id == "proj-123"


def test_get_geomai_geometry_projection_none(simai_client, httpx_mock):
    _mock_geometry(httpx_mock)
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/workspaces/ws-1/projections?geometry=geom-1",
        json=[],
        status_code=200,
    )
    geometry = simai_client.geomai.geometries.get(id="geom-1")
    assert geometry.get_projection("ws-1") is None


def test_get_geomai_projection(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/projections/proj-123",
        json=SUCCESSFUL_PROJECTION,
        status_code=200,
    )
    projection = simai_client.geomai.projections.get("proj-123")
    assert projection.latent_code == [0.1, 0.2, 0.3, 0.4]


def test_geomai_projection_get_latent_code(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/projections/proj-123",
        json=SUCCESSFUL_PROJECTION,
        status_code=200,
    )
    projection = simai_client.geomai.projections.get("proj-123")
    assert projection.get_latent_code() == [0.1, 0.2, 0.3, 0.4]
    assert projection.get_latent_code(n=2) == [0.1, 0.2]
    with pytest.raises(InvalidArguments):
        projection.get_latent_code(n=5)


def test_geomai_projection_failure(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/projections/proj-123",
        json={
            "id": "proj-123",
            "geometry_id": "geom-1",
            "model_id": "model-1",
            "workspace_id": "ws-1",
            "latent_code": None,
            "error": "Geometry is invalid",
            "state": "failure",
        },
        status_code=200,
    )
    projection = simai_client.geomai.projections.get("proj-123")
    assert projection.has_failed is True
    assert projection.failure_reason == "Geometry is invalid"
    with pytest.raises(ProcessingError):
        projection.wait()


def test_delete_geomai_projection(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/projections/proj-123",
        json=SUCCESSFUL_PROJECTION,
        status_code=200,
    )
    projection = simai_client.geomai.projections.get("proj-123")
    assert "proj-123" in simai_client.geomai.projections._registry

    httpx_mock.add_response(
        method="DELETE",
        url="https://test.test/geomai/projections/proj-123",
        status_code=204,
    )
    projection.delete()
    assert "proj-123" not in simai_client.geomai.projections._registry
