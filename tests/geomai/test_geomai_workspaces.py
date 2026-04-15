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
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.workspaces import GeomAIWorkspace


NB_EPOCHS = 50
NB_LATENT_PARAMS = 10

MODEL_CONF_RAW = {"nb_epochs": NB_EPOCHS, "nb_latent_param": NB_LATENT_PARAMS, "build_preset": None}


def test_geomai_workspace_download_mer(simai_client, httpx_mock):
    """WHEN downloading mer zip file
    THEN the content of the file matches the content of the response.
    """

    workspace: GeomAIWorkspace = simai_client.geomai._workspace_directory._model_from(
        {"id": "abc123", "name": "HL3"}
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/geomai/workspaces/{workspace.id}/model-evaluation-report",
        text="mer-geomai",
        status_code=200,
    )

    in_memory = workspace.download_model_evaluation_report()
    data_in_file = in_memory.readline()
    assert data_in_file.decode("ascii") == "mer-geomai"


def test_geomai_workspace_rename(simai_client, httpx_mock):
    workspace: GeomAIWorkspace = simai_client.geomai._workspace_directory._model_from(
        {"id": "0011", "name": "riri"}
    )

    httpx_mock.add_response(
        method="PATCH",
        url="https://test.test/geomai/workspaces/0011",
        status_code=204,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/workspaces/0011",
        json={"id": "0011", "name": "fifi"},
        status_code=200,
    )

    workspace.rename("fifi")
    assert workspace.name == "fifi"


def test_geomai_workspace_get_latent_parameters(simai_client, httpx_mock):
    workspace: GeomAIWorkspace = simai_client.geomai._workspace_directory._model_from(
        {"id": "abc123", "name": "HL3"}
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/geomai/workspaces/{workspace.id}/model/latent-parameters-json",
        text='{"geometry1": [1,2,3]}',
        status_code=200,
    )

    latent_parameters = workspace.get_latent_parameters()
    assert isinstance(latent_parameters, dict)
    assert latent_parameters == {"geometry1": [1, 2, 3]}


def test_get_workspace_model_configuration(mocker, simai_client, httpx_mock, training_data_factory):
    workspace: GeomAIWorkspace = simai_client.geomai._workspace_directory._model_from(
        {"id": "0011", "name": "riri"}
    )

    httpx_mock.add_response(
        method="GET",
        url="https://test.test/workspaces/0011/model/configuration",
        json=MODEL_CONF_RAW,
        status_code=200,
    )

    assert workspace.model_configuration.model_dump() == MODEL_CONF_RAW
    assert isinstance(workspace.model_configuration, GeomAIModelConfiguration)


def test_geomai_workspace_list_predictions(simai_client, httpx_mock):
    workspace: GeomAIWorkspace = simai_client.geomai._workspace_directory._model_from(
        {"id": "abc123", "name": "HL3"}
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/geomai/workspaces/{workspace.id}/predictions",
        json=[
            {"id": "pred1", "name": "Prediction 1"},
            {"id": "pred2", "name": "Prediction 2"},
        ],
        status_code=200,
    )

    predictions = workspace.list_predictions()
    assert len(predictions) == 2
    assert predictions[0].id == "pred1"
    assert predictions[1].id == "pred2"


def test_geomai_workspace_iter(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/workspaces/?",
        headers={"X-Pagination": json.dumps({"total": 999})},
        json=[{"id": "one", "name": "Workspace One"}],
        status_code=200,
    )

    workspace_iter = simai_client.geomai.workspaces.iter()

    assert len(workspace_iter) == 999
    assert next(workspace_iter).id == "one"
    assert len(workspace_iter) == 998
    assert next(workspace_iter, None) is None
    assert len(workspace_iter) == 998


def test_geomai_workspace_list(simai_client, httpx_mock):
    httpx_mock.add_response(
        is_reusable=True,
        method="GET",
        url="https://test.test/geomai/workspaces/?",
        headers={"Link": '<https://test.test/geomai/workspaces/?last_id=one>; rel="next"'},
        json=[{"id": "one", "name": "Workspace One"}],
        status_code=200,
    )
    httpx_mock.add_response(
        is_reusable=True,
        method="GET",
        url="https://test.test/geomai/workspaces/?last_id=one",
        json=[{"id": "two", "name": "Workspace Two"}],
        status_code=200,
    )

    workspaces = simai_client.geomai.workspaces.list()

    assert len(workspaces) == 2
    assert [workspace.id for workspace in workspaces] == ["one", "two"]


def test_geomai_workspace_list_created_by_me(simai_client, httpx_mock):
    user_uuid = "user-456"
    simai_client._api._session.auth._user_uuid = user_uuid

    raw_workspaces = [
        {"id": "ws-1", "name": "alpha"},
        {"id": "ws-2", "name": "beta"},
    ]

    raw_filters = [{"field": "created_by", "operator": "EQ", "value": user_uuid}]
    query = urlencode([("filter[]", json.dumps(f, separators=(",", ":"))) for f in raw_filters])
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/geomai/workspaces/?{query}",
        json=raw_workspaces,
        status_code=200,
    )

    workspaces = simai_client.geomai.workspaces.list(created_by_me=True)
    assert [workspace.id for workspace in workspaces] == ["ws-1", "ws-2"]
