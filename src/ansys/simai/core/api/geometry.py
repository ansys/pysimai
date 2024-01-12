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
import logging
from typing import Any, BinaryIO, Dict, List, Optional, Union
from urllib.parse import quote

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.data.types import File, MonitorCallback

logger = logging.getLogger(__name__)


class GeometryClientMixin(ApiClientMixin):
    """Provides the client for the Geometry ("/geometries/") part of the API."""

    def geometries(self, workspace_id: str, filters: Optional[Dict[str, Any]] = None):
        """Get list of all geometries."""
        if filters is not None:
            params = {"filters": json.dumps(filters), "workspace": workspace_id}
        else:
            params = {"workspace": workspace_id}
        return self._get("geometries/", params=params)

    def get_geometry(self, geometry_id: str):
        """Get information on a single geometry.

        Args:
            geometry_id: ID of the geometry.
        """
        return self._get(f"geometries/{geometry_id}")

    def get_geometry_by_name(self, name: str, workspace_id: str):
        """Get information on a single geometry by name instead of ID.

        Args:
            name: Name of the geometry.
            workspace_id: ID of the workspace that the geometry belongs to.
        """
        return self._get(f"geometries/name/{quote(name)}", params={"workspace": workspace_id})

    def delete_geometry(self, geometry_id: str):
        """Delete a single geometry.

        All objects associated with that geometry are also deleted.

        Args:
            geometry_id: ID of the geometry.
        """
        # TODO: Have user confirm or delete confirmation from API ?
        return self._delete(
            f"geometries/{geometry_id}",
            params={"confirm": True},
            return_json=False,
        )

    def update_geometry(
        self,
        geometry_id: str,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """Update the information for a given geometry.

        Args:
            geometry_id: ID of the geometry.
            name: New name to give to the geometries.
            metadata: Metadata to update the geometry with.
        """
        request_json = {}
        if name is not None:
            request_json["name"] = name
        if metadata is not None:
            request_json["metadata"] = metadata
        self._patch(f"geometries/{geometry_id}", json=request_json, return_json=False)

    def create_geometry(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        extension: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Create a geometry without pushing the data.

        Args:
            workspace_id: ID of the workspace to assign the geometry to.
            name: Name to give to the geometry.
            extension: Extension to give to the file.
            metadata: Metadata to apply to the geometry on creation.

        Returns:
           Tuple containing the geometry object and a 'presigned post'
           dictionary, which contains the URL to upload the data and fields to
           that was included in the request.
        """
        post_data = {
            "name": name,
            "workspace": workspace_id,
            "file_extension": extension,
        }
        if metadata:
            post_data.update({"metadata": json.dumps(metadata)})
        response = self._post(
            "geometries/",
            json=post_data,
        )
        return (response["geometry"], response["upload_id"])

    def complete_geometry_upload(self, id: str, upload_id: str, parts: List[Dict[str, Any]]):
        self._post(f"geometries/{id}/complete", json={"upload_id": upload_id, "parts": parts})

    def download_geometry(
        self,
        geometry_id: str,
        file: Optional[File] = None,
        monitor_callback: Optional[MonitorCallback] = None,
    ) -> Union[None, BinaryIO]:
        """Download the input geometry into the file at the given path.

        Args:
            geometry_id: ID of the geometry to download.
            file: Binary file-object or the path of the file to put the content into.
            monitor_callback: Function or method to pass the ``bytes_read`` delta to.
                This delta can be used to monitor progress.
        """
        return self.download_file(f"geometries/{geometry_id}/download", file, monitor_callback)

    def get_geometry_predictions(self, geometry_id: str):
        """Get predictions associated with a geometry.

        Args:
            geometry_id: ID of the geometry.
        """
        return self._get(f"geometries/{geometry_id}/predictions")
