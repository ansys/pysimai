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

from dataclasses import asdict
from typing import TYPE_CHECKING

import responses

from ansys.simai.core.data.models import ModelConfiguration
from ansys.simai.core.data.training_data import TrainingData

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
def test_last_model_configuration(simai_client):
    """Test last_configuration property."""

    last_conf = {
        "boundary_conditions": {"Vx": {}},
        "build_preset": "debug",
        "continuous": False,
        "fields": {},
        "global_coefficients": None,
        "simulation_volume": None,
    }

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
        "sample": None,
        "last_model_configuration": last_conf,
    }

    project: Project = simai_client._project_directory._model_from(raw_project)

    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}/",
        status=200,
        json=raw_project,
    )

    project_last_conf = project.last_model_configuration

    assert isinstance(project_last_conf, ModelConfiguration)
    assert asdict(project_last_conf) == (last_conf | {"project_id": raw_project.get("id")})
