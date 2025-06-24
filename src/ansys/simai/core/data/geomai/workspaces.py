# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

from typing import TYPE_CHECKING, BinaryIO, List, Optional, Union

from ansys.simai.core.data.base import DataModel, Directory
from ansys.simai.core.data.types import File, Identifiable, get_id_from_identifiable

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.predictions import GeomAIPrediction
    from ansys.simai.core.data.geomai.projects import GeomAIProject


class GeomAIWorkspace(DataModel):
    """Provides the local representation of a GeomAI workspace object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_manifest = None

    def __repr__(self) -> str:
        return f"<GeomAIWorkspace: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """Name of the workspace."""
        return self.fields["name"]

    def delete(self):
        """Delete the workspace."""
        return self._client._api.delete_geomai_workspace(self.id)

    def list_predictions(self) -> List["GeomAIPrediction"]:
        """Lists all the predictions in the workspace."""
        return [
            self._client.geomai.predictions._model_from(prediction)
            for prediction in self._client._api.geomai_predictions(self.id)
        ]

    def set_as_current_workspace(self) -> None:
        """Configure the client to use this workspace instead of the one currently configured."""
        self._client.geomai.current_workspace = self

    def download_latent_parameters_json(self, file: Optional[File] = None) -> Union[None, BinaryIO]:
        """Download the json file containing the latent parameters for the model's training data.

        Args:
            file: Binary file-object or the path of the file to put the content into.

        Returns:
            ``None`` if a file is specified or a binary file-object otherwise.
        """
        return self._client._api.download_geomai_workspace_latent_parameters(self.id, file)


class GeomAIWorkspaceDirectory(Directory[GeomAIWorkspace]):
    """Provides a collection of methods related to GeomAI workspaces.

    This class is accessed through ``client.geomai.workspaces``.

    Example:
      .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.geomai.workspaces.list()
    """

    _data_model = GeomAIWorkspace

    def list(self) -> List[GeomAIWorkspace]:
        """List all workspaces from the server."""
        return [self._model_from(workspace) for workspace in self._client._api.geomai_workspaces()]

    def get(self, id: Optional[str] = None, name: Optional[str] = None) -> GeomAIWorkspace:
        """Get a specific workspace object from the server by either ID or name.

        You can specify either the ID or the name, not both.

        Args:
            id: ID of the workspace.
            name: Name of the workspace.

        Returns:
            A :class:`GeomAIWorkspace`.

        Raises:
            NotFoundError: No workspace with the given ID exists.
        """
        if name and id:
            raise ValueError("'id' and 'name' cannot both be specified.")
        if name:
            return self._model_from(self._client._api.get_geomai_workspace_by_name(name))
        if id:
            return self._model_from(self._client._api.get_geomai_workspace(id))
        raise ValueError("Either 'id' or 'name' must be specified.")

    def create(self, name: str, project: Identifiable["GeomAIProject"]) -> GeomAIWorkspace:
        """Create a workspace.

        Args:
            name: Name to give the new workspace.
            project: ID or :class:`project <.projects.GeomAIProject>` of the workspace.
        """
        return self._model_from(
            self._client._api.create_geomai_workspace(name, get_id_from_identifiable(project))
        )

    def delete(self, workspace: Identifiable[GeomAIWorkspace]) -> None:
        """Delete a workspace.

        Args:
            workspace: ID or :class:`model <GeomAIWorkspace>` of the workspace.
        """
        self._client._api.delete_geomai_workspace(get_id_from_identifiable(workspace))
