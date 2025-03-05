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
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.types import (
    Filters,
    Identifiable,
    MonitorCallback,
    NamedFile,
    Path,
    SizedIterator,
    SubsetEnum,
    get_id_from_identifiable,
    to_raw_filters,
    unpack_named_file,
)
from ansys.simai.core.errors import InvalidArguments
from ansys.simai.core.utils.pagination import DataModelIterator

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
            f"training-data-parts/{training_data_part.id}/part",
            file,
            upload_id,
            monitor_callback=monitor_callback,
        )
        client._api.complete_training_data_part_upload(training_data_part.id, upload_id, parts)
    return training_data_part


class TrainingData(ComputableDataModel):
    """Provides the local representation of a training data object."""

    def __repr__(self) -> str:
        return f"<TrainingData: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """Name of the training data."""
        return self.fields["name"]

    @property
    def parts(self) -> List["TrainingDataPart"]:
        """List of all :class:`parts<ansys.simai.core.data.training_data_parts.TrainingDataPart>`
        objects in the training data.
        """
        return [
            self._client.training_data_parts._model_from(training_data_part)
            for training_data_part in self.fields["parts"]
        ]

    def get_subset(self, project: Identifiable["Project"]) -> Optional[SubsetEnum]:
        """Get the subset that the training data belongs to, in relation to the given project.

        Args:
            project: ID or :class:`model <.projects.Project>` of the project to check
                the :class:`~.projects.Project` object for, or its ID.

        Returns:
            The :obj:`~ansys.simai.core.data.types.SubsetEnum` of the subset to which
            the :class:`TrainingData` belongs to if any, ``None`` otherwise.
            (e.g. <SubsetEnum.TEST: 'Test'>)
        """
        project_id = get_id_from_identifiable(project, default=self._client._current_project)
        subset_value = self._client._api.get_training_data_subset(project_id, self.id).get("subset")
        return SubsetEnum(subset_value) if subset_value else None

    def assign_subset(
        self, project: Identifiable["Project"], subset: Optional[Union[SubsetEnum, str]]
    ) -> None:
        """Assign the training data to a subset in relation to a given project.

        Args:
            project: ID or :class:`model <.projects.Project>`
            subset: SubsetEnum attribute (e.g. SubsetEnum.TRAINING) or string value (e.g. "Training") or None to unassign.
                Available options: (Training, Test)

                Each new training data added to the project will be set to "None" by default.

                None allows for resetting the subset assignment of your training data, which will be automatically allocated
                in either test or training subsets upon each model building request. As a rule of thumb, 10% of all data should
                be allocated to the test subset.

                When wanting to assign a specific subset to your training data, note that:

                Each subset requires at least one data point.
                The training subset is used to train the model. The test subset is used for the model
                evaluation report but is not learned by the model.
                It is recommended to allocate about 10% of your data to the test subset.

        Returns:
            None
        """
        if subset is not None and subset not in SubsetEnum.__members__.values():
            raise InvalidArguments("Must be None or one of: 'Training', 'Test'.")

        project_id = get_id_from_identifiable(project, default=self._client._current_project)
        self._client._api.put_training_data_subset(project_id, self.id, subset)

    @property
    def extracted_metadata(self) -> Optional[Dict]:
        """Metadata extracted from the training data."""
        return self.fields["extracted_metadata"]

    def extract_data(self) -> None:
        """Extract or reextract the data from a training data.

        Data should be extracted from a training data once all its parts have been fully uploaded.
        This is done automatically when using :meth:`TrainingDataDirectory.upload_folder` to create training data.

        Data can only be reextracted from a training data if the extraction previously failed or if new files have been added.
        """
        self._client._api.compute_training_data(self.id)

    def delete(self) -> None:
        """Delete the training data on the server."""
        self._client._api.delete_training_data(self.id)

    def upload_part(
        self, file: NamedFile, monitor_callback: Optional[MonitorCallback] = None
    ) -> "TrainingDataPart":
        """Add a part to the training data.

        Args:
            file: :obj:`~ansys.simai.core.data.types.NamedFile` to upload.
            monitor_callback: Optional callback for monitoring the progress of the download.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.

        Returns:
            Created :class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart`.
        """
        return _upload_training_data_part(self.id, file, self._client, monitor_callback)

    def upload_folder(
        self,
        folder_path: Path,
    ) -> List["TrainingDataPart"]:
        """Upload all the parts contained in a folder to a :class:`~ansys.simai.core.data.training_data.TrainingData` instance.

        Upon upload completion, SimAI will extract data from each part.

        Args:
            folder_path: Path to the folder with the files to upload.

        Returns:
            List of uploaded training data parts.
        """
        return self._directory.upload_folder(self.id, folder_path)

    def add_to_project(self, project: Identifiable["Project"]):
        """Add the training data to a :class:`~ansys.simai.core.data.projects.Project` object.

        Args:
            project: ID or :class:`model <.projects.Project>` object of the project to add the data to.
        """
        project_id = get_id_from_identifiable(project)
        self._client._api.add_training_data_to_project(self.id, project_id)

    def remove_from_project(self, project: Identifiable["Project"]):
        """Remove the training data from a :class:`~ansys.simai.core.data.projects.Project` object.

        Args:
            project: ID or :class:`model <.projects.Project>` of the project to remove data from.

        Raises:
            ansys.simai.core.errors.ApiClientError: If the data is the project's sample.
            ansys.simai.core.errors.ApiClientError: If the project is in training.
        """
        project_id = get_id_from_identifiable(project)
        self._client._api.remove_training_data_from_project(self.id, project_id)


class TrainingDataDirectory(Directory[TrainingData]):
    """Provides a collection of methods related to training data.

    This class is accessed through ``client.training_data``.

    Example:
        List all of the training data::

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.training_data.list()
    """

    _data_model = TrainingData

    def iter(self, filters: Optional[Filters] = None) -> SizedIterator[TrainingData]:
        """Iterate over all :class:`TrainingData` objects on the server.

        Args:
            filters: Optional :obj:`~.types.Filters` to apply.

        Returns:
            Iterator over all :class:`TrainingData` objects on the server.
        """
        raw_filters = to_raw_filters(filters)
        raw_iterable = self._client._api.iter_training_data(filters=raw_filters)
        return DataModelIterator(raw_iterable, self)

    def list(self, filters: Optional[Filters] = None) -> List[TrainingData]:
        """List all :class:`TrainingData` objects on the server.

        Warning:
            This can take a very long time, consider using :py:meth:`~iter` instead.

        Args:
            filters: Optional :obj:`~.types.Filters` to apply.

        Returns:
            List of all :class:`TrainingData` objects on the server.
        """
        return list(self.iter(filters))

    def get(self, id) -> TrainingData:
        """Get a specific :class:`TrainingData` object from the server."""
        return self._model_from(self._client._api.get_training_data(id))

    def delete(self, training_data: Identifiable[TrainingData]) -> None:
        """Delete a :class:`TrainingData` object and its associated parts from the server.

        Args:
            training_data: ID or :class:`model <TrainingData>` object of the :class:`TrainingData` object.
        """
        return self._client._api.delete_training_data(get_id_from_identifiable(training_data))

    def create(self, name: str, project: Optional[Identifiable["Project"]] = None) -> TrainingData:
        """Create a :class:`TrainingData` object.

        Args:
            name: Name to give the new :class:`TrainingData` object.
            project: :class:`~.projects.Project` object to associate the data with.

        Returns:
            Created :class:`TrainingData` object.
        """
        project_id = get_id_from_identifiable(project, required=False)
        return self._model_from(self._client._api.create_training_data(name, project_id))

    def upload_part(
        self,
        training_data: Identifiable[TrainingData],
        file: NamedFile,
        monitor_callback: Optional[MonitorCallback],
    ) -> "TrainingDataPart":
        """Add a part to a :class:`TrainingData` object.

        Args:
            training_data: ID or :class:`model <TrainingData>` object of the training data to
                add the part to.
            file: :obj:`~ansys.simai.core.data.types.NamedFile` to upload.
            monitor_callback: Optional callback for monitoring the progress of the upload.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.

        Returns:
            Added :class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart` object.
        """
        return _upload_training_data_part(
            get_id_from_identifiable(training_data),
            file,
            self._client,
            monitor_callback,
        )

    def upload_folder(
        self,
        training_data: Identifiable[TrainingData],
        folder_path: Path,
    ) -> List["TrainingDataPart"]:
        """Upload all files in a folder to a :class:`~ansys.simai.core.data.training_data.TrainingData` object.

        This method automatically requests computation of the training data once the upload is complete
        unless specified otherwise.

        Args:
            training_data: ID or :class:`model <TrainingData>` object of the training data to upload parts to.
            folder_path: Path to the folder that contains the files to upload.
        """
        training_data_id = get_id_from_identifiable(training_data)
        path = pathlib.Path(folder_path)
        if not path.is_dir():
            raise InvalidArguments("Provided path is not a folder.")
        path_content = path.glob("[!.]*")
        files = (obj for obj in path_content if obj.is_file())
        uploaded_parts = []
        for file in files:
            uploaded_parts.append(
                _upload_training_data_part(training_data_id, file, self._client, None)
            )
        self._client._api.compute_training_data(training_data_id)
        return uploaded_parts
