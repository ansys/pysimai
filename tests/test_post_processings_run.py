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
import math

import pytest
import responses

from ansys.simai.core.data.post_processings import (
    GlobalCoefficients,
    Slice,
    SurfaceEvolution,
    VolumeVTU,
)
from ansys.simai.core.errors import ApiClientError


@responses.activate
def test_post_processing_async_status(prediction_factory):
    """WHEN Running a post-processing on a prediction
    THEN a PostProcessing object is returned, in status loading and not failed
    """
    pred = prediction_factory()
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json={"id": "0123456", "state": "queued"},
        status=200,
    )

    global_coefficients = pred.post.global_coefficients()
    assert isinstance(global_coefficients, GlobalCoefficients)
    assert global_coefficients.id == "0123456"
    assert not global_coefficients.has_failed
    assert global_coefficients.failure_reason is None
    assert global_coefficients.is_pending


@responses.activate
def test_post_processing_global_coefficients(prediction_factory):
    """WHEN Running a GlobalCoefficients post-processing on a prediction
    THEN a POST request is made on the post-processings/GlobalCoefficients endpoint
    ALSO subsequent calls do not generate calls to the endpoint
    """

    pred = prediction_factory()
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json={"id": "7777"},
        status=200,
    )

    global_coefficients = pred.post.global_coefficients()
    assert isinstance(global_coefficients, GlobalCoefficients)
    assert global_coefficients.id == "7777"

    pred.post.global_coefficients()
    assert len(responses.calls) == 1


@responses.activate
def test_post_processing_vtu(prediction_factory):
    """WHEN Running a VTU  post-processing on a prediction
    THEN a POST request is made on the post-processings/VolumeVTU endpoint
    ALSO subsequent calls do not generate calls to the endpoint
    """
    pred = prediction_factory()
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/VolumeVTU",
        json={"id": "6666"},
        status=200,
    )

    volume_vtu = pred.post.volume_vtu()
    assert isinstance(volume_vtu, VolumeVTU)
    assert volume_vtu.id == "6666"

    pred.post.volume_vtu()
    assert len(responses.calls) == 1


@responses.activate
def test_post_processing_surface_evolution(prediction_factory):
    """WHEN Running a SurfaceEvolution post-processing on a prediction
    THEN a POST request is made on the post-processings/SurfaceEvol endpoint
    AND on subsequent access, the endpoint is not called
    """

    pred = prediction_factory()

    def request_callback(request):
        payload = json.loads(request.body)
        if payload["axis"] == "x" and payload["delta"] == 5:
            return (200, {}, json.dumps({"id": "7894"}))
        if payload["axis"] == "y" and payload["delta"] == 9.5:
            return (200, {}, json.dumps({"id": "1111"}))
        return (400, {}, "This request is not expected in this test")

    responses.add_callback(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/SurfaceEvol",
        callback=request_callback,
    )

    surface_evolution = pred.post.surface_evolution(axis="x", delta=5)
    assert isinstance(surface_evolution, SurfaceEvolution)
    assert surface_evolution.id == "7894"

    surface_evolution = pred.post.surface_evolution(axis="y", delta=9.5)
    assert isinstance(surface_evolution, SurfaceEvolution)
    assert surface_evolution.id == "1111"

    # call the post-processings with same parameters again
    surface_evolution = pred.post.surface_evolution(axis="x", delta=5)
    assert surface_evolution.id == "7894"

    surface_evolution = pred.post.surface_evolution(axis="y", delta=9.5)
    assert surface_evolution.id == "1111"

    # Check the URL has been called exactly twice, only once by parameter set
    assert len(responses.calls) == 2


@responses.activate
def test_post_processing_surface_evolution_parameters_values(prediction_factory):
    """WHEN Running a SurfaceEvolution post-processing with good parameters,
    THEN a POST request is made on the post-processings/SurfaceEvol endpoint
    AND a PostProcessing object is returned
    """
    pred = prediction_factory()
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/SurfaceEvol",
        json={"id": "4444"},
        status=200,
    )

    surface_evolution = pred.post.surface_evolution(axis="x", delta=5)
    assert isinstance(surface_evolution, SurfaceEvolution)
    surface_evolution = pred.post.surface_evolution(axis="y", delta=5)
    assert isinstance(surface_evolution, SurfaceEvolution)
    surface_evolution = pred.post.surface_evolution(axis="z", delta=5)
    assert isinstance(surface_evolution, SurfaceEvolution)
    surface_evolution = pred.post.surface_evolution(axis="x", delta=1)
    assert isinstance(surface_evolution, SurfaceEvolution)
    surface_evolution = pred.post.surface_evolution(axis="x", delta=100)
    assert isinstance(surface_evolution, SurfaceEvolution)
    surface_evolution = pred.post.surface_evolution(axis="x", delta=0.0001)
    assert isinstance(surface_evolution, SurfaceEvolution)


