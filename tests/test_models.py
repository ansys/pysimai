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

import re
from copy import deepcopy
from typing import TYPE_CHECKING, NamedTuple
from unittest.mock import Mock

import pytest
import responses

from ansys.simai.core.data.model_configuration import (
    DomainAxisDefinition,
    DomainOfAnalysis,
    ModelConfiguration,
    ModelInput,
    ModelOutput,
    PostProcessInput,
)
from ansys.simai.core.errors import ApiClientError, InvalidArguments, ProcessingError

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
    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/trainable",
        json={"is_trainable": True},
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    in_model_conf = ModelConfiguration._from_payload(project=project, **MODEL_CONF_RAW)

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
    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/trainable",
        json={"is_trainable": True},
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
        build_on_top=False,
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


def test_set_doa(simai_client):
    """WHEN the Domain of Analysis is updated
    THEN the simulation_volume is updated accordingly.
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
    }

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    model_conf = ModelConfiguration._from_payload(project=project, **MODEL_CONF_RAW)

    new_height = {"position": "relative_to_center", "value": 0.5, "length": 15.2}

    model_conf.domain_of_analysis.height = DomainAxisDefinition(**new_height)

    assert model_conf._to_payload()["simulation_volume"]["Z"]["type"] == new_height["position"]

    assert model_conf._to_payload()["simulation_volume"]["Z"]["value"] == new_height["value"]
    assert model_conf._to_payload()["simulation_volume"]["Z"]["length"] == new_height["length"]


def test_get_doa(simai_client):
    """WHEN the Domain of Analysis is retrieved
    THEN the parameters of the axes match.
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
    }

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    model_conf = ModelConfiguration._from_payload(project=project, **MODEL_CONF_RAW)

    doa_length_raw = MODEL_CONF_RAW.get("simulation_volume").get("X")

    doa = model_conf.domain_of_analysis

    assert doa.length.length == doa_length_raw.get("length")
    assert doa.length.position == doa_length_raw.get("type")
    assert doa.length.value == doa_length_raw.get("value")


@pytest.mark.parametrize(
    "doa_axis_raw",
    [
        # negative "value" with non-absolute position -> error: "value" can be negative only when "position" is "absolute"
        ({"position": "relative_to_center", "value": -0.5, "length": 15.2}),
        # negative "length" -> error: length cannot be negative
        ({"position": "relative_to_center", "value": 0.5, "length": -15.2}),
    ],
)
def test_wrong_doa_axis_construction(doa_axis_raw):
    """1: WHEN the parameter length of the DomainAxisDefinition is negative
    2: WHEN the parameter value of the DomainAxisDefinition is negative AND the position is not absolute
    THEN an InvalidArguments exception is raised.
    """

    with pytest.raises(InvalidArguments):
        DomainAxisDefinition(**doa_axis_raw)


def test_wrong_doa_axis_length_in_assignment():
    """WHEN a negative number is assigned to the parameter length of DomainAxisDefinition
    THEN an InvalidArguments exception is raised.
    """

    doa_axis = DomainAxisDefinition("relative_to_center", 1.5, 15.2)

    with pytest.raises(InvalidArguments):
        doa_axis.length = -11.2


def test_wrong_doa_axis_value_in_assignment():
    """WHEN a negative number is assigned to the parameter value of DomainAxisDefinition
    THEN an InvalidArguments exception is raised.
    """

    doa_axis = DomainAxisDefinition("relative_to_center", 1.5, 15.2)

    with pytest.raises(InvalidArguments):
        doa_axis.value = -11.2


def test_doa_tuple():
    """WHEN a tuble is introduced to as an argument
    THEN it can be consumed as an DomainAxisDefinition
    (both DomainAxisDefinition and tuples can be consumed
    in the same manner).
    """

    lgth = ("relative_to_max", 5, 8.1)
    wdth = ("relative_to_max", 5, 8.1)
    hght = ("absolute", -4.5, 0.1)

    doa_tuple = DomainOfAnalysis(
        length=lgth,
        width=wdth,
        height=hght,
    )

    doa_long = DomainOfAnalysis(
        length=DomainAxisDefinition(*lgth),
        height=DomainAxisDefinition(*hght),
        width=DomainAxisDefinition(*wdth),
    )

    assert doa_tuple == doa_long


def test_exception_compute_global_coefficient(simai_client):
    """WHEN a project is not defined
    THEN an error is raise."""

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
    }

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    model_conf = ModelConfiguration._from_payload(project=project, **MODEL_CONF_RAW)

    model_conf.project = None

    with pytest.raises(ProcessingError):
        model_conf.compute_global_coefficient()


def test_exception_setting_global_coefficient():
    """WHEN a project is not defined
    THEN an error is raise."""

    with pytest.raises(ProcessingError):
        ModelConfiguration._from_payload(project=None, **MODEL_CONF_RAW)


