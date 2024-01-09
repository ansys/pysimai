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

from typing import TYPE_CHECKING, List, Optional

from ansys.simai.core.data.base import DataModel, Directory
from ansys.simai.core.data.types import Identifiable, get_id_from_identifiable
from ansys.simai.core.errors import InvalidArguments

if TYPE_CHECKING:
    from ansys.simai.core.data.training_data import TrainingData


class Project(DataModel):
    """Local representation of a Project object."""

    def __repr__(self) -> str:
        return f"<Project: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """The name of project."""
        return self.fields["name"]

    @name.setter
    def name(self, new_name: str):
        """Rename the project.

        Args:
            new_name: the new name to give to the project
        """
        self._client._api.update_project(self.id, name=new_name)
        self.reload()

    @property
    def data(self) -> List["TrainingData"]:
        """Lists all the :class:`~ansys.simai.core.data.training_data.TrainingData` in this project."""
        raw_td_list = self._client._api.iter_training_data_in_project(self.id)
        return [
            self._client.training_data._model_from(training_data) for training_data in raw_td_list
        ]

    @property
    def sample(self) -> Optional["TrainingData"]:
        """The sample of the project.

        The sample determines what variable and settings are available during model configuration.
        """
        raw_sample = self.fields["sample"]
        if raw_sample is None:
            return None
        return self._client.training_data._model_from(self.fields["sample"])

    @sample.setter
    def sample(self, new_sample: Identifiable["TrainingData"]):
        td_id = get_id_from_identifiable(new_sample)
        self._client._api.set_project_sample(self.id, td_id)
        self.reload()

    def delete(self) -> None:
        """Deletes the project."""
        self._client._api.delete_project(self.id)


class ProjectDirectory(Directory[Project]):
    """Collection of methods related to projects.

    Accessed through ``client.projects``

    Example:
        Listing all the projects::

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.projects.list()
    """

    _data_model = Project

    def list(self) -> List[Project]:
        """Lists all the projects available on the server."""
        return [self._model_from(data) for data in self._client._api.projects()]

    def create(self, name: str) -> Project:
        """Creates a new project."""
        return self._model_from(self._client._api.create_project(name=name))

    def get(self, id: Optional[str] = None, name: Optional[str] = None):
        """Gets a project by name or id.

        Only one of id or name should be specified

        Args:
            id: The id of the project to get
            name: The name of the project to get
        """
        if name and id:
            raise InvalidArguments("Only one of name and id arguments should be specified")
        elif name:
            return self._model_from(self._client._api.get_project_by_name(name))
        elif id:
            return self._model_from(self._client._api.get_project(id))
        else:
            raise InvalidArguments("Either name or id argument should be specified")

    def delete(self, project: Identifiable[Project]) -> None:
        """Deletes a project.

        Args:
            project: The id or :class:`model <Project>` of the project to delete
        """
        self._client._api.delete_project(get_id_from_identifiable(project))
