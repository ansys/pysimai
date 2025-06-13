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

from typing import Any, Dict, Optional
from urllib.parse import quote

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.data.types import File


class GeomAIWorkspaceClientMixin(ApiClientMixin):
    """Provides the client for the Workspace ("/workspaces") part of the API."""

    def geomai_workspaces(self):
        """List all workspaces."""
        return self._get("geomai/workspaces/")

    def get_geomai_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Get information on a single workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            JSON representation of the workspace.

        Raises:
            ansys.simai.core.errors.NotFoundError: If no workspace with that ID exists.
            ansys.simai.core.errors.ApiClientError: On other HTTP errors.
        """
        return self._get(f"geomai/workspaces/{workspace_id}")

    def get_geomai_workspace_by_name(self, name: str):
        """Get information on a single workspace by name instead of ID.

        Args:
            name: Name of the workspace.
        """
        return self._get(f"geomai/workspaces/name/{quote(name)}")

    def create_geomai_workspace(self, name: str, project_id: str, **kwargs):
        """Create a workspace.

        Args:
            name: Name to give to the new workspace.
            project_id: The project in which to create a workspace
            **kwargs: Additional arguments for the workspace creation.

        Returns:
            JSON representation of the new workspace.
        """
        return self._post(f"geomai/projects/{project_id}/workspaces", json={"name": name, **kwargs})

    def delete_geomai_workspace(self, workspace_id: str):
        """Delete a workspace.

        Args:
            workspace_id: ID of the workspace.

        Raises:
            ansys.simai.core.errors.NotFoundError: If no workspace with that ID exists.
            ansys.simai.core.errors.ApiClientError: On other HTTP errors.
        """
        return self._delete(f"geomai/workspaces/{workspace_id}")

    def download_geomai_workspace_latent_parameters(self, workspace_id: str, file: Optional[File]):
        return self.download_file(
            f"geomai/workspaces/{workspace_id}/model/latent-parameters-json", file
        )
