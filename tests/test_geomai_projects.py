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

import pytest

from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration
from ansys.simai.core.errors import ProcessingError

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.projects import GeomAIProject


def test_project_rename(simai_client, httpx_mock):
    project = simai_client.geomai._project_directory._model_from({"id": "0011", "name": "riri"})

    httpx_mock.add_response(
        method="PATCH",
        url="https://test.test/geomai/projects/0011",
        status_code=204,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/projects/0011",
        json={"id": "0011", "name": "fifi"},
        status_code=200,
    )

    project.name = "fifi"
    assert project.name == "fifi"


def test_project_list_training_data(simai_client, httpx_mock):
    project: GeomAIProject = simai_client.geomai._project_directory._model_from(
        {"id": "0011", "name": "riri"}
    )

    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/projects/0011/training-data",
        headers={
            "Link": '<https://test.test/geomai/projects/0011/training-data?last_id=first>; rel="next"'
        },
        json=[{"id": "first"}],
        status_code=200,
    )

    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/projects/0011/training-data?last_id=first",
        json=[{"id": "second"}],
        status_code=200,
    )

    assert [data.id for data in project.data()] == ["first", "second"]


def test_last_model_configuration(simai_client):
    """Test last_configuration property."""

    last_conf = {"nb_latent_param": 3, "build_preset": "short", "nb_epochs": None}

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
        "last_model_configuration": last_conf,
    }

    project: GeomAIProject = simai_client.geomai._project_directory._model_from(raw_project)

    project_last_conf = project.last_model_configuration

    assert isinstance(project_last_conf, GeomAIModelConfiguration)
    assert project_last_conf.model_dump() == last_conf


def test_cancel_build_for_specified_project_id(simai_client, httpx_mock):
    """WHEN I call projects.cancel_build() for a specified project id
    THEN it returns None if there is an build in progress
    AND raises a ProcessingError otherwise
    """

    project = simai_client.projects._model_from({"id": "e45y123", "name": "proj"})

    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": True},
        status_code=200,
    )

    httpx_mock.add_response(
        method="POST",
        url=f"https://test.test/projects/{project.id}/cancel-training",
        json={"id": "e45y123", "is_being_trained": False},
        status_code=200,
    )

    simai_client.projects.cancel_build(project.id)

    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": False},
        status_code=200,
    )

    with pytest.raises(ProcessingError) as excinfo:
        simai_client.projects.cancel_build(project.id)
        assert "No build pending for this project" in excinfo.value


def test_cancel_active_build_from_project(simai_client, httpx_mock):
    """WHEN I call cancel_build() from a project with an active build
    THEN returns None
    """

    project = simai_client.projects._model_from({"id": "e45y123", "name": "proj"})

    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": True},
        status_code=200,
    )

    httpx_mock.add_response(
        method="POST",
        url=f"https://test.test/projects/{project.id}/cancel-training",
        json={"id": "e45y123"},
        status_code=200,
    )

    project.cancel_build()
    assert len(httpx_mock.get_requests()) == 2


def test_cancel_inactive_build_from_project(simai_client, httpx_mock):
    """WHEN I call cancel_build() from a project with an inactive build
    THEN it raises a ProcessingError
    """

    project = simai_client.projects._model_from({"id": "e45y123", "name": "proj"})

    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/projects/{project.id}",
        json={"id": "e45y123", "is_being_trained": False},
        status_code=200,
    )

    with pytest.raises(ProcessingError) as excinfo:
        project.cancel_build()
        assert "No build pending for this project" in excinfo.value
    assert len(httpx_mock.get_requests()) == 1
