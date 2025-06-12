# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
from functools import partial
from typing import TYPE_CHECKING

import pytest
import responses

from ansys.simai.core.data.models import ModelConfiguration
from ansys.simai.core.data.training_data import TrainingData
from ansys.simai.core.errors import ApiClientError, ProcessingError

if TYPE_CHECKING:
    from ansys.simai.core.data.projects import Project


@responses.activate
def test_project_rename(simai_client):
    project = simai_client._project_directory._model_from({"id": "0011", "name": "riri"})

    responses.add(
        responses.PATCH,
        "https://test.test/projects/0011",
        status=204,
    )
    responses.add(
        responses.GET,
        "https://test.test/projects/0011",
        json={"id": "0011", "name": "fifi"},
        status=200,
    )

    project.name = "fifi"
    assert project.name == "fifi"


@responses.activate
def test_project_list_training_data(simai_client):
    project: Project = simai_client._project_directory._model_from({"id": "0011", "name": "riri"})

    responses.add(
        responses.GET,
        "https://test.test/projects/0011/data",
        match=[responses.matchers.query_param_matcher({})],
        headers={"Link": '<https://test.test/projects/0011/data?last_id=first>; rel="next"'},
        json=[{"id": "first"}],
        status=200,
    )

    responses.add(
        responses.GET,
        "https://test.test/projects/0011/data",
        match=[responses.matchers.query_param_matcher({"last_id": "first"})],
        json=[{"id": "second"}],
        status=200,
    )

    assert [data.id for data in project.data] == ["first", "second"]


@responses.activate
def test_project_sample(simai_client):
    raw_td = {"id": "28-06-1712", "name": "jean-jacques rousseau"}
    raw_project = {"id": "xX007Xx", "name": "fifi", "sample": None}

    project: Project = simai_client._project_directory._model_from(raw_project)

    responses.add(
        responses.PUT,
        f"https://test.test/projects/{project.id}/sample",
        match=[responses.matchers.json_params_matcher({"training_data": raw_td["id"]})],
        status=200,
    )
    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}",
        json=({**raw_project, "sample": raw_td}),
        status=200,
    )
    assert project.sample is None
    project.sample = raw_td["id"]
    assert isinstance(project.sample, TrainingData)
    assert project.sample.id == raw_td["id"]


@responses.activate
@pytest.mark.parametrize(
    "status_code,response_body,error_type",
    [
        (200, {"is_trainable": True}, None),
        (200, {"is_trainable": False, "reason": "a reason why it fails"}, None),
        (400, None, ApiClientError),
    ],
)
def test_is_trainable(simai_client, status_code, response_body, error_type):
    """Test is_trainable method according to is_trainable parameter and the response status code."""
    raw_project = {"id": "xX007Xx", "name": "fifi", "sample": None}

    project: Project = simai_client._project_directory._model_from(raw_project)

    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}/trainable",
        status=status_code,
        json=response_body,
    )

    if status_code == 200:
        pt = project.is_trainable()

        assert bool(pt) is response_body.get("is_trainable")
        assert pt.reason == response_body.get("reason")
    else:
        with pytest.raises(error_type):
            project.is_trainable()


########## Variables for testing get_variables ##########
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
            }
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


@pytest.mark.parametrize(
    "in_sample,vars_out",
    [
        (None, None),
        (SAMPLE_RAW, VARS_OUT),
    ],
)
def test_get_variables(simai_client, in_sample, vars_out):
    """WHEN sample exists
    THEN the output is the names of the available variables"""
    raw_project = {"id": "xX007Xx", "name": "fifi", "sample": in_sample}

    project: Project = simai_client._project_directory._model_from(raw_project)

    var_pool = project.get_variables()
    assert var_pool == vars_out


def test_last_model_configuration(simai_client):
    """Test last_configuration property."""

    last_conf = {
        "boundary_conditions": {"Vx": {}},
        "build_preset": "debug",
        "continuous": False,
        "fields": {
            "surface": [
                {
                    "format": "value",
                    "keys": None,
                    "location": "cell",
                    "name": "TurbulentViscosity",
                    "unit": None,
                }
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
                }
            ],
        },
        "global_coefficients": [],
        "simulation_volume": {
            "X": {"length": 300.0, "type": "relative_to_min", "value": 15.0},
            "Y": {"length": 80.0, "type": "absolute", "value": -80},
            "Z": {"length": 40.0, "type": "absolute", "value": -20.0},
        },
    }

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
        "sample": SAMPLE_RAW,
        "last_model_configuration": last_conf,
    }

    project: Project = simai_client._project_directory._model_from(raw_project)

    project_last_conf = project.last_model_configuration

    assert isinstance(project_last_conf, ModelConfiguration)
    assert project_last_conf._to_payload() == last_conf


