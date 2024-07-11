# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

from typing import Any, Dict, List

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.data.types import APIResponse


class PointCloudClientMixin(ApiClientMixin):
    def create_point_cloud(self, geometry_id: str, name: str, extension: str) -> APIResponse:
        """Create a point cloud without pushing the data.

        Args:
            geometry_id: ID of the geometry to assign the point cloud to.
            name: Name to give to the geometry.
            extension: Extension to give to the file.
        """
        post_data = {"name": name, "file_extension": extension}
        return self._post(f"geometries/{geometry_id}/point-cloud", json=post_data)

    def complete_point_cloud_upload(
        self, point_cloud_id: str, upload_id: str, parts: List[Dict[str, Any]]
    ):
        """Complete the upload of a point cloud.

        Args:
           point_cloud_id: ID of the point cloud to complete
           upload_id: ID used to upload the point cloud
           parts: List of the uploaded file parts
        """
        self._post(
            f"point-clouds/{point_cloud_id}/complete",
            json={"upload_id": upload_id, "parts": parts},
            return_json=False,
        )

    def delete_point_cloud(self, point_cloud_id: str):
        """Delete the specific point cloud file.

        Args:
            point_cloud_id: ID of the input cloud to delete
        """
        self._delete(f"point-clouds/{point_cloud_id}", return_json=False)
