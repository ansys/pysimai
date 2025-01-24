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
from io import BytesIO

import responses

from ansys.simai.core.data.post_processings import (
    CustomVolumePointCloud,
    DownloadableResult,
    GlobalCoefficients,
    Slice,
    SurfaceEvolution,
    SurfaceVTP,
    SurfaceVTPTDLocation,
    VolumeVTU,
)


@responses.activate
def test_post_processing_result_global_coefficients(simai_client):
    """WHEN Running a GlobalCoefficients post-processing on a prediction and calling its .data field,
    THEN a GET request is made on the post-processings/<id> endpoint
    ALSO the .data attribute is a dictionary containing the GlobalCoefficients data
    ALSO multiple accesses to .data don't call the endpoint multiple times
    """
    # Mock request for PP creation
    responses.add(
        responses.POST,
        "https://test.test/predictions/7546/post-processings/GlobalCoefficients",
        json={"id": "7167", "state": "successful"},
        status=200,
    )
    # Mock request for PP data
    responses.add(
        responses.GET,
        "https://test.test/post-processings/7167",
        json={
            "data": {
                "values": {
                    "IsoStaticPressureForce": {
                        "data": {
                            "X": 4.441544089820862,
                            "Y": 0.32894839148911376,
                            "Z": 14.442021446988662,
                        },
                        "type": "base",
                        "unit": {"N": 1},
                    },
                    "WallShearStress": {
                        "data": {
                            "X": -0.6887743615741067,
                            "Y": 0.08958696618025093,
                            "Z": 0.0741612935822976,
                        },
                        "type": "base",
                        "unit": {"N": 1},
                    },
                }
            },
            "id": "ak2gr7pw",
            "location": {},
            "prediction": "bw6z91zj",
            "type": "GlobalCoefficients",
        },
        status=200,
    )

    pred = simai_client._prediction_directory._model_from({"id": "7546", "state": "successful"})
    global_coefficients = pred.post.global_coefficients()

    assert isinstance(global_coefficients, GlobalCoefficients)
    assert isinstance(global_coefficients.data, dict)
    assert len(global_coefficients.data) == 2
    assert global_coefficients.data["IsoStaticPressureForce"]["data"]["X"] == 4.441544089820862
    assert global_coefficients.data["IsoStaticPressureForce"]["type"] == "base"

    # check despite 2 access to global_coefficients.data, only 1 call to API endpoint
    assert responses.assert_call_count("https://test.test/post-processings/7167", 1)


@responses.activate
def test_post_processing_result_surface_evolution(simai_client):
    """WHEN Running a SurfaceEvolution post-processing on a prediction and calling its .data field,
    THEN a GET request is made on the post-processings/<id> endpoint
    ALSO the .data attribute is a dictionary containing the expected data
    ALSO multiple accesses to .data don't call the endpoint multiple times
    """
    # Mock request for PP creation
    responses.add(
        responses.POST,
        "https://test.test/predictions/r26g04j8/post-processings/SurfaceEvol",
        json={"id": "4c7r4c", "state": "successful"},
        status=200,
    )
    # Mock request for PP data
    responses.add(
        responses.GET,
        "https://test.test/post-processings/4c7r4c",
        json={
            "data": {"resources": {"json": "https://s3.test/some/path/to/json"}},
            "id": "xn49z2z5",
            "location": {"axis": "x", "delta": 5},
            "prediction": "r26g04j8",
            "type": "SurfaceEvol",
        },
        status=200,
    )
    responses.add(
        responses.GET,
        "https://s3.test/some/path/to/json",
        body=json.dumps(
            {
                "area": {
                    "data": [
                        247.03766026765066,
                        307.41345249496834,
                        266.0681832190391,
                        62.77419701451614,
                    ],
                    "type": "base",
                    "unit": {"m": 2},
                },
                "position": {
                    "data": [
                        -75.07807159423828,
                        -52.07807159423828,
                        -29.07807159423828,
                        -6.078071594238281,
                    ],
                    "type": "base",
                    "unit": {"m": 1},
                },
                "WallShearStress": {
                    "data": {
                        "X": [
                            107167.4091582841,
                            131679.1151319072,
                            112707.19948165954,
                            25602.98322615308,
                        ],
                        "Y": [
                            -5719.545388303992,
                            -5059.645424596727,
                            -3057.985328271491,
                            -479.55662520016926,
                        ],
                        "Z": [
                            -2765.7740285333916,
                            -3634.3034712755143,
                            -2185.0554359153575,
                            -537.9401310387967,
                        ],
                    },
                    "type": "base",
                    "unit": {"N": 1, "m": -2},
                },
            }
        ),
    )

    pred = simai_client._prediction_directory._model_from({"id": "r26g04j8", "state": "successful"})
    surface_evolution = pred.post.surface_evolution(axis="x", delta=5)

    assert isinstance(surface_evolution, SurfaceEvolution)
    assert isinstance(surface_evolution.data, DownloadableResult)
    surface_evolution_dict = surface_evolution.as_dict()
    assert len(surface_evolution_dict) == 3
    assert surface_evolution_dict["WallShearStress"]["data"]["X"][0] == 107167.4091582841

    # we have used surface_evolution.data twice, generating 2 hits to the endpoint
    assert responses.assert_call_count("https://test.test/post-processings/4c7r4c", 2)


