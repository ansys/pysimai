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

import responses


@responses.activate
def test_post_processing_delete(simai_client, post_processing_factory):
    """WHEN Calling delete() on a post-processing
    THEN the /delete endpoint is called
    ALSO the post-processing is not anymore registered in the Directory
    """
    responses.add(
        responses.DELETE,
        "https://test.test/post-processings/uninteresting-coeffs",
        status=204,
    )

    global_coefficients = post_processing_factory(
        id="uninteresting-coeffs", type="GlobalCoefficients"
    )
    global_coefficients.delete()
    assert "uninteresting-coeffs" not in simai_client._post_processing_directory._registry


@responses.activate
def test_post_processing_global_coefficients_delete(prediction_factory):
    """WHEN deleting a GlobalCoefficients post-processing from a prediction
    THEN there is a call to the DELETE endpoint
    ALSO a new call to pred.post.global_coefficients() re-runs the post-processing
    """
    pred = prediction_factory()
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json={
            "id": "pp-instance-one",
            "state": "successful",
            "type": "GlobalCoefficients",
        },
        status=200,
    )
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/GlobalCoefficients",
        json={
            "id": "pp-instance-two",
            "state": "successful",
            "type": "GlobalCoefficients",
        },
        status=200,
    )
    responses.add(
        responses.DELETE,
        "https://test.test/post-processings/pp-instance-one",
        status=204,
    )

    global_coefficients = pred.post.global_coefficients()
    assert global_coefficients.id == "pp-instance-one"

    global_coefficients.delete()

    global_coefficients = pred.post.global_coefficients()
    assert global_coefficients.id == "pp-instance-two"


@responses.activate
def test_post_processing_surface_evolution_delete(prediction_factory):
    """WHEN deleting a SurfaceEvolution post-processing from a prediction
    THEN there is a call to the DELETE endpoint
    ALSO a new call to pred.post.surface_evolution() re-runs the post-processing
    """
    pred = prediction_factory()
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/SurfaceEvol",
        json={
            "id": "im-the-first-one",
            "state": "successful",
            "type": "SurfaceEvol",
            "location": {"axis": "y", "delta": 9.5},
        },
        status=200,
    )
    responses.add(
        responses.POST,
        f"https://test.test/predictions/{pred.id}/post-processings/SurfaceEvol",
        json={
            "id": "im-the-second-one",
            "state": "successful",
            "type": "SurfaceEvol",
            "location": {"axis": "y", "delta": 9.5},
        },
        status=200,
    )
    responses.add(
        responses.DELETE,
        "https://test.test/post-processings/im-the-first-one",
        status=204,
    )

    surface_evolution = pred.post.surface_evolution(axis="y", delta=9.5)
    assert surface_evolution.id == "im-the-first-one"

    surface_evolution.delete()

    surface_evolution = pred.post.surface_evolution(axis="y", delta=9.5)
    assert surface_evolution.id == "im-the-second-one"
