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

from ansys.simai.core.data.post_processings import (
    GlobalCoefficients,
    Slice,
    SurfaceEvolution,
    SurfaceVTP,
    SurfaceVTPTDLocation,
    VolumeVTU,
)
from ansys.simai.core.data.selection_post_processings import ExportablePPList, PPList
from ansys.simai.core.data.selections import Selection
from ansys.simai.core.errors import ApiClientError


@pytest.fixture()
def test_selection(
    geometry_factory,
    prediction_factory,
):
    """A test selection containing 2 geometries and one speed"""
    bc = {"Vx": 10}
    geometries = [
        geometry_factory(
            id="geom1",
            predictions=[prediction_factory(id="pred1", boundary_conditions=bc)],
        ),
        geometry_factory(
            id="geom2",
            predictions=[prediction_factory(id="pred2", boundary_conditions=bc)],
        ),
    ]
    yield Selection(geometries, [bc])


@responses.activate
def test_selection_post_processing_global_coefficients(test_selection):
    """WHEN I call post.post.global_coefficients() on a selection
    THEN the /GlobalCoefficients endpoint is called for each prediction in the selection
    AND I get a list of GlobalCoefficients objects in return
    """
    assert len(test_selection.points) == 2

    for num in [1, 2]:
        responses.add(
            responses.POST,
            f"https://test.test/predictions/pred{num}/post-processings/GlobalCoefficients",
            json={"id": f"gc{num}", "state": "successful"},
            status=200,
        )

    post_processings = test_selection.post.global_coefficients()
    assert isinstance(post_processings, ExportablePPList)
    assert len(post_processings) == 2
    for pp in post_processings:
        assert isinstance(pp, GlobalCoefficients)


@responses.activate
def test_selection_post_processing_surface_evolution(test_selection):
    """WHEN I call post.post.surface_evolution() on a selection
    THEN the /SurfaceEvol endpoint is called for each prediction in the selection
    AND I get a list of SurfaceEvolution objects in return
    """
    assert len(test_selection.points) == 2

    for num in [1, 2]:
        responses.add(
            responses.POST,
            f"https://test.test/predictions/pred{num}/post-processings/SurfaceEvol",
            json={"id": f"se{num}", "state": "successful"},
            status=200,
        )
    post_processings = test_selection.post.surface_evolution(axis="x", delta=0.02)
    assert isinstance(post_processings, ExportablePPList)
    assert len(post_processings) == 2
    for pp in post_processings:
        assert isinstance(pp, SurfaceEvolution)


@responses.activate
def test_selection_post_processing_slice(test_selection):
    """WHEN I call post.post.slice() on a selection
    THEN the /Slice endpoint is called for each prediction in the selection
    AND I get a list of Slice objects in return
    """
    assert len(test_selection.points) == 2

    responses.add(
        responses.POST,
        "https://test.test/predictions/pred1/post-processings/Slice",
        json={"id": "slice01", "status": "queued"},
        status=200,
    )
    responses.add(
        responses.POST,
        "https://test.test/predictions/pred2/post-processings/Slice",
        json={"id": "slice02", "status": "queued"},
        status=200,
    )
    post_processings = test_selection.post.slice(axis="z", coordinate=30)
    assert isinstance(post_processings, PPList)
    assert len(post_processings) == 2
    for pp in post_processings:
        assert isinstance(pp, Slice)


@responses.activate
def test_selection_post_processing_volume_vtu(test_selection):
    """WHEN I call post.post.volume_vtu() on a selection
    THEN the /VolumeVTU endpoint is called for each prediction in the selection
    AND I get a list of PostProcessingVTUExport objects in return
    """
    assert len(test_selection.points) == 2

    responses.add(
        responses.POST,
        "https://test.test/predictions/pred1/post-processings/VolumeVTU",
        json={"id": "vtu01", "status": "queued"},
        status=200,
    )
    responses.add(
        responses.POST,
        "https://test.test/predictions/pred2/post-processings/VolumeVTU",
        json={"id": "vtu02", "status": "queued"},
        status=200,
    )
    post_processings = test_selection.post.volume_vtu()
    assert isinstance(post_processings, PPList)
    assert len(post_processings) == 2
    for pp in post_processings:
        assert isinstance(pp, VolumeVTU)


@responses.activate
def test_selection_post_processing_surface_vtp(test_selection):
    """WHEN I call post.post.surface_vtp() on a selection
    THEN the /SurfaceVTP endpoint is called for each prediction in the selection
    AND I get a list of PostProcessingVTUExport objects in return
    """
    assert len(test_selection.points) == 2

    responses.add(
        responses.POST,
        "https://test.test/predictions/pred1/post-processings/SurfaceVTP",
        json={"id": "vtu01", "status": "queued"},
        status=200,
    )
    responses.add(
        responses.POST,
        "https://test.test/predictions/pred2/post-processings/SurfaceVTP",
        json={"id": "vtu02", "status": "queued"},
        status=200,
    )
    post_processings = test_selection.post.surface_vtp()
    assert isinstance(post_processings, PPList)
    assert len(post_processings) == 2
    for pp in post_processings:
        assert isinstance(pp, SurfaceVTP)


@responses.activate
def test_selection_post_processing_surface_vtp_td_location(test_selection):
    """WHEN I call post.post.surface_vtp() on a selection
    THEN the /SurfaceVTPTDLocation endpoint is called for each prediction in the selection
    AND I get a list of SurfaceVTPTDLocation objects in return
    """
    assert len(test_selection.points) == 2

    responses.add(
        responses.POST,
        "https://test.test/predictions/pred1/post-processings/SurfaceVTPTDLocation",
        json={"id": "vtu01", "status": "queued"},
        status=200,
    )
    responses.add(
        responses.POST,
        "https://test.test/predictions/pred2/post-processings/SurfaceVTPTDLocation",
        json={"id": "vtu02", "status": "queued"},
        status=200,
    )
    post_processings = test_selection.post.surface_vtp_td_location()
    assert isinstance(post_processings, PPList)
    assert len(post_processings) == 2
    for pp in post_processings:
        assert isinstance(pp, SurfaceVTPTDLocation)


@responses.activate
def test_selection_post_processing_error(test_selection):
    """WHEN I call post.post.volume_vtu() on a selection
    AND the first VTU fails
    THEN the second VTU is still executed
    AND a ApiClientError is raised
    AND the working VTU has still been created
    """
    assert len(test_selection.points) == 2

    responses.add(
        responses.POST,
        "https://test.test/predictions/pred1/post-processings/VolumeVTU",
        json={
            "errors": {"json": {"Vx": "This is too fast"}},
            "status": "SppedingUp",
        },
        status=422,
    )
    responses.add(
        responses.POST,
        "https://test.test/predictions/pred2/post-processings/VolumeVTU",
        json={"id": "vtu03", "status": "queued"},
        status=200,
    )
    with pytest.raises(ApiClientError):
        test_selection.post.volume_vtu()

    assert len(responses.calls) == 2
    assert test_selection.predictions[1].post.volume_vtu().id == "vtu03"
