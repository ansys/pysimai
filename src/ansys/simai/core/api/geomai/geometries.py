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

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from ansys.simai.core.api.mixin import ApiClientMixin


class GeomAIGeometryClientMixin(ApiClientMixin):
    """Provides the client for the GeomAI geometries ("/geomai/geometries") part of the API."""

    def geomai_geometries(self) -> List[Dict[str, Any]]:
        """List all the GeomAI geometries."""
        return self._get("geomai/geometries/")

    def get_geomai_geometry(self, geometry_id: str) -> Dict[str, Any]:
        """Get information on a single GeomAI geometry.

        Args:
            geometry_id: ID of the geometry.
        """
        return self._get(f"geomai/geometries/{geometry_id}")

    def get_geomai_geometry_by_name(self, name: str) -> Dict[str, Any]:
        """Get information on a single GeomAI geometry by name.

        Args:
            name: Name of the geometry.
        """
        return self._get(f"geomai/geometries/name/{quote(name)}")

    def create_geomai_geometry(self, name: str, extension: str) -> Tuple[Dict[str, Any], str]:
        """Create a GeomAI geometry without uploading the data.

        Args:
            name: Name of the geometry, without its extension.
            extension: Extension of the file.

        Returns:
            Tuple containing the geometry object and the upload ID to use for
            further requests.
        """
        response = self._post(
            "geomai/geometries/",
            json={"name": name, "file_extension": extension},
        )
        return (response["geometry"], response["upload_id"])

    def complete_geomai_geometry_upload(
        self, geometry_id: str, upload_id: str, parts: List[Dict[str, Any]]
    ) -> None:
        """Complete the multipart upload of a GeomAI geometry.

        Args:
            geometry_id: ID of the geometry.
            upload_id: ID of the multipart upload.
            parts: List of the uploaded parts.
        """
        self._post(
            f"geomai/geometries/{geometry_id}/complete",
            json={"upload_id": upload_id, "parts": parts},
            return_json=False,
        )

    def update_geomai_geometry(self, geometry_id: str, name: Optional[str] = None) -> None:
        """Update the information of a GeomAI geometry.

        Args:
            geometry_id: ID of the geometry.
            name: New name to give to the geometry.
        """
        request_json = {}
        if name is not None:
            request_json["name"] = name
        self._patch(f"geomai/geometries/{geometry_id}", json=request_json, return_json=False)

    def delete_geomai_geometry(self, geometry_id: str) -> None:
        """Delete a single GeomAI geometry.

        Args:
            geometry_id: ID of the geometry.
        """
        self._delete(f"geomai/geometries/{geometry_id}", return_json=False)
