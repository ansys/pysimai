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

from ansys.simai.core.data.downloads import DownloadableResult
from ansys.simai.core.data.post_processings import GlobalCoefficients
from ansys.simai.core.data.selection_post_processings import ExportablePPList
from ansys.simai.core.data.selections import Selection


@pytest.fixture()
def selection_factory(simai_client) -> Selection:
    """Returns a function to create a :py:class:`Selection`."""

    def _factory(predictions=None, **kwargs) -> Selection:
        selection = Selection(geometries=[], boundary_conditions=[])
        selection.get_predictions = lambda: predictions or []
        return selection

    return _factory


@responses.activate
def test_post_processing_export_global_coefficients(simai_client):
    """WHEN I call export() on a GlobalCoefficients post-processing
    THEN I get a DownloadableResult object allowing me to download the content.
    """

    pp = simai_client._post_processing_directory._model_from(
        {"id": "zebu", "type": "GlobalCoefficients", "state": "successful"}
    )

    def request_callback(request):
        payload = json.loads(request.body)
        # check export format and id are as expected
        assert payload["format"] == "json"
        assert payload["ids"] == ["zebu"]
        return (200, {}, json.dumps({"data": "it's here"}))

    responses.add_callback(
        responses.POST,
        "https://test.test/post-processings/export",
        callback=request_callback,
    )

    res = pp.export()
    assert isinstance(res, DownloadableResult)
    data = res.in_memory().readline()
    assert json.loads(data.decode("ascii")) == {"data": "it's here"}


@responses.activate
def test_post_processing_export_surface_evolution_excel(simai_client):
    """WHEN I call export() on a SurfaceEvolution post-processing
    THEN I get a DownloadableResult object allowing me to download the content.
    """

    pp = simai_client._post_processing_directory._model_from(
        {"id": "mozeu", "type": "SurfaceEvolution", "state": "successful"}
    )

    def request_callback(request):
        payload = json.loads(request.body)
        # check export format and id are as expected
        assert payload["format"] == "xlsx"
        assert payload["ids"] == ["mozeu"]
        return (200, {}, b"some binary excel data")

    responses.add_callback(
        responses.POST,
        "https://test.test/post-processings/export",
        callback=request_callback,
    )

    res = pp.export(format="xlsx")
    assert isinstance(res, DownloadableResult)
    data = res.in_memory().readline()
    assert data == b"some binary excel data"


@responses.activate
def test_post_processing_selection_export(
    selection_factory, prediction_factory, post_processing_factory
):
    """WHEN I call export() on a selection.post.global_coefficients()
    THEN the post-processing/export is called with the ids of expected post-processings
    ALSO I get a DownloadableResult in return
    """
    pp1 = post_processing_factory(type=GlobalCoefficients._api_name())
    pp2 = post_processing_factory(type=GlobalCoefficients._api_name())
    selection = selection_factory(
        predictions=[
            prediction_factory(
                post_processings=[
                    pp1,
                ]
            ),
            prediction_factory(
                post_processings=[
                    pp2,
                ]
            ),
        ]
    )

    def request_callback(request):
        payload = json.loads(request.body)
        # check export format and id are as expected
        assert payload["format"] == "xlsx"
        assert payload["ids"] == [pp1.id, pp2.id]
        return (200, {}, b"some binary excel data")

    responses.add_callback(
        responses.POST,
        "https://test.test/post-processings/export",
        callback=request_callback,
    )
    post_processings = selection.post.global_coefficients()
    assert isinstance(post_processings, ExportablePPList)
    res = post_processings.export(format="xlsx")
    assert isinstance(res, DownloadableResult)
    data = res.in_memory().readline()
    assert data == b"some binary excel data"
