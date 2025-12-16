# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.simai.core.data.model_configuration import ModelConfiguration

if TYPE_CHECKING:
    from ansys.simai.core.data.projects import Project
    from ansys.simai.core.data.workspaces import Workspace

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
        "surface_pp_input": [],
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
    "global_coefficients": [
        {"formula": "max(Pressure)", "name": "maxpress", "gc_location": "cells"}
    ],
    "scalars_to_predict": [],
    "simulation_volume": {
        "X": {"length": 300.0, "type": "relative_to_min", "value": 15.0},
        "Y": {"length": 80.0, "type": "absolute", "value": -80},
        "Z": {"length": 40.0, "type": "absolute", "value": -20.0},
    },
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


def test_workspace_download_mer_data(simai_client, httpx_mock):
    """WHEN downloading mer csv file
    THEN the content of the file matches the content of the response.
    """

    workspace: Workspace = simai_client._workspace_directory._model_from(
        {"id": "0011", "name": "riri"}
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/workspaces/{workspace.id}/mer-data",
        content=b"mer-data-geometries",
        status_code=200,
    )

    in_memory = workspace.download_mer_data()
    data_in_file = in_memory.readline()
    assert data_in_file.decode("ascii") == "mer-data-geometries"


def test_workspace_rename(simai_client, httpx_mock):
    workspace: Workspace = simai_client._workspace_directory._model_from(
        {"id": "0011", "name": "riri"}
    )

    httpx_mock.add_response(
        method="PATCH",
        url="https://test.test/workspaces/0011",
        status_code=204,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/workspaces/0011",
        json={"id": "0011", "name": "fifi"},
        status_code=200,
    )

    workspace.rename("fifi")
    assert workspace.name == "fifi"


def test_get_workspace_model_configuration(mocker, simai_client, httpx_mock, training_data_factory):
    workspace: Workspace = simai_client._workspace_directory._model_from(
        {"id": "0011", "name": "riri", "project": "project101"}
    )

    raw_project = {
        "id": "project101",
        "name": "fifi",
        "sample": SAMPLE_RAW,
    }
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/projects/project101",
        json=raw_project,
        status_code=200,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/workspaces/0011/model/configuration",
        json=MODEL_CONF_RAW,
        status_code=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)
    mocker.patch.object(project, "process_gc_formula", autospec=True)
    assert isinstance(workspace.model_configuration, ModelConfiguration)
    assert workspace.model_configuration.project == project
    assert workspace.model_configuration._to_payload() == MODEL_CONF_RAW
