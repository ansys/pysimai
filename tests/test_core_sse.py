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
from threading import Event
from typing import NamedTuple
from unittest.mock import Mock

import pytest
import responses

from ansys.simai.core.api.client import ApiClient
from ansys.simai.core.data.post_processings import GlobalCoefficients, VolumeVTU
from ansys.simai.core.errors import ConnectionError, ProcessingError
from ansys.simai.core.utils.configuration import ClientConfig


def test_api_client_connects_to_sse_if_flag():
    """WHEN ApiClient is created
    THEN it connects to the SSE URL if and only if the no_sse_connection is not False
    """
    did_connect_to_sse_url = Event()

    def sse_connection(request):
        did_connect_to_sse_url.set()
        return (200, {}, "{}")

    with responses.RequestsMock() as rsps:
        rsps.add_callback(
            responses.GET,
            "https://test.test/sessions/events",
            content_type="application/json",
            callback=sse_connection,
        )
        for sse_disabled in [True, False]:
            should_connect = not sse_disabled
            ApiClient(
                ClientConfig(
                    organization="toto",
                    url="https://test.test",
                    _disable_authentication=True,
                    # We need this flag as unit tests will otherwise be stuck
                    # waiting for a second event (if we set the flag after start).
                    # Also __del__ cannot be trusted to be called.
                    _stop_sse_threads=True,
                    no_sse_connection=sse_disabled,
                )
            )
            # wait 1 sec max if a connection has been made
            did_connect = did_connect_to_sse_url.wait(1)
            assert did_connect == should_connect


@responses.activate
def test_api_client_sse_endpoint_unreachable():
    """WHEN ApiClient is created, if SSE endpoint is not reachable
    THEN a ConnectionError is raised
    """
    responses.add(
        responses.GET,
        "https://test.test/sessions/events",
        body="Not found",
        status=404,
    )
    with pytest.raises(ConnectionError):
        ApiClient(
            ClientConfig(
                organization="toto",
                url="https://test.test",
                _disable_authentication=True,
            )
        )


@responses.activate
def test_wait_non_blocking_for_non_loading_items(simai_client):
    """WHEN Creating Mesh, prediction, post-processing objects that are finished
    THEN wait can be called and are not blocking
    """
    responses.add(
        responses.POST,
        "https://test.test/geometries/7412/predictions",
        json={"id": "2222", "state": "successful"},
        status=200,
    )

    responses.add(
        responses.POST,
        "https://test.test/predictions/2222/post-processings/GlobalCoefficients",
        json={"id": "3333", "state": "successful"},
        status=200,
    )
    geometry = simai_client.geometries._model_from(
        {"id": "7412", "state": "successful", "predictions": []}
    )
    pred = geometry.run_prediction(Vx=10)
    assert pred.id == "2222"
    global_coefficients = pred.post.global_coefficients()
    assert global_coefficients.id == "3333"
    assert not geometry.is_pending
    assert not pred.is_pending
    assert not global_coefficients.is_pending
    assert geometry.wait() is True
    assert pred.wait() is True
    assert global_coefficients.wait() is True


create_sse_event = NamedTuple("SSEEvent", [("data", dict)])


def test_sse_event_prediction_success(sse_mixin, prediction_factory):
    """WHEN SSEMixin receives an SSE message updating a prediction to success
    THEN the appropriate prediction is updated and changes state to successful
    """
    pred = prediction_factory(state="processing")
    assert pred.is_pending
    # Mock an SSE success event
    updated_record = pred.fields.copy()
    updated_record.update({"state": "successful", "confidence_score": "high"})
    sse_mixin._handle_sse_event(
        create_sse_event(
            f'{{"target": {{"id": "{pred.id}", "type": "prediction"}}, "status": "successful", "type": "job", "record": {json.dumps(updated_record)}}}'
        )
    )
    assert not pred.is_pending
    assert pred.is_ready
    assert pred.confidence_score == "high"


