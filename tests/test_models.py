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

from typing import TYPE_CHECKING, NamedTuple
from unittest.mock import Mock

import responses

from ansys.simai.core.data.model_configuration import (
    ModelConfiguration,
    ModelInput,
    ModelOutput,
)

if TYPE_CHECKING:
    from ansys.simai.core.data.models import Model
    from ansys.simai.core.data.projects import Project


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

METADATA_RAW = {
    "boundary_conditions": {
        "fields": [
            {
                "format": "value",
                "keys": None,
                "name": "Vx",
                "unit": None,
                "value": -5.569587230682373,
            }
        ]
    },
    "surface": {
        "fields": [
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
                "name": "TurbulentViscosity",
                "unit": None,
            },
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "WallShearStress_0",
                "unit": None,
            },
        ]
    },
    "volume": {
        "fields": [
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
        ]
    },
}

VARS_OUT = {
    "boundary_conditions": ["Vx"],
    "surface": ["Pressure", "TurbulentViscosity"],
    "volume": ["Pressure"],
}

SAMPLE_RAW = {
    "extracted_metadata": METADATA_RAW,
    "id": "DarkKnight",
    "is_complete": True,
    "is_deletable": True,
    "is_in_a_project_being_trained": False,
    "is_sample_of_a_project": True,
    "luggage_version": "52.2.2",
}

create_sse_event = NamedTuple("SSEEvent", [("data", dict)])


@responses.activate
def test_build_with_last_config(simai_client):
    """WHEN I call launch_build() with using the last build configuration
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

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
    }

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}",
        json=raw_project,
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    in_model_conf = ModelConfiguration(project=project, **MODEL_CONF_RAW)

    launched_model: Model = simai_client.models.build(in_model_conf)

    assert isinstance(launched_model.configuration, ModelConfiguration)
    assert launched_model.project_id == MODEL_RAW["project_id"]

    assert launched_model.configuration._to_payload() == MODEL_CONF_RAW


@responses.activate
def test_build_with_new_config(simai_client):
    """WHEN I call launch_build() with using a new build configuration
    THEN I get a Model object, its project_id matches the
    id of the project, and its configuration is a
    ModelConfiguration and its content matches the raw conf.
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
    }

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}",
        json=raw_project,
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    model_input = ModelInput(surface=[], boundary_conditions=["Vx"])
    model_output = ModelOutput(
        surface=["Pressure", "WallShearStress_0"], volume=["Velocity_0", "Pressure"]
    )
    global_coefficients = [("max(Pressure)", "maxpress")]
    simulation_volume = {
        "X": {"length": 300.0, "type": "relative_to_min", "value": 15.0},
        "Y": {"length": 80.0, "type": "absolute", "value": -80},
        "Z": {"length": 40.0, "type": "absolute", "value": -20.0},
    }

    new_conf = ModelConfiguration(
        project=project,
        build_preset="debug",
        continuous=False,
        input=model_input,
        output=model_output,
        global_coefficients=global_coefficients,
        simulation_volume=simulation_volume,
    )

    responses.add(
        responses.POST,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/model",
        json=MODEL_RAW,
        status=200,
    )

    launched_model: Model = simai_client.models.build(new_conf)

    assert isinstance(launched_model.configuration, ModelConfiguration)
    assert launched_model.project_id == MODEL_RAW["project_id"]

    assert launched_model.configuration._to_payload() == new_conf._to_payload()
