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

import logging
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Optional

from ansys.simai.core.data.base import DataModel, Directory
from ansys.simai.core.data.model_configuration import ModelConfiguration
from ansys.simai.core.data.types import Identifiable, get_id_from_identifiable
from ansys.simai.core.errors import InvalidArguments, ProcessingError

if TYPE_CHECKING:
    from ansys.simai.core.data.global_coefficients_requests import (
        CheckGlobalCoefficient,
        ComputeGlobalCoefficient,
    )
    from ansys.simai.core.data.training_data import TrainingData

EXTRA_CALCULETTE_FIELDS = ["Area", "Normals", "Centroids"]

logger = logging.getLogger(__name__)


class IsTrainableInfo(NamedTuple):
    """Properties for project's trainability.

    The objects of this class can be used as booleans
    in condition statements as in the example:

    Example:
        Verify the project is trainable

        .. code-block:: python

            pt = my_project.is_trainable()

            if pt:
                print(pt)

        It prints:

        .. code-block:: shell

            <is_trainable: False, reason(s): Not enough data to train a model: we need at least 3 data points to train a model.>

    Attributes:
        is_trainable (bool):    True if the project is trainable, False if it is not.
        reason (str):           If not_trainable is False, the reason why the project is not trainable. None otherwise.

    """

    is_trainable: bool
    reason: str = None

    def __bool__(self) -> bool:
        return self.is_trainable

    def __repr__(self) -> str:
        return f"<is_trainable: {self.is_trainable}, reason(s): {self.reason}>"


class Project(DataModel):
    """Provides the local representation of a  project object."""

    def __repr__(self) -> str:
        return f"<Project: {self.id}, {self.name}>"

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
        self._client._api.update_project(self.id, name=new_name)
        self.reload()

    @property
    def data(self) -> List["TrainingData"]:
        """List of all :class:`~ansys.simai.core.data.training_data.TrainingData` instances in the project."""
        raw_td_list = self._client._api.iter_training_data_in_project(self.id)
        return [
            self._client.training_data._model_from(training_data) for training_data in raw_td_list
        ]

    @property
    def sample(self) -> Optional["TrainingData"]:
        """Sample of the project. The sample determines what variable and settings are available during model configuration."""
        raw_sample = self.fields["sample"]
        if raw_sample is None:
            return None
        return self._client.training_data._model_from(self.fields["sample"])

    @sample.setter
    def sample(self, new_sample: Identifiable["TrainingData"]):
        td_id = get_id_from_identifiable(new_sample)
        self._client._api.set_project_sample(self.id, td_id)
        self.reload()

    @property
    def last_model_configuration(self) -> ModelConfiguration:
        """Last :class:`configuration <ansys.simai.core.data.model_configuration.ModelConfiguration>` used for model training in this project."""
        return ModelConfiguration(project=self, **self.fields.get("last_model_configuration"))

    def delete(self) -> None:
        """Delete the project."""
        self._client._api.delete_project(self.id)

    def is_trainable(self) -> bool:
        """Check if the project meets the prerequisites to be trained."""
        tt = self._client._api.is_project_trainable(self.id)
        return IsTrainableInfo(**tt)

    def get_variables(self) -> Optional[Dict[str, List[str]]]:
        """Get the available variables for the model's input/output."""
        if not self.sample:
            return None

        sample_metadata = self.sample.fields.get("extracted_metadata")
        data = {}
        for key, vals in sample_metadata.items():
            local_fields = vals.get("fields", [])
            data[key] = [local_field.get("name") for local_field in local_fields]
        return data

    def verify_gc_formula(
        self, gc_formula: str, bc: list[str] = None, surface_variables: list[str] = None
    ):
        """Verify whether the syntax of the global coefficient formula is valid."""

        if not self.sample:
            raise ProcessingError(
                f"No sample is set in the project {self.id}. A sample should be set to verify a global coefficient formula."
            )

        sample_metadata = self.sample.fields.get("extracted_metadata")

        gc_check: CheckGlobalCoefficient = self._client._check_gc_formula_directory._model_from(
            data={
                "id": f"{self.id}-check-{gc_formula}",
            },
            project_id=self.id,
            gc_formula=gc_formula,
            sample_metadata=sample_metadata,
            bc=bc,
            surface_variables=surface_variables,
        )

        gc_check.run()
        gc_check.wait()

        return gc_check.is_ready

    def compute_gc_formula(
        self, gc_formula: str, bc: list[str] = None, surface_variables: list[str] = None
    ):
        """Compute the result of a global coefficient formula according to the project sample."""

        if not self.sample:
            raise ProcessingError(
                f"No sample is set for the project {self.id}. A sample should be set for computing the results of a Global Coefficients formula."
            )

        sample_metadata = self.sample.fields.get("extracted_metadata")

        gc_compute: ComputeGlobalCoefficient = (
            self._client._compute_gc_formula_directory._model_from(
                data={
                    "id": f"{self.id}-compute-{gc_formula}",
                },
                project_id=self.id,
                gc_formula=gc_formula,
                sample_metadata=sample_metadata,
                bc=bc,
                surface_variables=surface_variables,
            )
        )

        gc_compute.run()
        gc_compute.wait()

        return gc_compute.result if gc_compute.is_ready else None


class ProjectDirectory(Directory[Project]):
    """Provides a collection of methods related to projects.

    This class is accessed through ``client.projects``.

    Example:
        List all projects::

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.projects.list()
    """

    _data_model = Project

    def list(self) -> List[Project]:
        """List all projects available on the server."""
        return [self._model_from(data) for data in self._client._api.projects()]

    def create(self, name: str) -> Project:
        """Create a project."""
        return self._model_from(self._client._api.create_project(name=name))

    def get(self, id: Optional[str] = None, name: Optional[str] = None):
        """Get a project by either ID or name.

        You can specify either the ID or the name, not both.

        Args:
            id: ID of the project.
            name: Name of the project.
        """
        if name and id:
            raise InvalidArguments("Only the 'id' or 'name' argument should be specified.")
        elif name:
            return self._model_from(self._client._api.get_project_by_name(name))
        elif id:
            return self._model_from(self._client._api.get_project(id))
        else:
            raise InvalidArguments("Either the 'id' or 'name' argument should be specified.")

    def delete(self, project: Identifiable[Project]) -> None:
        """Delete a project.

        Args:
            project: ID or :class:`model <Project>` of the project.
        """
        self._client._api.delete_project(get_id_from_identifiable(project))