@pytest.mark.parametrize(
    "start_status, status, record",
    [
        ("processing", "successful", {"confidence_score": "yolo"}),
        ("successful", "processing", {}),
    ],
)
def test_prediction_fields_updated_on_sse_event(
    sse_mixin, prediction_factory, start_status, status, record
):
    prediction = prediction_factory(state=start_status)
    updated_record = prediction.fields.copy()
    updated_record.update(record)
    sse_event = {
        "target": {"id": prediction.id, "type": "prediction"},
        "status": status,
        "type": "job",
    }
    if record:
        sse_event["record"] = updated_record

    sse_mixin._handle_sse_event(create_sse_event(json.dumps(sse_event)))

    assert prediction.fields.get("confidence_score") == record.get("confidence_score")


def test_sse_event_update_prediction_failure(sse_mixin, prediction_factory):
    """WHEN SSEMixin receives a SSE message updating a prediction as failed
    THEN the appropriate prediction object is set to failed and failure_reason field is as expected
    """
    pred = prediction_factory(state="processing")
    assert pred.is_pending
    # Mock a SSE failure event
    updated_record = pred.fields.copy()
    updated_record.update({"state": "failure", "error": "something went wrong"})
    sse_mixin._handle_sse_event(
        create_sse_event(
            f'{{"target": {{"id": "{pred.id}", "type": "prediction"}}, "status": "failure", "type": "job", "record": {json.dumps(updated_record)}}}'
        )
    )
    assert not pred.is_pending
    assert pred.has_failed
    assert pred.failure_reason == "something went wrong"
    with pytest.raises(ProcessingError):
        pred.wait()


@responses.activate
def test_wait_timeout_false(simai_client):
    """WHEN wait timed out
    THEN the return value reflects that to the user (is False)
    """
    responses.add(
        responses.POST,
        "https://test.test/geometries/7412/predictions",
        json={"id": "2222", "state": "pending"},
        status=200,
    )
    geometry = simai_client.geometries._model_from(
        {"id": "7412", "state": "successful", "predictions": []}
    )
    pred = geometry.run_prediction(Vx=10)
    assert pred.id == "2222"
    assert pred.wait(0.001) is False


def test_global_wait(simai_client):
    """WHEN simai_client's wait() method is called,
    THEN the wait() method is called once for each registered object.
    """
    pred1 = simai_client._prediction_directory._model_from(
        {"id": "m7541d9", "is_complete": False, "state": "processing"}
    )
    pred2 = simai_client._prediction_directory._model_from(
        {"id": "u87e14", "is_complete": True, "state": "successful"}
    )
    pred3 = simai_client._prediction_directory._model_from(
        {"id": "c963f778", "is_complete": True, "state": "failure"}
    )
    pp1 = simai_client._post_processing_directory._model_from(
        pp_class=GlobalCoefficients,
        data={"id": "ch4687x", "is_complete": False, "state": "processing"},
        prediction=pred2,
    )
    pp2 = simai_client._post_processing_directory._model_from(
        pp_class=VolumeVTU,
        data={"id": "pmx37354", "is_complete": True, "state": "successful"},
        prediction=pred2,
    )

    all_models = [pred1, pred2, pred3, pp1, pp2]
    for model in all_models:
        model.wait = Mock()
    simai_client.wait()
    for model in all_models:
        model.wait.assert_called_once()


def test_prediction_data_update(simai_client, prediction_factory):
    """WHEN simai_client's wait() method is called,
    THEN the wait() method is called once for each registered object.
    """
    pred = prediction_factory(state="processing")
    updated_record = pred.fields.copy()
    updated_record.update({"state": "successful", "confidence_score": "low"})
    simai_client._prediction_directory._handle_sse_event(
        {
            "reason": "",
            "status": "successful",
            "result": {"data": {"values": {"confidence_score": "low"}}, "dim": 1},
            "target": {"id": pred.id, "type": "prediction"},
            "type": "job",
            "record": updated_record,
        }
    )
    assert pred.is_ready
    assert pred.confidence_score == "low"
