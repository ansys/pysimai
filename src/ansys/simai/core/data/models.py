# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Dict, List

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.errors import ProcessingError

if TYPE_CHECKING:
    from ansys.simai.core.data.projects import Project


@dataclass
class GcField:
    """Single Global Coefficient field."""

    formula: str
    name: str


@dataclass
class ModelInput:
    """The inputs of a model."""

    surface: List[str] = None
    boundary_conditions: List[str] = None


@dataclass
class ModelOutput:
    """The outputs of a model."""

    surface: List[str] = None
    volume: List[str] = None
    global_coefficients: List[GcField] = None


@dataclass
class ModelConfiguration(ComputableDataModel):
    """The configuration for building a model."""

    boundary_conditions: Dict[str, Any] = None
    build_preset: str = None
    continuous: bool = False
    fields: Dict[str, Any] = None
    global_coefficients: List[Dict[str, Any]] = None
    simulation_volume: Dict[str, Any] = None
    project: "Project" = None
    _model_input: ModelInput = None
    _model_output: ModelOutput = ModelOutput()

    @property
    def input(self) -> ModelInput:
        """The inputs of a model."""
        return self._model_input

    @property
    def output(self) -> ModelOutput:
        """The outputs of a model."""
        return self._model_output

    @input.setter
    def input(self, model_input: ModelInput):
        """Sets the inputs of a model."""

        self.project.reload()

        if not self.project.sample:
            raise ProcessingError(
                f"No sample is set in the project {self.project.id}. A sample should be set before setting the model's input"
            )

        sample_metadata = self.project.sample.fields.get("extracted_metadata")

        if self.fields is None:
            self.fields = {}

        if model_input.surface is not None:
            self.fields["surface_input"] = [
                fd
                for fd in sample_metadata.get("surface").get("fields")
                if fd.get("name") in model_input.surface
            ]
            self._model_input.surface = model_input.surface

        if model_input.boundary_conditions is not None:
            self.boundary_conditions = {bc_name: {} for bc_name in model_input.boundary_conditions}
            self._model_input.boundary_conditions = model_input.boundary_conditions

    @output.setter
    def output(self, model_output: ModelOutput):
        """Sets the outputs of a model."""

        self.project.reload()

        if not self.project.sample:
            raise ProcessingError(
                f"No sample is set in the project {self.project.id}. A sample should be set before setting the model's output"
            )

        sample_metadata = self.project.sample.fields.get("extracted_metadata")
        if self.fields is None:
            self.fields = {}
        if model_output.volume is not None:
            self.fields["volume"] = [
                fd
                for fd in sample_metadata.get("volume").get("fields")
                if fd.get("name") in model_output.volume
            ]
            self._model_output.volume = model_output.volume

        if model_output.surface is not None:
            self.fields["surface"] = [
                fd
                for fd in sample_metadata.get("surface").get("fields")
                if fd.get("name") in model_output.surface
            ]
            self._model_output.surface = model_output.surface

        if model_output.global_coefficients is not None:
            if self.global_coefficients is None:
                self.global_coefficients = []
            for gc in model_output.global_coefficients:
                bc_keys = self.boundary_conditions.keys() if self.boundary_conditions else None
                self.project.verify_gc_formula(gc.formula, bc_keys, model_output.surface)
                self.global_coefficients += [asdict(gc)]

            self._model_output.global_coefficients = model_output.global_coefficients

    def to_payload(self):
        """Constracts the payload for a build request."""
        return {
            "boundary_conditions": self.boundary_conditions,
            "build_preset": self.build_preset,
            "continuous": self.continuous,
            "fields": self.fields,
            "global_coefficients": self.global_coefficients,
            "simulation_volume": self.simulation_volume,
        }

    def global_coefficient_values(self):
        """Computes the results of ."""
        rr = []

        for gc in self._model_output.global_coefficients:
            bc_keys = self.boundary_conditions.keys() if self.boundary_conditions else None
            rr += [self.project.compute_gc_formula(gc.formula, bc_keys, self._model_output.surface)]
        return rr


class Model(ComputableDataModel):
    """Training model representation."""

    def __repr__(self) -> str:
        return f"<Model: {self.id}>"

    @property
    def project_id(self) -> str:
        """The ID of the project where the model exists."""
        return self.fields["project_id"]

    @property
    def configuration(self) -> ModelConfiguration:
        """The build configuration of model."""
        return ModelConfiguration(project_id=self.project_id, **self.fields["configuration"])


class ModelDirectory(Directory[Model]):
    """Provides a collection of methods related to building models."""

    _data_model = Model

    def get(self, model_id: str) -> Model:
        """[Do not use] Get a model by project ID.

        Args:
            model_id: ID of the model.
        """

        raise NotImplementedError("The method 'get' of the class Model is not implemented yet.")

    def build(
        self,
        configuration: ModelConfiguration,
        dismiss_data_with_fields_discrepancies: bool = False,
        dismiss_data_with_volume_overflow: bool = False,
    ):
        """Launches a build given a configuration.

        Args:
            configuration: a ModelConfiguration object that contains the properties to be used in the build
            dismiss_data_with_fields_discrepancies: set to True for omitting data with missing properties
            dismiss_data_with_volume_overflow: set to True for omitting data outside the Domain of Analysis

        Example:
            Use a previous configuration for a new build in the same project

            .. code-block:: python

                a_project = simai.projects.get("project_A")

                build_conf = a_project.last_model_configuration

                new_model = simai.models.build(build_conf)

            Use a previous configuration for a new build in another project

            .. code-block:: python

                a_project = simai.projects.get("project_A")

                build_conf = a_project.last_model_configuration

                b_project = simai.projects.get("project_B")

                # set the id of b_project as the project_id of the configuration
                builf_conf.project_id = b_project.id

                new_model = simai.models.build(build_conf)

        """

        project_id = configuration.project.id
        return self._model_from(
            self._client._api.launch_build(
                project_id,
                configuration.to_payload(),
                dismiss_data_with_fields_discrepancies,
                dismiss_data_with_volume_overflow,
            )
        )

    @property
    def model_input(self) -> ModelInput:
        """Returns an empty ModelInput object."""
        return ModelInput()

    @property
    def model_output(self) -> ModelOutput:
        """Empty ModelOutput object."""
        return ModelOutput()

    @property
    def model_configuration(self) -> ModelConfiguration:
        """Empty ModelConfiguration object."""
        return ModelConfiguration()

    def global_coefficient(self, formula: str, name: str) -> GcField:
        """Empty GlobalCoefficient object."""
        return GcField(formula, name)
