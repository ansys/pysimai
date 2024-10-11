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


class WorkspaceClientMixin(ApiClientMixin):
    """Provides the client for the Workspace ("/workspaces") part of the API."""

    def workspaces(self):
        """List all workspaces."""
        return self._get("workspaces/")

    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Get information on a single workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            JSON representation of the workspace.

        Raises:
            ansys.simai.core.errors.NotFoundError: If no workspace with that ID exists.
            ansys.simai.core.errors.ApiClientError: On other HTTP errors.
        """
        return self._get(f"workspaces/{workspace_id}")

    def get_workspace_by_name(self, name: str):
        """Get information on a single workspace by name instead of ID.

        Args:
            name: Name of the workspace.
        """
        return self._get(f"workspaces/name/{quote(name)}")

    def get_workspace_model_manifest(self, workspace_id):
        """Get the public part of the manifest for the given workspace.

        Args:
            workspace_id: ID of the workspace.

        Raises:
            ansys.simai.core.errors.NotFoundError: If no workspace with that ID exists.
            ansys.simai.core.errors.ApiClientError: On other HTTP errors.
        """
        return self._get(f"workspaces/{workspace_id}/model/manifest/public")

    def create_workspace(self, name: str, model_id: str, **kwargs):
        """Create a workspace.

        Args:
            name: Name to give to the new workspace.
            model_id: ID of the model that the workspace is to use.
            **kwargs: Additional arguments for the workspace creation.

        Returns:
            JSON representation of the new workspace.
        """
        return self._post("workspaces/", json={"name": name, "model": model_id, **kwargs})

    def delete_workspace(self, workspace_id: str):
        """Delete a workspace.

        Args:
            workspace_id: ID of the workspace.

        Raises:
            ansys.simai.core.errors.NotFoundError: If no workspace with that ID exists.
            ansys.simai.core.errors.ApiClientError: On other HTTP errors.
        """
        return self._delete(f"workspaces/{workspace_id}")

    def download_workspace_model_evaluation_report(self, workspace_id: str, file: Optional[File]):
        return self.download_file(f"workspaces/{workspace_id}/model-evaluation-report", file)

    def download_workspace_mer_data(self, workspace_id: str, file: Optional[File]):
        return self.download_file(f"workspaces/{workspace_id}/mer-data", file)
