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

import pytest
import responses

from ansys.simai.core.data.geometries import Geometry


def test_prediction_failure(simai_client):
    """WHEN creating a Prediction in an error state and with an "error" field
    THEN prediction.has_failed is true and failure_reason describes the error
    """
    prediction = simai_client._prediction_directory._model_from(
        {"id": "pizza-4789", "state": "rejected", "error": "The pizza was lukewarm"}
    )
    assert prediction.has_failed
    assert prediction.failure_reason == "The pizza was lukewarm"

    prediction = simai_client._prediction_directory._model_from(
        {"id": "drink-4673", "state": "failure", "error": "Drink was spilled over"}
    )
    assert prediction.has_failed
    assert prediction.failure_reason == "Drink was spilled over"


@responses.activate
def test_prediction_delete(simai_client):
    """WHEN deleting a Prediction
    THEN a DELETE query on predictions/id endpoint is called
    ALSO the prediction doesn't exist anymore in its Directory's registry
    """
    pred_id = "uninteresting-prediction-001"
    prediction = simai_client._prediction_directory._model_from(
        {"id": pred_id, "state": "successful"}
    )

    assert simai_client._prediction_directory._registry[pred_id] == prediction

    responses.add(
        responses.DELETE,
        f"https://test.test/predictions/{pred_id}",
        status=204,
    )
    prediction.delete()

    assert pred_id not in simai_client._prediction_directory._registry


@responses.activate
def test_prediction_wait_deleted(simai_client):
    """WHEN deleting a Prediction that is not done
    THEN prediction.wait() immediately returns
    """
    pred_id = "uninteresting-prediction-002"
    prediction = simai_client._prediction_directory._model_from({"id": pred_id, "state": "pending"})

    responses.add(
        responses.DELETE,
        f"https://test.test/predictions/{pred_id}",
        status=204,
    )
    prediction.delete()
    prediction.wait()


@responses.activate
def test_prediction_geometry_attribute(prediction_factory):
    """WHEN accessing a Prediction's geometry attribute
    THEN the geometry object is returned
    """
    prediction = prediction_factory(geometry_id="mexico")
    responses.add(
        responses.GET,
        "https://test.test/geometries/mexico",
        json={"id": "mexico", "state": "successful"},
        status=200,
    )

    assert isinstance(prediction.geometry, Geometry)
    assert prediction.geometry.id == "mexico"


@responses.activate
def test_prediction_call_geometry_attribute_twice(prediction_factory):
    """WHEN accessing twice the geometry attribute of a Prediction
    THEN the endpoint is called only once
    """
    prediction = prediction_factory(geometry_id="cuba")
    responses.add(
        responses.GET,
        "https://test.test/geometries/cuba",
        json={"id": "cuba", "state": "successful"},
        status=200,
    )

    prediction.geometry  # noqa: B018
    prediction.geometry  # noqa: B018

    assert len(responses.calls) == 1


@responses.activate
def test_prediction_call_geometry_attribute_already_registered(
    geometry_factory, prediction_factory
):
    """WHEN accessing the geometry attribute of a prediction when the geometry exists locally
    THEN no query is ran
    """
    geometry_factory(id="registered_geometry")  # Registering geometry
    prediction = prediction_factory(geometry_id="registered_geometry")
    responses.add(
        responses.GET,
        "https://test.test/geometries/registered_geometry",
        json={"id": "registered_geometry", "state": "successful"},
        status=200,
    )

    prediction.geometry  # noqa: B018
    assert len(responses.calls) == 0


@responses.activate
def test_run(simai_client, geometry_factory):
    responses.add(
        responses.GET,
        "https://test.test/geometries/geom-0",
        json={"id": "geom-0"},
        status=200,
    )
    responses.add(
        responses.POST,
        "https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status=200,
    )
    geometry = geometry_factory(id="geom-0")
    simai_client.predictions.run(geometry.id, Vx=10.5)


@responses.activate
def test_run_dict_bc(simai_client, geometry_factory):
    responses.add(
        responses.GET,
        "https://test.test/geometries/geom-0",
        json={"id": "geom-0"},
        status=200,
    )
    responses.add(
        responses.POST,
        "https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status=200,
    )
    geometry = geometry_factory(id="geom-0")
    simai_client.predictions.run(geometry.id, {"Vx": 10.5})


@responses.activate
def test_run_no_bc(simai_client, geometry_factory):
    responses.add(
        responses.GET,
        "https://test.test/geometries/geom-0",
        json={"id": "geom-0"},
        status=200,
    )
    responses.add(
        responses.POST,
        "https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status=200,
    )
    geometry = geometry_factory(id="geom-0")
    simai_client.predictions.run(geometry.id)


@responses.activate
def test_confidence_score(prediction_factory):
    """WHEN accessing a Prediction's confidence score properties
    THEN the corresponding values are returned
    """
    prediction = prediction_factory(confidence_score="high", raw_confidence_score=0.94107)
    empty_prediction = prediction_factory()
    bad_prediction = prediction_factory(confidence_score="abysmal")

    assert prediction.confidence_score == "high"
    assert prediction.raw_confidence_score == 0.94107
    assert empty_prediction.confidence_score is None
    assert empty_prediction.raw_confidence_score is None
    with pytest.raises(ValueError) as exc:
        assert bad_prediction.confidence_score
    assert str(exc.value) == "Must be None or one of: 'high', 'low', None."