@responses.activate
def test_post_processing_surface_evolution_with_wrong_parameters(prediction_factory):
    """WHEN Running a SurfaceEvolution PP with missing or wrong parameters,
    THEN a TypeError exception is raised
    """
    pred = prediction_factory()
    with pytest.raises(TypeError):
        pred.post.surface_evolution()
    with pytest.raises(TypeError):
        pred.post.surface_evolution(axis="x")
    with pytest.raises(TypeError):
        pred.post.surface_evolution(delta=5)
    with pytest.raises(TypeError):
        pred.post.surface_evolution(axis="y", delta=-10)
    with pytest.raises(TypeError):
        pred.post.surface_evolution(axis="y", delta="10")
    with pytest.raises(TypeError):
        pred.post.surface_evolution(axis="b", delta=10)
    with pytest.raises(TypeError):
        pred.post.surface_evolution(plane=[1, 2, 3, 4])


@responses.activate
def test_post_processing_slice(prediction_factory):
    """WHEN Running a Slice post-processing on a prediction
    THEN a POST request is made on the post-processings/Slice endpoint
    AND on subsequent access, the endpoint is not called
    """
    pred = prediction_factory()

    def request_callback(request):
        payload = json.loads(request.body)
        plane = payload["plane"]
        if plane == [1, 0, 0, 30.5]:
            return (200, {}, json.dumps({"id": "976544"}))
        if plane == [0, 1, 0, 4]:
            return (200, {}, json.dumps({"id": "114455"}))
        return (400, {}, json.dumps({"error": "unexpected plane"}))

    responses.add_callback(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/Slice",
        callback=request_callback,
    )

    slice = pred.post.slice(axis="x", coordinate=30.5)
    assert isinstance(slice, Slice)
    assert slice.id == "976544"

    slice = pred.post.slice(axis="y", coordinate=4)
    assert isinstance(slice, Slice)
    assert slice.id == "114455"

    # Check the URL has been called exactly twice, only once by parameter set
    assert len(responses.calls) == 2


@responses.activate
def test_post_processing_slice_parameters_values(prediction_factory):
    """WHEN Running a Slice post-processing with good parameters,
    THEN a POST request is made on the post-processings/Slice endpoint
    AND a PostProcessing object is returned
    """
    pred = prediction_factory()

    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/Slice",
        json={"id": "7654198"},
        status=200,
    )
    slice = pred.post.slice(axis="x", coordinate=4)
    assert isinstance(slice, Slice)
    slice = pred.post.slice(axis="z", coordinate=math.pi)
    assert isinstance(slice, Slice)


@responses.activate
def test_post_processing_slice_with_wrong_parameters(prediction_factory):
    """WHEN Running a Slice PP with missing or wrong parameters,
    THEN a ValueError or TypeError exception is raised
    """
    pred = prediction_factory()
    with pytest.raises(ValueError):
        pred.post.slice(axis="a", coordinate=20.4)
    with pytest.raises(TypeError):
        pred.post.slice(axis="x")
    with pytest.raises(TypeError):
        pred.post.slice(coordinate=20.4)


@responses.activate
def test_post_processing_request_failure_raises_exception(prediction_factory):
    """WHEN Running a post-processing
    IF back-end replies with an error status code
    THEN a ApiClientError is raised
    """
    pred = prediction_factory()

    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/SurfaceEvol",
        json={"error": "Something went wrong"},
        status=400,
    )
    with pytest.raises(ApiClientError):
        pred.post.surface_evolution(axis="x", delta=45)


@responses.activate
def test_post_processing_reload(simai_client):
    """WHEN Reloading a post-processing
    THEN a query is made to the post processing endpoint
    """
    pp_json = {"id": "88x88x", "type": "GlobalCoefficients"}
    pp = simai_client._post_processing_directory._model_from(data=pp_json)

    responses.add(
        responses.GET,
        "https://test.test/post-processings/88x88x",
        json=pp_json,
        status=200,
    )
    pp.reload()


@responses.activate
def test_post_processing_get(simai_client):
    """WHEN Calling get() on post-processing directory
    THEN a post-processing object of corresponding type is returned
    """
    responses.add(
        responses.GET,
        "https://test.test/post-processings/0001",
        json={"id": "0001", "type": "GlobalCoefficients"},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://test.test/post-processings/0002",
        json={"id": "0002", "type": "SurfaceEvolution"},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://test.test/post-processings/0003",
        json={"id": "0003", "type": "Slice"},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://test.test/post-processings/0004",
        json={"id": "0004", "type": "VolumeVTU"},
        status=200,
    )
    assert isinstance(
        simai_client._post_processing_directory.get("0001"),
        GlobalCoefficients,
    )
    assert isinstance(
        simai_client._post_processing_directory.get("0002"),
        SurfaceEvolution,
    )
    assert isinstance(simai_client._post_processing_directory.get("0003"), Slice)
    assert isinstance(simai_client._post_processing_directory.get("0004"), VolumeVTU)


@responses.activate
def test_post_processing_get_unknown_type(simai_client):
    """WHEN Calling get() on post-processing directory
    IF an unknown type is received from the server
    THEN a ValueError is raised
    """
    responses.add(
        responses.GET,
        "https://test.test/post-processings/000x",
        json={"id": "000x", "type": "ThisFormatDoesNotExist"},
        status=200,
    )

    with pytest.raises(ValueError):
        simai_client._post_processing_directory.get("000x")
