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


import pytest

from ansys.simai.core.data.model_configuration import (
    GlobalCoefficientDefinition,
    ModelConfiguration,
    ModelOutput,
    SupportedBuildPresets,
)
from ansys.simai.core.errors import InvalidArguments, ProcessingError

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

SAMPLE_RAW = {
    "extracted_metadata": METADATA_RAW,
    "id": "DarkKnight",
    "is_complete": True,
    "is_deletable": True,
    "is_in_a_project_being_trained": False,
    "is_sample_of_a_project": True,
    "luggage_version": "52.2.2",
}


def test_build_preset_error(simai_client):
    """WHEN build_preset gets a non-supported value
    THEN an InvalidArgument is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
    }

    project = simai_client._project_directory._model_from(raw_project)

    with pytest.raises(InvalidArguments) as excinfo:
        ModelConfiguration(
            project=project,
            build_preset="not_valid_value",
        )

        assert f"{list(SupportedBuildPresets)}" in excinfo.value


def test_model_input_not_none(simai_client):
    """WHEN ModelConfiguration.input gets a None value
    THEN an InvalidArgument is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
    }

    project = simai_client._project_directory._model_from(raw_project)

    bld_conf = ModelConfiguration(
        project=project,
    )

    with pytest.raises(InvalidArguments):
        bld_conf.input = None


def test_model_output_not_none(simai_client):
    """WHEN ModelConfiguration.input gets a None value
    THEN an InvalidArgument is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
    }

    project = simai_client._project_directory._model_from(raw_project)

    bld_conf = ModelConfiguration(
        project=project,
    )

    with pytest.raises(InvalidArguments):
        bld_conf.output = None


def test_model_gc_same_name_as_output_scalar(simai_client):
    """WHEN global coefficient has the same name as a output scalar
    THEN an ProcessingError is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
    }

    project = simai_client._project_directory._model_from(raw_project)

    # with specific exception message
    with pytest.raises(ProcessingError) as e:
        ModelConfiguration(
            project=project,
            global_coefficients=[
                GlobalCoefficientDefinition("max(pressure)", "conflict_name", "cells")
            ],
            output=ModelOutput(scalars=["conflict_name"]),
        )
    assert (
        str(e.value)
        == "Global Coefficient 'conflict_name' has the same name as an output scalar variable."
    )


def test_model_output_scalars_same_name_gc(mocker, simai_client):
    """WHEN ModelConfiguration.output.scalars has the same name as a global coefficient
    THEN an ProcessingError is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
        "sample": SAMPLE_RAW,
    }

    project = simai_client._project_directory._model_from(raw_project)

    mocker.patch.object(project, "process_gc_formula", autospec=True)

    with pytest.raises(ProcessingError) as e:
        config = ModelConfiguration(
            project=project,
            global_coefficients=[
                GlobalCoefficientDefinition("max(pressure)", "conflict_name", "cells")
            ],
        )
        config.output = ModelOutput(scalars=["conflict_name"])
    assert (
        str(e.value)
        == "Scalar variables 'conflict_name' have the same name as global coefficients."
    )
