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
import urllib

import responses


@responses.activate
def test_geometries_list_no_parameter(simai_client):
    expected_params = urllib.parse.urlencode(
        {
            "filters": {},
            "workspace": simai_client._current_workspace.id,
        }
    )
    responses.add(
        responses.GET,
        f"https://test.test/geometries/?{expected_params}",
        json={},
        status=200,
    )
    simai_client.geometries.list()


@responses.activate
def test_geometries_filter(simai_client):
    expected_params = urllib.parse.urlencode(
        {
            "filters": json.dumps(
                {
                    "DIAMETER": 12.5,
                    "SAUCE": "cream",
                }
            ),
            "workspace": simai_client._current_workspace.id,
        }
    )
    responses.add(
        responses.GET,
        f"https://test.test/geometries/?{expected_params}",
        json={},
        status=200,
    )
    simai_client.geometries.filter(DIAMETER=12.5, SAUCE="cream")


@responses.activate
def test_geometries_run_prediction(geometry_factory):
    responses.add(
        responses.POST,
        f"https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status=200,
    )
    geometry = geometry_factory(id="geom-0")
    geometry.run_prediction(Vx=10.5)


@responses.activate
def test_geometries_run_prediction_dict_bc(geometry_factory):
    responses.add(
        responses.POST,
        f"https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status=200,
    )
    geometry = geometry_factory(id="geom-0")
    geometry.run_prediction(dict(Vx=10.5))


@responses.activate
def test_geometries_run_prediction_no_bc(geometry_factory):
    responses.add(
        responses.POST,
        f"https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status=200,
    )
    geometry = geometry_factory(id="geom-0")
    geometry.run_prediction()
