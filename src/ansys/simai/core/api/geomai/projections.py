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

from typing import Any, Dict, List, Optional

from ansys.simai.core.api.mixin import ApiClientMixin


class GeomAIProjectionClientMixin(ApiClientMixin):
    """Provides the client for the GeomAI projections ("/geomai/projections") part of the API."""

    def geomai_projections(
        self, workspace_id: str, geometry_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get the list of the projections onto the model of a workspace.

        Args:
            workspace_id: ID of the workspace.
            geometry_id: Optional ID of a geometry to restrict the listing to.
        """
        params = {"geometry": geometry_id} if geometry_id is not None else None
        return self._get(f"geomai/workspaces/{workspace_id}/projections", params=params)

    def run_geomai_projection(self, workspace_id: str, geometry_id: str) -> Dict[str, Any]:
        """Project a geometry onto the model of a workspace.

        If a projection already exists for that geometry and model, it is
        returned as is instead of being recomputed.

        Args:
            workspace_id: ID of the workspace.
            geometry_id: ID of the geometry to project.
        """
        return self._post(
            f"geomai/workspaces/{workspace_id}/projections",
            json={"geometry": geometry_id},
        )

    def get_geomai_projection(self, projection_id: str) -> Dict[str, Any]:
        """Get information on a single projection.

        Args:
            projection_id: ID of the projection.
        """
        return self._get(f"geomai/projections/{projection_id}")

    def delete_geomai_projection(self, projection_id: str) -> None:
        """Delete a single projection.

        Args:
            projection_id: ID of the projection.
        """
        self._delete(f"geomai/projections/{projection_id}", return_json=False)