def test_sse_event_handler(simai_client, model_factory):
    """WHEN SSE signals successful state,
    THEN model becomes ready.
    """
    model = model_factory(state="processing")
    updated_record = model.fields.copy()
    updated_record.update({"state": "successful"})
    simai_client._model_directory._handle_sse_event(
        {
            "type": "job",
            "status": "successful",
            "target": {"id": model.id, "project": "o14qpmvy", "type": "model"},
            "record": {
                "id": model.id,
                "state": "successful",
                "project_id": "o14qpmvy",
                "workspaces": [],
                "name": "test",
                "version": None,
                "manifest": {},
                "configuration": {},
            },
        }
    )
    assert model.is_ready


def test_throw_error_when_volume_is_missing_from_sample(simai_client):
    """WHEN there is no volume in the extracted_metadata of the reference sample
    AND the volume variables are set as model output
    THEN a ProcessingError is thrown.
    """

    sample_raw = deepcopy(SAMPLE_RAW)

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": sample_raw,
    }

    raw_project["sample"]["extracted_metadata"].pop("volume")

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}",
        json=raw_project,
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    model_input = ModelInput(surface=[], boundary_conditions=[])
    model_output = ModelOutput(surface=[], volume=["Velocity_0"])
    global_coefficients = []

    with pytest.raises(ProcessingError):
        _ = ModelConfiguration._from_payload(
            project=project,
            build_preset="debug",
            continuous=False,
            input=model_input,
            output=model_output,
            global_coefficients=global_coefficients,
        )


@responses.activate
def test_post_process_input(simai_client):
    """WHEN ModelConfiguration includes a specified pp_input arg
    THEN ModelConfiguration object and Model.configuration property return that exact pp_input
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "pp_newnew",
        "sample": SAMPLE_RAW,
    }

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}",
        json=raw_project,
        status=200,
    )
    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/trainable",
        json={"is_trainable": True},
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)
    project.verify_gc_formula = Mock()

    pp_input = PostProcessInput(surface=["TurbulentViscosity"])

    model_conf_dict = deepcopy(MODEL_CONF_RAW)
    model_conf_dict["fields"].pop("volume")
    model_conf_dict["fields"]["surface_pp_input"] = [
        {
            "keys": None,
            "name": "TurbulentViscosity",
            "unit": None,
            "format": "value",
            "location": "cell",
        }
    ]
    model_request = deepcopy(MODEL_RAW)
    model_request["configuration"] = model_conf_dict

    config_with_pp_input = ModelConfiguration._from_payload(
        project=project,
        **model_conf_dict,
        pp_input=pp_input,
    )

    responses.add(
        responses.POST,
        f"https://test.test/projects/{model_request['project_id']}/model",
        json=model_request,
        status=200,
    )

    build_model: Model = simai_client.models.build(config_with_pp_input)

    assert config_with_pp_input.pp_input.surface == pp_input.surface
    assert (
        config_with_pp_input._to_payload()["fields"]["surface_pp_input"]
        == model_conf_dict["fields"]["surface_pp_input"]
    )
    assert build_model.configuration.pp_input.surface == pp_input.surface
    assert (
        build_model.fields["configuration"]["fields"]["surface_pp_input"]
        == model_conf_dict["fields"]["surface_pp_input"]
    )


@responses.activate
def test_failed_build_with_resolution(simai_client):
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
    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/trainable",
        json={"is_trainable": True},
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    lgth = ("relative_to_max", 5, 8.1)
    wdth = ("relative_to_max", 5, 8.1)
    hght = ("absolute", -4.5, 0.1)

    doa = DomainOfAnalysis(
        length=lgth,
        width=wdth,
        height=hght,
    )

    new_conf = ModelConfiguration._from_payload(
        project=project,
        build_preset="debug",
        domain_of_analysis=doa,
    )
    response_json = {
        "status": "Conflict",
        "errors": {
            "fields_discrepancies": [
                {
                    "id": "2a324",
                    "name": "td-987",
                    "message": "Missing fields: p (volume), p_rgh (volume)",
                }
            ]
        },
        "resolution": "This is a resolution.",
    }

    responses.add(
        responses.POST,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/model",
        json=response_json,
        status=409,
    )

    with pytest.raises(ApiClientError) as e:
        simai_client.models.build(new_conf)
    assert "This is a resolution." in str(e.value)


@responses.activate
def test_throw_error_when_unknown_variables(simai_client):
    """WHEN input/output/pp_input variables are not found in the reference sample
    THEN a ProcessingError is raised.
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "pp_newnew",
        "sample": SAMPLE_RAW,
    }

    project: Project = simai_client._project_directory._model_from(raw_project)

    mdl_config = ModelConfiguration(project=project)

    unknown_vars = ["abc1", "abc2"]

    with pytest.raises(ProcessingError) as e:
        mdl_config.input = ModelInput(surface=unknown_vars)
    for ukn_var in unknown_vars:
        assert ukn_var in str(e.value)

    with pytest.raises(ProcessingError) as e:
        mdl_config.output = ModelOutput(surface=unknown_vars)
    for ukn_var in unknown_vars:
        assert ukn_var in str(e.value)

    with pytest.raises(ProcessingError) as e:
        mdl_config.output = ModelOutput(volume=unknown_vars)
    for ukn_var in unknown_vars:
        assert ukn_var in str(e.value)


