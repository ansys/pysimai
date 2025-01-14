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

import pytest
import responses

import ansys.simai.core
from ansys.simai.core.data import post_processings
from ansys.simai.core.data.predictions import Prediction
from ansys.simai.core.errors import InvalidArguments


@responses.activate
def test_post_processing_prediction_attribute(post_processing_factory):
    """WHEN accessing the prediction attribute of a PostProcessing
    THEN the prediction is returned
    """
    post_processing = post_processing_factory(type="GlobalCoefficients", prediction_id="java")
    responses.add(
        responses.GET,
        "https://test.test/predictions/java",
        json={"id": "java", "state": "processing"},
        status=200,
    )

    assert isinstance(post_processing.prediction, Prediction)
    assert post_processing.prediction.id == "java"


@responses.activate
def test_post_processing_call_prediction_attribute_twice(post_processing_factory):
    """WHEN accessing the prediction attribute of a PostProcessing twice
    THEN the endpoint is called only once
    """
    post_processing = post_processing_factory(type="GlobalCoefficients", prediction_id="sumatra")
    responses.add(
        responses.GET,
        "https://test.test/predictions/sumatra",
        json={"id": "sumatra", "state": "successful"},
        status=200,
    )

    post_processing.prediction  # noqa: B018
    post_processing.prediction  # noqa: B018

    assert len(responses.calls) == 1


@responses.activate
def test_post_processing_call_prediction_attribute_already_registered(
    prediction_factory, post_processing_factory
):
    """WHEN accessing the prediction attribute of a PostProcessing when the geometry exists locally
    THEN no query is ran
    """
    prediction_factory(id="registered_prediction")
    post_processing = post_processing_factory(
        type="GlobalCoefficients", prediction_id="registered_prediction"
    )
    responses.add(
        responses.GET,
        "https://test.test/predictions/registered_prediction",
        json={"id": "registered_prediction", "state": "successful"},
        status=200,
    )

    post_processing.prediction  # noqa: B018

    assert len(responses.calls) == 0


@responses.activate
def test_post_processing_ran_from_prediction_already_has_a_prediction(
    prediction_factory, post_processing_factory
):
    """WHEN Running a post-treatment on a prediction
    THEN the prediction attribute is available without calling the /predictions/id endpoint
    """
    pred = prediction_factory(post_processings=[post_processing_factory(type="GlobalCoefficients")])
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json={"id": "7777"},
        status=200,
    )
    global_coefficients = pred.post.global_coefficients()

    assert global_coefficients.prediction == pred
    assert len(responses.calls) == 0


@responses.activate
def test_post_processing_dont_run_exists_locally(prediction_factory, post_processing_factory):
    """WHEN Running a post-processing with run=False and it already exists locally
    THEN The local post-processing is returned and the API not called
    """
    pred = prediction_factory(post_processings=[post_processing_factory(type="GlobalCoefficients")])

    assert pred.post.global_coefficients(run=False) is not None

    assert len(responses.calls) == 0


@responses.activate
def test_post_processing_dont_run_does_not_exist_locally_no_params(prediction_factory):
    """WHEN Running a parameter-less post-processing with run=False and it does not exist locally
    THEN The local post-processing is returned and the API get endpoint is called
    """
    pred = prediction_factory()
    responses.add(
        responses.GET,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json=[{"id": "0001", "type": "GlobalCoefficients"}],
        status=200,
    )

    pp = pred.post.global_coefficients(run=False)
    assert pp.id == "0001"


@responses.activate
def test_post_processing_dont_run_does_not_exist_locally_with_params(
    prediction_factory,
):
    """WHEN Running a post-processing with parameters and run=False and it does not exist locally
    THEN The local post-processing is returned and the API get endpoint is called
    """
    pred = prediction_factory()
    responses.add(
        responses.GET,
        f"https://test.test/predictions/{pred.id}/post-processings/SurfaceEvol",
        match=[
            responses.matchers.query_param_matcher(
                {"filters": json.dumps({"axis": "x", "delta": 0.5})}
            )
        ],
        json=[
            {
                "id": "0002",
                "type": "SurfaceEvol",
                "location": {"axis": "x", "delta": 0.5},
            }
        ],
        status=200,
    )

    pp = pred.post.surface_evolution(axis="x", delta=0.5, run=False)
    assert pp.id == "0002"


