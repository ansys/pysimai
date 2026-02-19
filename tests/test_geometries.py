# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
import urllib.parse
from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.simai.core.data.geometries import Geometry


def test_geometries_list_no_parameter(simai_client, httpx_mock):
    expected_params = urllib.parse.urlencode(
        {
            "filters": {},
            "workspace": simai_client._current_workspace.id,
        }
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/geometries/?{expected_params}",
        json={},
        status_code=200,
    )
    list(simai_client.geometries.list())


def test_geometries_filter(simai_client, httpx_mock):
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
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/geometries/?{expected_params}",
        json={},
        status_code=200,
    )
    list(simai_client.geometries.list(filters={"DIAMETER": 12.5, "SAUCE": "cream"}))


def test_geometries_run_prediction(geometry_factory, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status_code=200,
    )
    geometry = geometry_factory(id="geom-0")
    geometry.run_prediction(Vx=10.5)


def test_geometries_run_prediction_dict_bc(geometry_factory, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status_code=200,
    )
    geometry = geometry_factory(id="geom-0")
    geometry.run_prediction({"Vx": 10.5})


def test_geometries_run_prediction_no_bc(geometry_factory, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geometries/geom-0/predictions",
        json={"id": "pred-0"},
        status_code=200,
    )
    geometry = geometry_factory(id="geom-0")
    geometry.run_prediction()


def test_geometries_upload_point_cloud(geometry_factory, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://test.test/geometries/geom-0/point-cloud",
        json={"point_cloud": {"id": "pc-0"}, "upload_id": "123"},
        status_code=200,
    )
    httpx_mock.add_response(
        method="PUT",
        url="https://test.test/point-clouds/pc-0/part",
        json={"url": "https://s3.test/pc-0/part"},
        status_code=200,
    )
    httpx_mock.add_response(
        method="PUT", url="https://s3.test/pc-0/part", headers={"ETag": "SaladeTomateOignon"}
    )
    httpx_mock.add_response(
        method="POST", url="https://test.test/point-clouds/pc-0/complete", status_code=204
    )

    geometry = geometry_factory(id="geom-0")
    file = BytesIO(b"Hello World")
    geometry.upload_point_cloud((file, "my-point-cloud.vtp"))
    assert geometry.point_cloud == {"id": "pc-0"}


def test_geometries_delete_point_cloud(geometry_factory, httpx_mock):
    httpx_mock.add_response(
        method="DELETE", url="https://test.test/point-clouds/point-cloud-0", status_code=204
    )

    geometry = geometry_factory(id="geom-0", point_cloud={"id": "point-cloud-0"})
    geometry.delete_point_cloud()
    assert geometry.point_cloud is None


def test_geometries_delete_point_cloud_cleares_pp_cache(
    geometry_factory, prediction_factory, post_processing_factory, httpx_mock
):
    httpx_mock.add_response(
        method="DELETE", url="https://test.test/point-clouds/point-cloud-0", status_code=204
    )

    custom_volume_point_cloud = post_processing_factory(
        type="CustomVolumePointCloud", prediction_id="prediction-0"
    )
    prediction = prediction_factory(
        id="prediction-0", post_processings=[custom_volume_point_cloud], geometry_id="geom-0"
    )
    geometry = geometry_factory(
        id="geom-0", predictions=[prediction], point_cloud={"id": "point-cloud-0"}
    )

    assert custom_volume_point_cloud in prediction.post._local_post_processings
    geometry.delete_point_cloud()
    assert custom_volume_point_cloud not in prediction.post._local_post_processings


def test_geometries_rename(simai_client, httpx_mock):
    geometry: Geometry = simai_client._geometry_directory._model_from(
        {"id": "0011", "name": "riri"}
    )

    httpx_mock.add_response(
        method="PATCH",
        url="https://test.test/geometries/0011",
        status_code=204,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geometries/0011",
        json={"id": "0011", "name": "fifi"},
        status_code=200,
    )

    geometry.rename("fifi")
    assert geometry.name == "fifi"


def test_geometries_list_predictions(geometry_factory, prediction_factory, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geometries/geom-0/predictions",
        json=[
            {"id": "pred-0"},
            {"id": "pred-1"},
        ],
        status_code=200,
    )
    geometry = geometry_factory(id="geom-0")
    predictions = geometry.list_predictions()
    assert len(predictions) == 2
    assert predictions[0].id == "pred-0"
    assert predictions[1].id == "pred-1"
