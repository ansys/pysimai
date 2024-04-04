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

import json
from typing import TYPE_CHECKING

import pytest
import responses

if TYPE_CHECKING:
    from ansys.simai.core.data.training_data import TrainingData


@responses.activate
def test_training_data_list(simai_client):
    responses.add(
        responses.GET,
        "https://test.test/training_data",
        match=[responses.matchers.query_param_matcher({})],
        headers={
            "X-Pagination": json.dumps({"total_pages": 2}),
            "Link": '<http://test.test/training_data?last_id=one>; rel="next"',
        },
        json=[{"id": "one"}],
        status=200,
    )
    responses.add(
        responses.GET,
        "http://test.test/training_data",
        match=[responses.matchers.query_param_matcher({"last_id": "one"})],
        json=[{"id": "two"}],
        status=200,
    )

    td = simai_client.training_data.list()
    assert len(td) == 2
    assert td[0].id == "one"
    assert td[1].id == "two"


@responses.activate
def test_training_data_add_to_project(simai_client, training_data_factory, project_factory):
    td: TrainingData = training_data_factory(id="08080")
    project = project_factory(id="09090")
    responses.add(
        responses.PUT,
        f"https://test.test/training_data/{td.id}/project/{project.id}/association",
        status=204,
    )
    td.add_to_project(project)


@responses.activate
def test_training_data_remove_from_project(simai_client, training_data_factory, project_factory):
    td: TrainingData = training_data_factory(id="08080")
    project = project_factory(id="09090")
    responses.add(
        responses.DELETE,
        f"https://test.test/training_data/{td.id}/project/{project.id}/association",
        status=204,
    )
    td.remove_from_project(project)


@pytest.mark.parametrize(
    "td_factory_args, td_subset",
    [
        ({"id": "777", "name": "ICBM", "subset": "Training"}, "Training"),
        ({"id": "888", "name": "Duke Nukem", "subset": ""}, None),
        ({"id": "999", "name": "Roman"}, None),
    ],
)
@responses.activate
def test_subset_with_project(
    simai_client, training_data_factory, project_factory, td_factory_args, td_subset
):
    project = project_factory(id="e45y", name="coolest_proj")
    td_factory_args["project"] = project
    td: TrainingData = training_data_factory(**td_factory_args)

    simai_client.current_project = project
    assert td.get_subset(project=project) == td_subset


@responses.activate
def test_subset_without_project(training_data_factory):
    td: TrainingData = training_data_factory(
        id="8118",
        name="Suez",
        subset="Test",
    )
    with pytest.raises(Exception) as e:
        td.get_subset(project="fake_proj")
    assert str(e.value) == "Current project is not set."
