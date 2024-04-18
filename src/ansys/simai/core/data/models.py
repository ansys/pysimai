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
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, PositiveFloat, ValidationError, model_validator

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.errors import InvalidArguments


class DomainAxisDefinition(BaseModel):
    """Representation of an axis in Domain of Analysis.

    Args:
        position: indicates the position of the anchor.

                    | *relative_to_min*: it corresponds to `VolXmin = xmin - value`

                    | *relative_to_max*: it corresponds to `VolXmax = xmax + value`

                    | *relative_to_center*: it corresponds to `(xmin+xmax)/2 - value`

                    | *absolute*: it corresponds to `VolXmin = value`

        value:      the distance of the anchor from the position. When position is set to
                    "absolute", value could be either positive or negative. Only positive
                    values are accepted in any other case.
        length:     the length of the Domain of Analysis along the axis.

    """

    position: Literal["relative_to_min", "relative_to_max", "relative_to_center", "absolute"]
    value: float
    length: PositiveFloat

    @model_validator(mode="after")
    def chek_value(self):
        """Evaluates that the value is set correctly according to the position argument."""
        if self.value < 0 and self.position != "absolute":
            raise InvalidArguments(
                "value should be a positive number when the position is not absolute"
            )
        return self


@dataclass
class DomainOfAnalysis:
    """Definition of the Domain of Analysis.

    Args:
        Length: the definition of the Domain of Analysis along the X axis
        Width: the definition of the Domain of Analysis along the Y axis
        Height: the definition of the Domain of Analysis along the Z axis
    """

    Length: DomainAxisDefinition = None
    Width: DomainAxisDefinition = None
    Height: DomainAxisDefinition = None


@dataclass
class ModelConfiguration:
    """The configuration for building a model."""

    boundary_conditions: Dict[str, Any] = None
    build_preset: str = None
    continuous: bool = False
    fields: Dict[str, Any] = None
    global_coefficients: List[Dict[str, Any]] = None
    simulation_volume: Dict[str, Any] = None
    project_id: str = None

    @property
    def domain_of_analysis(self) -> DomainOfAnalysis | None:
        """The Domain of Analysis of the model configuration."""
        if not self.simulation_volume:
            return None

        doa = DomainOfAnalysis()

        doa.Length = self._get_doa_axis("X")
        doa.Width = self._get_doa_axis("Y")
        doa.Height = self._get_doa_axis("Z")

        return doa

    @domain_of_analysis.setter
    def domain_of_analysis(self, doa: DomainOfAnalysis):
        """Sets the Domain of Analysis in the configuration."""

        if self.simulation_volume is None:
            self.simulation_volume = {}

        self.simulation_volume["X"] = self._set_doa_axis(doa.Length, "Length")
        self.simulation_volume["Y"] = self._set_doa_axis(doa.Width, "Width")
        self.simulation_volume["Z"] = self._set_doa_axis(doa.Height, "Height")

    def _get_doa_axis(self, rel_pos: str) -> DomainAxisDefinition:
        pos = self.simulation_volume.get(rel_pos)
        return DomainAxisDefinition(position=pos["type"], value=pos["value"], length=pos["length"])

    def _set_doa_axis(self, fld: DomainAxisDefinition, param: str) -> Dict[str, Any]:
        """Serializes a DomainAxisDefinition to the required format for the server."""
        if fld is None:
            raise InvalidArguments(
                f"Empty parameter {param} found when setting the Domain of Analysis. All the parameters should be filled in."
            )
        return {"length": fld.length, "type": fld.position, "value": fld.value}


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
        build_conf = asdict(configuration)
        project_id = build_conf.pop("project_id")
        return self._model_from(
            self._client._api.launch_build(
                project_id,
                build_conf,
                dismiss_data_with_fields_discrepancies,
                dismiss_data_with_volume_overflow,
            )
        )

    def doa_axis_definition(
        self, position: str, value: float, length: PositiveFloat
    ) -> DomainAxisDefinition:
        """Sets an axis in the Domain of Analysis.

        Returns:
            a :class:`DomainAxisDefinition <DomainAxisDefinition>` object.

        Raises:
            `ansys.simai.core.errors.InvalidArguments`: when the arguments are not compatible with the definition of an axis of the Domain of Analysis.

        """
        try:
            return DomainAxisDefinition(position=position, value=value, length=length)
        except ValidationError as pydandic_exc:
            raise InvalidArguments(pydandic_exc) from None

    def domain_of_analysis(self):
        """An empty :class:`DomainOfAnalysis <DomainOfAnalysis>` object."""
        return DomainOfAnalysis()