@responses.activate
def test_post_processing_result_slice(simai_client):
    """WHEN Running a Slice post-processing on a prediction and calling its .data field,
    THEN a GET request is made on the post-processings/<id> endpoint
    ALSO the .data attribute is a DownloadableResult object,
        that we can call a .binary_io method on,
        which will send the expected content
    """
    location = {"plane": [0, 1, 0, 20], "output_format": "png"}
    # Mock request for PP creation
    responses.add(
        responses.POST,
        "https://test.test/predictions/7546/post-processings/Slice",
        json={"id": "98413534", "state": "successful", "location": location},
        status=200,
    )
    # Mock request for PP data
    responses.add(
        responses.GET,
        "https://test.test/post-processings/98413534",
        json={
            "data": {"resources": {"png": "https://s3.test.test/slice.png?key=9988776655"}},
            "id": "98413534",
            "location": location,
            "prediction": "7546",
            "type": "Slice",
        },
        status=200,
    )
    # Mock request for slice binary download
    responses.add(
        responses.GET,
        "https://s3.test.test/slice.png?key=9988776655",
        body="this-is-slice-binary-data",
        content_type="application/octet-stream",
        status=200,
    )

    pred = simai_client._prediction_directory._model_from({"id": "7546", "state": "successful"})
    slice = pred.post.slice(axis="y", coordinate="20")

    assert isinstance(slice, Slice)
    assert isinstance(slice.data, DownloadableResult)
    # Test a binary download
    binary_io = slice.data.in_memory()
    assert isinstance(binary_io, BytesIO)
    data_line = binary_io.readline()
    assert data_line.decode("ascii") == "this-is-slice-binary-data"

    # we have used slice.data twice, generating 2 hits to the endpoint
    assert responses.assert_call_count("https://test.test/post-processings/98413534", 2)


@responses.activate
def test_post_processing_result_volume_vtu(simai_client):
    """WHEN Running a VolumeVTU post-processing on a prediction and calling its .data field,
    THEN a GET request is made on the post-processings/<id> endpoint
    ALSO the .data attribute is a DownloadableResult object
        we can call a .binary_io method on
    """
    # Mock request for PP creation
    responses.add(
        responses.POST,
        "https://test.test/predictions/7546/post-processings/VolumeVTU",
        json={"id": "01010101654", "state": "successful"},
        status=200,
    )
    # Mock request for PP data
    responses.add(
        responses.GET,
        "https://test.test/post-processings/01010101654",
        json={
            "data": {"resources": {"vtk": "https://s3.test.test/slice.npz?key=445461321"}},
            "id": "01010101654",
            "location": {},
            "prediction": "7546",
            "type": "VolumeVTU",
        },
        status=200,
    )
    # Mock request for npz binary download
    responses.add(
        responses.GET,
        "https://s3.test.test/slice.npz?key=445461321",
        body="this-is-vtu-binary-data",
        content_type="application/octet-stream",
        status=200,
    )

    pred = simai_client._prediction_directory._model_from({"id": "7546", "state": "successful"})
    volume_vtu = pred.post.volume_vtu()
    assert isinstance(volume_vtu, VolumeVTU)
    assert isinstance(volume_vtu.data, DownloadableResult)
    # Test a binary download
    binary_io = volume_vtu.data.in_memory()
    assert isinstance(binary_io, BytesIO)
    data_line = binary_io.readline()
    assert data_line.decode("ascii") == "this-is-vtu-binary-data"

    # we have used vtu.data twice, generating 2 hits to the endpoint
    assert responses.assert_call_count("https://test.test/post-processings/01010101654", 2)


