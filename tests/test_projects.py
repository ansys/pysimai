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

from typing import TYPE_CHECKING

import pytest
import responses

from ansys.simai.core.data.training_data import TrainingData
from ansys.simai.core.errors import ApiClientError

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
