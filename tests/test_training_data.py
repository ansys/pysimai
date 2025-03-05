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
from urllib.parse import urlencode

import pytest
import responses

from ansys.simai.core.data.types import SubsetEnum
from ansys.simai.core.errors import InvalidArguments

if TYPE_CHECKING:
    from ansys.simai.core.data.training_data import TrainingData


@responses.activate
def test_training_data_iter(simai_client):
    responses.add(
        responses.GET,
        "https://test.test/training-data",
        match=[responses.matchers.query_param_matcher({})],
        headers={
            "X-Pagination": json.dumps({"total": 999}),
        },
        json=[{"id": "one"}],
        status=200,
    )
    it = simai_client.training_data.iter()
    assert len(it) == 999
    assert next(it).id == "one"
    assert len(it) == 998
    assert next(it, None) is None
    assert len(it) == 998


@responses.activate
def test_training_data_list(simai_client):
    responses.add(
        responses.GET,
        "https://test.test/training-data",
        match=[responses.matchers.query_param_matcher({})],
        headers={
            "X-Pagination": json.dumps({"total_pages": 2}),
            "Link": '<http://test.test/training-data?last_id=one>; rel="next"',
        },
        json=[{"id": "one"}],
        status=200,
    )
    responses.add(
        responses.GET,
        "http://test.test/training-data",
        match=[responses.matchers.query_param_matcher({"last_id": "one"})],
        json=[{"id": "two"}],
        status=200,
    )

    td = simai_client.training_data.list()
    assert len(td) == 2
    assert td[0].id == "one"
    assert td[1].id == "two"


@responses.activate
def test_training_data_list_with_filters(simai_client):
    resps_lst = responses.add(
        responses.GET,
        "https://test.test/training-data",
        match=[
            responses.matchers.query_string_matcher(
                urlencode(
                    [
                        (
                            "filter[]",
                            json.dumps(
                                {"field": "name", "operator": "EQ", "value": "thingo"},
                                separators=(",", ":"),
                            ),
                        ),
                        (
                            "filter[]",
                            json.dumps(
                                {"field": "size", "operator": "LT", "value": 10000},
                                separators=(",", ":"),
                            ),
                        ),
                    ]
                )
            )
        ],
        headers={
            "X-Pagination": json.dumps({"total_pages": 1}),
        },
        json=[{"id": "one"}],
        status=200,
    )

    td = simai_client.training_data.list(filters=[("name", "EQ", "thingo"), ("size", "LT", 10000)])
    assert len(td) == 1
    assert resps_lst.call_count == 1


@responses.activate
def test_training_data_add_to_project(simai_client, training_data_factory, project_factory):
    td: TrainingData = training_data_factory(id="08080")
    project = project_factory(id="09090")
    responses.add(
        responses.PUT,
        f"https://test.test/training-data/{td.id}/project/{project.id}/association",
        status=204,
    )
    td.add_to_project(project)


@responses.activate
def test_training_data_remove_from_project(simai_client, training_data_factory, project_factory):
    td: TrainingData = training_data_factory(id="08080")
    project = project_factory(id="09090")
    responses.add(
        responses.DELETE,
        f"https://test.test/training-data/{td.id}/project/{project.id}/association",
        status=204,
    )
    td.remove_from_project(project)


@pytest.mark.parametrize(
    "td_factory_args",
    [
        ({"id": "777", "name": "ICBM", "subset": SubsetEnum.TRAINING}),
        ({"id": "888", "name": "Duke Nukem", "subset": "Training"}),
        ({"id": "999", "name": "Roman"}),
        ({"id": "81", "name": "Diablo", "subset": None}),
    ],
)
@responses.activate
def test_get_subset(training_data_factory, project_factory, td_factory_args):
    project = project_factory(id="e45y", name="coolest_proj")
    td_subset = td_factory_args.get("subset")
    td_factory_args["project"] = project
    td: TrainingData = training_data_factory(**td_factory_args)

    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}/data/{td.id}/subset",
        status=200,
        json={"subset": td_subset},
    )
    assert td.get_subset(project=project) == td_subset


@responses.activate
def test_get_subset_fails_enum_check(training_data_factory, project_factory):
    project = project_factory(id="bon5ai", name="coolest_proj")
    td: TrainingData = training_data_factory(project=project, id="415")
    td_subset = "Trainidation"
    responses.add(
        responses.GET,
        f"https://test.test/projects/{project.id}/data/{td.id}/subset",
        status=200,
        json={"subset": td_subset},
    )
    with pytest.raises(ValueError) as e:
        td.get_subset(project=project)
    assert str(e.value) == f"'{td_subset}' is not a valid SubsetEnum"


@responses.activate
def test_assign_subset(training_data_factory, project_factory):
    project = project_factory(id="n07e45y", name="bananarama")
    td: TrainingData = training_data_factory(project=project, subset=SubsetEnum.TRAINING)

    responses.add(
        responses.PUT,
        f"https://test.test/projects/{project.id}/data/{td.id}/subset",
        status=200,
        json={"subset": SubsetEnum.TEST},
    )
    td.assign_subset(project=project, subset=SubsetEnum.TEST)
    td.assign_subset(project=project, subset="Test")
    td.assign_subset(project=project, subset=None)
    with pytest.raises(InvalidArguments) as ve:
        td.assign_subset(project=project, subset="Travalignorinestidation")
    assert str(ve.value) == "Must be None or one of: 'Training', 'Test'."