@responses.activate
def test_post_processing_dont_run_does_not_exist_locally_or_remotely(
    prediction_factory,
):
    """WHEN Running a post-processing with run=False and it does not exist locally or on the server
    THEN None is returned and the API get endpoint is called
    """
    pred = prediction_factory()
    responses.add(
        responses.GET,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json=[],
        status=200,
    )

    assert pred.post.global_coefficients(run=False) is None


@responses.activate
def test_post_processing_run_from_directory(simai_client, prediction_factory):
    """WHEN I run a post-processing from the directory
    THEN The created post-processing is returned
    """
    pred = prediction_factory()
    responses.add(
        responses.GET,
        f"https://test.test/predictions/{pred.id}",
        json={"id": pred.id},
        status=200,
    )
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json={"id": "7777"},
        status=200,
    )

    pp = simai_client.post_processings.run(ansys.simai.core.GlobalCoefficients, pred.id)
    pp_bis = simai_client.post_processings.run("GlobalCoefficients", pred.id)
    assert pp.id == "7777"
    assert pp_bis.id == "7777"


@responses.activate
def test_post_processing_list(simai_client):
    """WHEN simai.post_processings.list is called
    THEN it returns a list of all post-processings for the workspace
    """
    responses.add(
        responses.GET,
        "https://test.test/post-processings/",
        match=[
            responses.matchers.query_param_matcher({"workspace": simai_client.current_workspace.id})
        ],
        headers={"X-Pagination": json.dumps({"total_pages": 3})},
        json=[{"type": "GlobalCoefficients", "id": "1"}],
    )
    responses.add(
        responses.GET,
        "https://test.test/post-processings/",
        match=[
            responses.matchers.query_param_matcher(
                {"workspace": simai_client.current_workspace.id, "page": "2"}
            )
        ],
        headers={"X-Pagination": json.dumps({"total_pages": 3})},
        json=[{"type": "SurfaceVTP", "id": "2"}],
    )
    responses.add(
        responses.GET,
        "https://test.test/post-processings/",
        match=[
            responses.matchers.query_param_matcher(
                {"workspace": simai_client.current_workspace.id, "page": "3"}
            )
        ],
        headers={"X-Pagination": json.dumps({"total_pages": 3})},
        json=[{"type": "VolumeVTU", "id": "3"}],
    )

    pps = simai_client.post_processings.list()
    assert len(pps) == 3
    assert [pp.id for pp in pps] == ["1", "2", "3"]


@responses.activate
def test_post_processing_list_prediction_and_workspace_forbidden(simai_client):
    """WHEN simai.post_processings.list is called with a prediction and a workspace
    THEN InvalidArguments error is raised
    """
    with pytest.raises(InvalidArguments):
        simai_client.post_processings.list(workspace="toto", prediction="tata")


@responses.activate
def test_post_processing_list_in_prediction(simai_client, mocker):
    api_mock = mocker.Mock(return_value=[])
    simai_client._api.get_post_processings_for_prediction = api_mock
    pp = simai_client.post_processings.list(prediction="CrouAnthem")
    assert pp == []
    api_mock.assert_called_with("CrouAnthem", None)


@responses.activate
def test_post_processing_list_in_workspace(simai_client, mocker):
    api_mock = mocker.Mock(return_value=[])
    simai_client._api.get_post_processings_in_workspace = api_mock
    pp = simai_client.post_processings.list(
        workspace="BODEGA", post_processing_type=post_processings.Slice
    )
    assert pp == []
    api_mock.assert_called_with("BODEGA", post_processings.Slice._api_name())


@responses.activate
def test_prediction_post_list(simai_client, mocker, prediction_factory):
    pred = prediction_factory()
    api_mock = mocker.Mock(return_value=[])
    simai_client._api.get_post_processings_for_prediction = api_mock
    pp = pred.post.list(post_processings.SurfaceVTP)
    assert pp == []
    api_mock.assert_called_with(pred.id, post_processings.SurfaceVTP._api_name())
