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

import pathlib
from typing import TYPE_CHECKING, Dict, List, Optional

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.types import (
    Identifiable,
    MonitorCallback,
    NamedFile,
    Path,
    get_id_from_identifiable,
    get_object_from_identifiable,
    unpack_named_file,
)
from ansys.simai.core.errors import InvalidArguments

if TYPE_CHECKING:
    from ansys.simai.core.data.projects import Project
    from ansys.simai.core.data.training_data_parts import TrainingDataPart


def _upload_training_data_part(id, named_part, client, monitor_callback):
    with unpack_named_file(named_part) as (file, name, extension):
        (training_data_part_fields, upload_id) = client._api.create_training_data_part(
            id, name, extension
        )
        training_data_part = client.training_data_parts._model_from(
            training_data_part_fields, is_upload_complete=False
        )
        parts = client._api.upload_parts(
            f"training_data_parts/{training_data_part.id}/part", file, upload_id, monitor_callback
        )
        client._api.complete_training_data_part_upload(training_data_part.id, upload_id, parts)
    return training_data_part


class TrainingData(ComputableDataModel):
    """Local representation of a TrainingData object."""

    def __repr__(self) -> str:
        return f"<TrainingData: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """The name of the training data."""
        return self.fields["name"]

    @property
    def parts(self) -> List["TrainingDataPart"]:
        """Lists the :class:`parts<ansys.simai.core.data.training_data_parts.TrainingDataPart>` in that TrainingData."""
        return [
            self._client.training_data_parts._model_from(training_data_part)
            for training_data_part in self.fields["parts"]
        ]

    def get_subset(self, project: Identifiable["Project"]) -> Optional[str]:
        """Indicates which subset this training data belongs to, in relation to the given project.

        Args:
            project: The id or :class:`model <.projects.Project>` of the project to check for :class:`~.projects.Project` to check for, or its id

        Returns:
            The name of the subset this training data belongs to in the given project
        """
        project_model = get_object_from_identifiable(
            project, self._client.projects, default=self._client.current_project
        )
        for subset_name, list_ids in project_model.subsets:
            if self.id in list_ids:
                return subset_name

    @property
    def extracted_metadata(self) -> Optional[Dict]:
        """The metadata extracted from the training data."""
        return self.fields["extracted_metadata"]

    def compute(self) -> None:
        """Requests to compute or recompute the training data.

        Training data should be computed once all its parts have been fully uploaded

        Recomputation can only be requested if it previously failed or if new data has been added.
        """
        self._client._api.compute_training_data(self.id)

    def delete(self) -> None:
        """Deletes the training data on the server."""
        self._client._api.delete_training_data(self.id)

    def upload_part(
        self, file: NamedFile, monitor_callback: Optional[MonitorCallback] = None
    ) -> "TrainingDataPart":
        """Adds a part to a training data.

        Args:
            file: A :obj:`~ansys.simai.core.data.types.NamedFile` to upload.
            monitor_callback: An optional callback to monitor the progress of the download.
                See :obj:`~ansys.simai.core.data.types.MonitorCallback` for details.

        Returns:
            The created :class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart`
        """
        return _upload_training_data_part(self.id, file, self._client, monitor_callback)

    def upload_folder(
        self,
        folder_path: Path,
        compute: bool = True,
        monitor_callback: Optional[MonitorCallback] = None,
    ) -> List["TrainingDataPart"]:
        """Uploads all the parts contained in a folder to a :class:`~ansys.simai.core.data.training_data.TrainingData`.

        Automatically requests computation of the training data
        once the upload is complete unless specified otherwise.

        Args:
            folder_path: Path to the folder which contains the files to upload
            compute: Whether to compute the training data after upload, defaults to True
            monitor_callback: An optional callback to monitor the progress of the download.
                See :obj:`~ansys.simai.core.data.types.MonitorCallback` for details.

        Returns:
            The list of created training data parts
        """
        return self._directory.upload_folder(self.id, folder_path, compute, monitor_callback)

    def add_to_project(self, project: Identifiable["Project"]):
        """Adds the training data into a :class:`~ansys.simai.core.data.projects.Project`.

        Args:
            project: The id or :class:`model <.projects.Project>` of the project into which the data is to be added
        """
        project_id = get_id_from_identifiable(project)
        self._client._api.add_training_data_to_project(self.id, project_id)

    def remove_from_project(self, project: Identifiable["Project"]):
        """Removes the training data from a :class:`~ansys.simai.core.data.projects.Project`.

        Args:
            project: The id or :class:`model <.projects.Project>` of the project from which the data is to be removed.

        Raises:
            ansys.simai.core.errors.ApiClientError: if the data is the project's sample
            ansys.simai.core.errors.ApiClientError: if the project is in training
        """
        project_id = get_id_from_identifiable(project)
        self._client._api.remove_training_data_from_project(self.id, project_id)


class TrainingDataDirectory(Directory[TrainingData]):
    """Collection of methods related to training data.

    Accessed through ``client.training_data``.

    Example:
        Listing all the training data::

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.training_data.list()
    """

    _data_model = TrainingData

    def list(self) -> List[TrainingData]:
        """Lists :class:`TrainingData` from the server.

        Returns:
            The list of all TrainingData records on the server.
        """
        return [
            self._model_from(training_data)
            for training_data in self._client._api.iter_training_data()
        ]

    def get(self, id) -> TrainingData:
        """Gets a specific :class:`TrainingData` from the server."""
        return self._model_from(self._client._api.get_training_data(id))

    def delete(self, training_data: Identifiable[TrainingData]) -> None:
        """Deletes a TrainingData and it's associated parts from the server.

        Args:
            training_data: The id or :class:`model <TrainingData>` of the training data to delete
        """
        return self._client._api.delete_training_data(get_id_from_identifiable(training_data))

    def create(self, name: str, project: Optional[Identifiable["Project"]] = None) -> TrainingData:
        """Creates a new :class:`TrainingData` object.

        Args:
            name: The name given to the new :class:`TrainingData`.
            project: Associate the data with a :class:`~.projects.Project`.

        Returns:
            The created TrainingData
        """
        project_id = get_id_from_identifiable(project, required=False)
        return self._model_from(self._client._api.create_training_data(name, project_id))

    def upload_part(
        self,
        training_data: Identifiable[TrainingData],
        file: NamedFile,
        monitor_callback: Optional[MonitorCallback],
    ) -> "TrainingDataPart":
        """Adds a part to a training data.

        Args:
            training_data: The id or :class:`model <TrainingData>` of the training data that will contain the part
            file: A :obj:`~ansys.simai.core.data.types.NamedFile` to upload
            monitor_callback: An optional callback to monitor the progress of the download.
                See :obj:`~ansys.simai.core.data.types.MonitorCallback` for details.

        Returns:
            The created :class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart`
        """
        return _upload_training_data_part(
            get_id_from_identifiable(training_data), file, self._client, monitor_callback
        )

    def upload_folder(
        self, training_data: Identifiable[TrainingData], folder_path: Path, compute: bool = True
    ) -> List["TrainingDataPart"]:
        """Uploads all the files contained in a folder to a :class:`~ansys.simai.core.data.training_data.TrainingData`.

        Automatically requests computation of the training data
        once the upload is complete unless specified otherwise

        Args:
            training_data: The id or :class:`model <TrainingData>` of the training data that will contain the parts
            folder_path: Path to the folder which contains the files to upload
            compute: Whether to compute the training data after upload, defaults to True
        """
        path = pathlib.Path(folder_path)
        if not path.is_dir():
            raise InvalidArguments("Provided path is not a folder")
        path_content = path.glob("[!.]*")
        files = (obj for obj in path_content if obj.is_file())
        uploaded_parts = []
        for file in files:
            uploaded_parts.append(_upload_training_data_part(id, file, self._client, None))
        if compute:
            self._client._api.compute_training_data(id)
        return uploaded_parts