@responses.activate
def test_post_processing_result_surface_vtp(simai_client):
    """WHEN Running a SurfaceVTP post-processing on a prediction and calling its .data field,
    THEN a GET request is made on the post-processings/<id> endpoint
    ALSO the .data attribute is a DownloadableResult object
        we can call a .binary_io method on
    """
    # Mock request for PP creation
    responses.add(
        responses.POST,
        "https://test.test/predictions/7546/post-processings/SurfaceVTP",
        json={"id": "01010101654", "state": "successful"},
        status=200,
    )
    # Mock request for PP data
    responses.add(
        responses.GET,
        "https://test.test/post-processings/01010101654",
        json={
            "data": {"resources": {"vtk": "https://s3.test.test/slice.npz?key=445461321"}},
            "id": "01010101654",
            "location": {},
            "prediction": "7546",
            "type": "SurfaceVTP",
        },
        status=200,
    )
    # Mock request for npz binary download
    responses.add(
        responses.GET,
        "https://s3.test.test/slice.npz?key=445461321",
        body="this-is-vtp-binary-data",
        content_type="application/octet-stream",
        status=200,
    )

    pred = simai_client._prediction_directory._model_from({"id": "7546", "state": "successful"})
    surface_vtp = pred.post.surface_vtp()
    assert isinstance(surface_vtp, SurfaceVTP)
    assert isinstance(surface_vtp.data, DownloadableResult)
    # Test a binary download
    binary_io = surface_vtp.data.in_memory()
    assert isinstance(binary_io, BytesIO)
    data_line = binary_io.readline()
    assert data_line.decode("ascii") == "this-is-vtp-binary-data"

    # we have used vtp.data twice, generating 2 hits to the endpoint
    assert responses.assert_call_count("https://test.test/post-processings/01010101654", 2)


@responses.activate
def test_post_processing_result_surface_vtp_td_location(simai_client):
    """WHEN Running a surface_vtp post-processing on a prediction
    WITH predict-as-learnt option (location is PPSurfaceLocation.AS_LEARNT)
    AND calling its .data field,
    THEN a GET request is made on the post-processings/SurfaceVTPTDLocation endpoint
    AND the returned instance is of type SurfaceVTPTDLocation.
    """
    # Mock request for PP creation
    responses.add(
        responses.POST,
        "https://test.test/predictions/7546/post-processings/SurfaceVTPTDLocation",
        json={"id": "01010101654", "state": "successful"},
        status=200,
    )

    pred = simai_client._prediction_directory._model_from({"id": "7546", "state": "successful"})
    surface_vtp = pred.post.surface_vtp_td_location()
    assert responses.assert_call_count(
        "https://test.test/predictions/7546/post-processings/SurfaceVTPTDLocation", 1
    )
    assert isinstance(surface_vtp, SurfaceVTPTDLocation)


@responses.activate
def test_post_processing_result_point_cloud(simai_client):
    responses.add(
        responses.POST,
        "https://test.test/predictions/7546/post-processings/CustomVolumePointCloud",
        json={"id": "01010101654", "state": "successful"},
        status=200,
    )
    # Mock request for PP data
    responses.add(
        responses.GET,
        "https://test.test/post-processings/01010101654",
        json={
            "data": {"resources": {"vtp": "https://s3.test.test/point_cloud.vtp?key=445461321"}},
            "id": "01010101654",
            "location": {},
            "prediction": "7546",
            "type": "CustomVolumePointCloud",
        },
        status=200,
    )
    # Mock request for binary download
    responses.add(
        responses.GET,
        "https://s3.test.test/point_cloud.vtp?key=445461321",
        body="this-is-vtp-binary-data",
        content_type="application/octet-stream",
        status=200,
    )
    responses.add(
        responses.GET,
        "https://test.test/geometries/4321",
        json={"id": "4321", "point_cloud": {"id": "2345"}},
    )

    pred = simai_client._prediction_directory._model_from(
        {"id": "7546", "state": "successful", "geometry_id": "4321"}
    )
    point_cloud = pred.post.custom_volume_point_cloud()
    assert isinstance(point_cloud, CustomVolumePointCloud)
    assert isinstance(point_cloud.data, DownloadableResult)
    # Test a binary download
    binary_io = point_cloud.data.in_memory()
    assert isinstance(binary_io, BytesIO)
    data_line = binary_io.readline()
    assert data_line.decode("ascii") == "this-is-vtp-binary-data"

    # we have used vtp.data twice, generating 2 hits to the endpoint
    assert responses.assert_call_count("https://test.test/post-processings/01010101654", 2)
