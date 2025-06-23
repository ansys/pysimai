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

from typing import TYPE_CHECKING, List, Optional, Union

from ansys.simai.core.data.base import DataModel, Directory
from ansys.simai.core.data.geomai.models import GeomAIModel, GeomAIModelConfiguration
from ansys.simai.core.data.types import Identifiable, get_id_from_identifiable
from ansys.simai.core.errors import InvalidArguments, ProcessingError

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.training_data import GeomAITrainingData
    from ansys.simai.core.data.geomai.workspaces import GeomAIWorkspace


class GeomAIProject(DataModel):
    """Provides the local representation of a GeomAI project object."""

    def __repr__(self) -> str:
        return f"<GeomAIProject: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """Name of project."""
        return self.fields["name"]

    @name.setter
    def name(self, new_name: str):
        """Rename the project.

        Args:
            new_name: New name to give to the project.
        """
        self._client._api.update_geomai_project(self.id, name=new_name)
        self.reload()

    def data(self) -> List["GeomAITrainingData"]:
        """Lists all :class:`~.training_data.GeomAITrainingData` instances in the project."""
        raw_td_list = self._client._api.iter_training_data_in_geomai_project(self.id)
        return [
            self._client.geomai.training_data._model_from(training_data)
            for training_data in raw_td_list
        ]

    def workspaces(self) -> List["GeomAIWorkspace"]:
        """Lists all :class:`~.workspaces.GeomAIWorkspace` instances in the project."""
        workspaces = self._client._api.get_geomai_project_related_workspaces(self.id)
        return [self._client.geomai.workspaces._model_from(workspace) for workspace in workspaces]

    @property
    def last_model_configuration(self) -> Optional[GeomAIModelConfiguration]:
        """Last :class:`configuration <.models.GeomAIModelConfiguration>` used for model training in this project."""
        raw_last_model_configuration = self.fields.get("last_model_configuration")
        if raw_last_model_configuration is None:
            return None
        return GeomAIModelConfiguration(**raw_last_model_configuration)

    def delete(self) -> None:
        """Delete the project."""
        self._client._api.delete_geomai_project(self.id)

    def cancel_build(self):
        """Cancels a build if there is one pending.

        Raises:
            ProcessingError: If there is no build to cancel
        """

        self.reload()
        if self.fields.get("is_being_trained") is False:
            raise ProcessingError("No build pending for this project.")
        self._client._api.cancel_geomai_build(self.id)

    def build_model(self, configuration: Union[dict, GeomAIModelConfiguration]) -> GeomAIModel:
        """Launches a GeomAI build with the given configuration.

        Args:
            configuration: the configuration to run the model with.
                See :class:`.models.GeomAIModelConfiguration` for details.
        """
        return self._client.geomai.models.build(self.id, configuration)

    def create_workspace(self, name: str) -> "GeomAIWorkspace":
        """Creates a workspace using the latest model trained in this project.

        Args:
            name: Name to give to the new workspace
        """
        return self._client.geomai.workspaces._model_from(
            self._client._api.create_geomai_workspace(name, self.id)
        )

    def set_as_current_project(self) -> None:
        """Configure the client to use this project instead of the one currently configured."""
        self._client.geomai.current_project = self


class GeomAIProjectDirectory(Directory[GeomAIProject]):
    """Provides a collection of methods related to projects.

    This class is accessed through ``client.projects``.

    Example:
        List all projects::

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.geomai.projects.list()
    """

    _data_model = GeomAIProject

    def list(self) -> List[GeomAIProject]:
        """List all projects available on the server."""
        return [self._model_from(data) for data in self._client._api.geomai_projects()]

    def create(self, name: str) -> GeomAIProject:
        """Create a project."""
        return self._model_from(self._client._api.create_geomai_project(name=name))

    def get(self, id: Optional[str] = None, name: Optional[str] = None) -> GeomAIProject:
        """Get a project by either ID or name.

        You can specify either the ID or the name, not both.

        Args:
            id: ID of the project.
            name: Name of the project.

        Returns:
            :class:`GeomAIProject` instance with the given ID if it exists.

        Raises:
            NotFoundError: If the project doesn't exist
        """
        if name and id:
            raise InvalidArguments("Only the 'id' or 'name' argument should be specified.")
        elif name:
            return self._model_from(self._client._api.get_geomai_project_by_name(name))
        elif id:
            return self._model_from(self._client._api.get_geomai_project(id))
        else:
            raise InvalidArguments("Either the 'id' or 'name' argument should be specified.")

    def delete(self, project: Identifiable[GeomAIProject]) -> None:
        """Delete a project.

        Args:
            project: ID or :class:`model <GeomAIProject>` of the project.
        """
        self._client._api.delete_geomai_project(get_id_from_identifiable(project))

    def cancel_build(self, project: Identifiable[GeomAIProject]):
        """Cancel a build if one is in progress.

        Args:
            project: ID or :class:`model <GeomAIProject>` of the project.
        """

        project_id = get_id_from_identifiable(project)
        project_response = self._client._api.get_geomai_project(project_id)
        if project_response.get("is_being_trained") is False:
            raise ProcessingError("No build pending for this project.")
        self._client._api.cancel_geomai_build(project_id)