@responses.activate
def test_build_with_build_on_top_not_able(simai_client):
    """WHEN I call launch_build() using last model conf and build on top
    WITH project not being able to use continuous learning
    THEN an InvalidArguments exception is raised
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
        "last_model_configuration": MODEL_CONF_RAW,
        "training_capabilities": {
            "continuous_learning": {"able": False, "reasons": ["Reason 1", "Reason 2"]}
        },
    }

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/trainable",
        json={"is_trainable": True},
        status=200,
    )

    responses.add(
        responses.POST,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/model/on-top",
        json={
            "message": "Continuous learning not available due to: ['Last model is a debug model. Build a production model to enable this feature.']"
        },
        status=400,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    project_last_conf = project.last_model_configuration

    assert isinstance(project_last_conf, ModelConfiguration)
    assert project_last_conf._to_payload() == MODEL_CONF_RAW

    with pytest.raises(
        ApiClientError,
        match=re.escape(
            "400 Continuous learning not available due to: ['Last model is a debug model. Build a production model to enable this feature.']"
        ),
    ):
        project_last_conf.build_on_top = True
        simai_client.models.build(project_last_conf)


@responses.activate
def test_build_with_build_on_top_previous_config(simai_client):
    """WHEN I call launch_build() using the last build configuration and build on top
    THEN I get a Model object, its project_id matches the
    id of the project, and its configuration is a
    ModelConfiguration and its content matches the project last conf.
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
        "last_model_configuration": MODEL_CONF_RAW,
        "training_capabilities": {"continuous_learning": {"able": True, "reasons": []}},
    }

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/trainable",
        json={"is_trainable": True},
        status=200,
    )

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}",
        json=raw_project,
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()
    project_last_conf = project.last_model_configuration
    project_last_conf.build_on_top = True

    model_config_new = deepcopy(MODEL_CONF_RAW)
    model_raw_new = deepcopy(MODEL_RAW)

    model_config_new["continuous"] = True
    model_raw_new["configuration"] = model_config_new

    responses.add(
        responses.POST,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/model/on-top",
        json=model_raw_new,
        status=200,
    )
    launched_model: Model = simai_client.models.build(project_last_conf)

    assert isinstance(launched_model.configuration, ModelConfiguration)
    assert launched_model.project_id == MODEL_RAW["project_id"]
    assert launched_model.configuration._to_payload() == project_last_conf._to_payload()


@responses.activate
def test_build_with_build_on_top_minimal_config(simai_client):
    """WHEN I call launch_build() using the minimal configuration and build on top
    THEN I get a Model object, its project_id matches the
    id of the project, and its configuration is a
    ModelConfiguration and its content matches the project last conf.
    """

    raw_project = {
        "id": MODEL_RAW["project_id"],
        "name": "fifi",
        "sample": SAMPLE_RAW,
        "last_model_configuration": MODEL_CONF_RAW,
        "training_capabilities": {"continuous_learning": {"able": True, "reasons": []}},
    }

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/trainable",
        json={"is_trainable": True},
        status=200,
    )

    responses.add(
        responses.GET,
        f"https://test.test/projects/{MODEL_RAW['project_id']}",
        json=raw_project,
        status=200,
    )

    project: Project = simai_client._project_directory._model_from(raw_project)

    project.verify_gc_formula = Mock()

    build_conf = ModelConfiguration(
        project=project,
        build_on_top=True,
    )

    model_config_new = deepcopy(MODEL_CONF_RAW)
    model_raw_new = deepcopy(MODEL_RAW)

    model_config_new["continuous"] = True
    model_raw_new["configuration"] = model_config_new

    responses.add(
        responses.POST,
        f"https://test.test/projects/{MODEL_RAW['project_id']}/model/on-top",
        json=model_raw_new,
        status=200,
    )
    launched_model: Model = simai_client.models.build(build_conf)

    project_last_conf = project.last_model_configuration
    project_last_conf.build_on_top = True

    assert isinstance(launched_model.configuration, ModelConfiguration)
    assert launched_model.project_id == MODEL_RAW["project_id"]
    assert launched_model.configuration._to_payload() == project_last_conf._to_payload()
