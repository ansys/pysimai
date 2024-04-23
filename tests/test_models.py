# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

from dataclasses import asdict
from typing import TYPE_CHECKING

import pytest
import responses

from ansys.simai.core.data.models import (
    ModelConfiguration,
)
from ansys.simai.core.errors import InvalidArguments

if TYPE_CHECKING:
    from ansys.simai.core.data.models import Model


MODEL_CONF_RAW = {
    "boundary_conditions": {"Vx": {}},
    "build_preset": "debug",
    "continuous": False,
    "fields": {
        "surface": [
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "Pressure",
                "unit": None,
            },
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "WallShearStress_0",
                "unit": None,
            },
        ],
        "surface_input": [],
        "volume": [
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "Pressure",
                "unit": None,
            },
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "Velocity_0",
                "unit": None,
            },
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "Velocity_1",
                "unit": None,
            },
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "VolumeFractionWater",
                "unit": None,
            },
        ],
    },
    "global_coefficients": [{"formula": "max(Pressure)", "name": "maxpress"}],
    "simulation_volume": {
        "X": {"length": 300.0, "type": "relative_to_min", "value": 15.0},
        "Y": {"length": 80.0, "type": "absolute", "value": -80},
        "Z": {"length": 40.0, "type": "absolute", "value": -20.0},
    },
}

MODEL_RAW = {
    "configuration": MODEL_CONF_RAW,
    "coreml_version": "5.666.333",
    "creation_time": "2035-07-08T16:26:51.943312",
    "error": None,
    "has_custom_training_configuration": False,
    "hidden": False,
    "id": "2yg3vpq9",
    "is_deployed": False,
    "manifest": {},
    "name": "pspsps",
    "project_id": "r291h3yk",
    "state": "pending request",
    "training_configuration": None,
    "updated_time": "2036-12-08T16:26:51.953502",
    "version": None,
    "workspaces": [],
}


@responses.activate
def test_build(simai_client):
    """WHEN I call launch_build() with a ModelConfiguration
    THEN I get a Model object, its project_id matches the
    id of the project, and its configuration is a
    ModelConfiguration and its content matches the raw conf.
    """

    responses.add(
        responses.POST,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/model",
        json=MODEL_RAW,
        status=200,
    )

    in_model_conf = ModelConfiguration(project_id=MODEL_RAW["project_id"], **MODEL_CONF_RAW)

    launched_model: Model = simai_client.models.build(in_model_conf)

    assert isinstance(launched_model.configuration, ModelConfiguration)
    assert launched_model.project_id == MODEL_RAW["project_id"]

    model_conf = asdict(launched_model.configuration)
    model_conf.pop("project_id")

    assert model_conf == MODEL_CONF_RAW


def test_set_doa(simai_client):
    """WHEN the Domain of Analysis is updated
    THEN the simulation_volume is updated accordingly
    """

    model_conf = ModelConfiguration(project_id=MODEL_RAW["project_id"], **MODEL_CONF_RAW)

    doa = model_conf.domain_of_analysis

    new_height = {"position": "relative_to_center", "value": 0.5, "length": 15.2}

    doa.height = simai_client.models.doa_axis_definition(**new_height)

    model_conf.domain_of_analysis = doa

    assert model_conf.simulation_volume.get("Z").get("type") == new_height.get("position")
    assert model_conf.simulation_volume.get("Z").get("value") == new_height.get("value")
    assert model_conf.simulation_volume.get("Z").get("length") == new_height.get("length")


def test_get_doa():
    """WHEN the Domain of Analysis is retrieved
    THEN the params of the axes match
    """

    model_conf = ModelConfiguration(project_id=MODEL_RAW["project_id"], **MODEL_CONF_RAW)

    doa_length_raw = MODEL_CONF_RAW.get("simulation_volume").get("X")

    doa = model_conf.domain_of_analysis

    assert doa.length.length == doa_length_raw.get("length")
    assert doa.length.position == doa_length_raw.get("type")
    assert doa.length.value == doa_length_raw.get("value")


def test_wrong_doa_axis_values(simai_client):
    """WHEN the value of the DomainAxisDefinition is negative
    AND the position is not absolute
    THEN an InvalidArguments exception is raised.
    """

    doa_axis_raw = {"position": "relative_to_center", "value": -0.5, "length": 15.2}

    with pytest.raises(InvalidArguments):
        simai_client.models.doa_axis_definition(**doa_axis_raw)