def test_process_gc_formula_with_no_sample(simai_client):
    """WHEN no sample is defined in the project
    THEN an exception is raised in process_gc_formula."""
    raw_project = {"id": "xX007Xx", "name": "fifi", "sample": None}
    project: Project = simai_client._project_directory._model_from(raw_project)

    with pytest.raises(ProcessingError):
        project.process_gc_formula("max(Pressure)")


@responses.activate
def test_process_gc_formula_without_cache(simai_client, delayed_events):
    gc_formula = "max(Pressure)"
    compute_result = 0.25478328
    raw_project = {"id": "xX007Xx", "name": "fifi", "sample": SAMPLE_RAW}
    project: Project = simai_client._project_directory._model_from(raw_project)
    responses.add(
        responses.POST,
        f"https://test.test/projects/{project.id}/process-formula",
        status=204,
    )
    check_sse_event = {
        "status": "successful",
        "target": {"id": "xX007Xx", "action": "check", "formula": gc_formula},
    }
    compute_sse_event = {
        "status": "successful",
        "target": {"id": "xX007Xx", "action": "compute", "formula": gc_formula},
        "result": {"value": compute_result},
    }
    sse_callback = simai_client._process_gc_formula_directory._handle_sse_event
    # Schedule events with proper sequencing - check event first, then compute event
    delayed_events.add(partial(sse_callback, data=check_sse_event))
    delayed_events.add(partial(sse_callback, data=compute_sse_event))
    delayed_events.start()

    result = project.process_gc_formula(gc_formula)

    assert result == compute_result


@responses.activate
def test_process_gc_formula_with_cache(simai_client):
    raw_project = {"id": "xX007Xx", "name": "fifi", "sample": SAMPLE_RAW}
    project: Project = simai_client._project_directory._model_from(raw_project)
    responses.add(
        responses.POST,
        f"https://test.test/projects/{project.id}/process-formula",
        status=200,
        json={
            "formula": "max(Pressure)",
            "result": 0.25478328,
        },
    )

    # No need to wait for the SSE event, the cache value is returned by the API
    result = project.process_gc_formula("max(Pressure)")

    assert result == 0.25478328


@responses.activate
def test_cancel_build_for_specified_project_id(simai_client):
    """WHEN I call projects.cancel_build() for a specified project id
    THEN it returns None if there is an build in progress
    AND raises a ProcessingError otherwise
    """

    project = simai_client.projects._model_from({"id": "e45y123", "name": "proj"})

    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": True},
        status=200,
    )

    responses.add(
        responses.POST,
        f"https://test.test/projects/{project.id}/cancel-training",
        json={"id": "e45y123", "is_being_trained": False},
        status=200,
    )

    simai_client.projects.cancel_build(project.id)

    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": False},
        status=200,
    )

    with pytest.raises(ProcessingError) as excinfo:
        simai_client.projects.cancel_build(project.id)
        assert "No build pending for this project" in excinfo.value


@responses.activate
def test_cancel_active_build_from_project(simai_client):
    """WHEN I call cancel_build() from a project with an active build
    THEN returns None
    """

    project = simai_client.projects._model_from({"id": "e45y123", "name": "proj"})

    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": True},
        status=200,
    )

    responses.add(
        responses.POST,
        f"https://test.test/projects/{project.id}/cancel-training",
        json={"id": "e45y123"},
        status=200,
    )

    project.cancel_build()
    assert len(responses.calls) == 2


@responses.activate
def test_cancel_inactive_build_from_project(simai_client):
    """WHEN I call cancel_build() from a project with an inactive build
    THEN it raises a ProcessingError
    """

    project = simai_client.projects._model_from({"id": "e45y123", "name": "proj"})

    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": False},
        status=200,
    )

    with pytest.raises(ProcessingError) as excinfo:
        project.cancel_build()
        assert "No build pending for this project" in excinfo.value
    assert len(responses.calls) == 1
