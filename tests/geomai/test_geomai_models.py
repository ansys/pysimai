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

from typing import TYPE_CHECKING

from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.models import GeomAIModel
    from ansys.simai.core.data.geomai.projects import GeomAIProject

NB_EPOCHS = 50
NB_LATENT_PARAMS = 10

MODEL_CONF_RAW = {
    "nb_epochs": NB_EPOCHS,
    "nb_latent_param": NB_LATENT_PARAMS,
}

MODEL_RAW = {
    "configuration": MODEL_CONF_RAW,
    "coreml_version": "5.666.333",
    "creation_time": "2035-07-08T16:26:51.943312",
    "error": None,
    "hidden": False,
    "id": "2yg3vpq3",
    "is_deployed": False,
    "name": "pspsps",
    "project_id": "r291h3yk",
    "state": "pending request",
    "updated_time": "2036-12-08T16:26:51.953502",
    "version": None,
}


def test_build(mocker, simai_client, httpx_mock):
    """WHEN I call build() with a working GeomAIModelConfiguration
    THEN I get a GeomAIModel object, its project_id matches the
    id of the project, and its configuration is a
    GeomAIModelConfiguration and its content matches the raw conf.
    """
    httpx_mock.add_response(
        method="POST",
        url=f"https://test.test/geomai/projects/{MODEL_RAW['project_id']}/models",
        json=MODEL_RAW,
        status_code=200,
    )

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
    }

    project: GeomAIProject = simai_client.geomai._project_directory._model_from(raw_project)

    model_config = GeomAIModelConfiguration(**MODEL_CONF_RAW)
    launched_model: GeomAIModel = simai_client.geomai.models.build(project, model_config)

    assert isinstance(launched_model.configuration, GeomAIModelConfiguration)
    assert launched_model.project_id == MODEL_RAW["project_id"]

    assert launched_model.configuration == GeomAIModelConfiguration(**MODEL_CONF_RAW)


def test_build_with_config_as_dict(mocker, simai_client, httpx_mock):
    """WHEN I call build() with a working dict as model configuration
    THEN I get a GeomAIModel object, its project_id matches the
    id of the project, and its configuration is a
    GeomAIModelConfiguration and its content matches the raw conf.
    """
    httpx_mock.add_response(
        method="POST",
        url=f"https://test.test/geomai/projects/{MODEL_RAW['project_id']}/models",
        json=MODEL_RAW,
        status_code=200,
    )

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
    }

    project: GeomAIProject = simai_client.geomai._project_directory._model_from(raw_project)

    launched_model: GeomAIModel = simai_client.geomai.models.build(project, MODEL_CONF_RAW)

    assert isinstance(launched_model.configuration, GeomAIModelConfiguration)
    assert launched_model.project_id == MODEL_RAW["project_id"]

    assert launched_model.configuration == GeomAIModelConfiguration(**MODEL_CONF_RAW)
