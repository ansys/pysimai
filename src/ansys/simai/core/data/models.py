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

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.errors import InvalidArguments


@dataclass
class DomainAxisDefinition:
    """Defines an axis in the Domain of Analysis.

    Args:
        position: Anchor point position.

                    | *relative_to_min*: `VolXmin = xmin - value`

                    | *relative_to_max*: `VolXmax = xmax + value`

                    | *relative_to_center*: `(xmin+xmax)/2 - value`

                    | *absolute*: `VolXmin = value`

        value:      Distance of the anchor from the position.
                        When ``position=absolute``, the distance can be either positive or negative.
                        In any other case, only positive values are accepted.
        length:     Length of the Domain of Analysis along the axis. Only positive numbers are accepted.

    Example:
        Define the Z-axis(i.e., height) in a Domain of Analysis

        .. code-block:: python

            from ansys.simai.core.data.models import DomainAxisDefinition, DomainOfAnalysis

            # Get the last configuration from a project
            bld_conf = my_project.last_model_configuration

            # Define a new axis for the Domain of Analysis
            new_doa_height = DomainAxisDefinition("relative_to_min", 180.5, 99.1)

            # Assign the new Domain of Analysis to the configuration
            bld_conf.domain_of_analysis.height = new_doa_height

    """

    def __post_init__(self):
        """Assess whether the value and length are correctly set."""

        self.__validate_length(self.length)
        self.__validate_value(self.value)

    def __set_value(self, val: float):
        self.__validate_value(val)
        self.__dict__["value"] = val

    def __get_value(self):
        return self.__dict__.get("value")

    def __validate_value(self, val: float):
        if val < 0 and self.position != "absolute":
            raise InvalidArguments(
                f"{self.__class__.__name__}: 'value' must be a positive number when the position is not 'absolute'.",
            ) from None

    def __set_length(self, lgth: float):
        self.__validate_length(lgth)
        self.__dict__["length"] = lgth

    def __get_length(self):
        return self.__dict__.get("length")

    def __validate_length(self, lgth: float):
        if not lgth > 0:
            raise InvalidArguments(
                f"{self.__class__.__name__}: 'length' must be a positive number.",
            ) from None

    position: Literal["relative_to_min", "relative_to_max", "relative_to_center", "absolute"]
    value: float = property(__get_value, __set_value)
    length: float = property(__get_length, __set_length)

    del __set_length, __set_value, __get_length, __get_value


@dataclass
class DomainOfAnalysis:
    """Defines the Domain of Analysis.

    Args:
        length: Domain of Analysis along the X axis
        width: Domain of Analysis along the Y axis
        height: Domain of Analysis along the Z axis

    Example:
        Get the Domain of Analysis from a configuration and replace it with a new one

        .. code-block:: python

            from ansys.simai.core.data.models import DomainOfAnalysis

            # Get the last configuration from a project
            bld_conf = my_project.last_model_configuration

            # Define a new Domain of Analysis
            new_doa = DomainOfAnalysis(
                length=("relative_to_max", 5, 8.1),
                width=("relative_to_max", 5, 8.1),
                height=("absolute", -4.5, 0.1),
            )

            # Assign the new Domain of Analysis to the configuration
            bld_conf.domain_of_analysis = new_doa

    """

    length: DomainAxisDefinition = None
    width: DomainAxisDefinition = None
    height: DomainAxisDefinition = None

    def __post_init__(self):
        if isinstance(self.length, tuple):
            self.length = DomainAxisDefinition(*self.length)
        if isinstance(self.width, tuple):
            self.width = DomainAxisDefinition(*self.width)
        if isinstance(self.height, tuple):
            self.height = DomainAxisDefinition(*self.height)


@dataclass
class ModelConfiguration:
    """Configures the build of a model.

    Attributes:
        domain_of_analysis: The Domain of Analysis of the model configuration.

    Example:
        Define the Domain of Analsysin in a new model configuration

        .. code-block:: python

            from ansys.simai.core.data.models import (
                DomainAxisDefinition,
                DomainOfAnalysis,
                ModelConfiguration,
            )

            # Create an empty model configuration
            mdl_conf = ModelConfiguration()

            # Domain of Analysis parameters can be set one-by-one, as:
            # such as setting the length
            mdl_conf.domain_of_analysis.length = DomainAxisDefinition(
                "relative_to_min", 11155.5, 27.1
            )

            # Also, a Domain of Analysis can be assigned to the configuration at once
            mdl_conf.domain_of_analysis = DomainOfAnalysis(
                length=("relative_to_max", 5, 8.1),
                width=("relative_to_max", 5, 8.1),
                height=("absolute", -4.5, 0.1),
            )
    """

    domain_of_analysis: DomainOfAnalysis = field(default_factory=lambda: DomainOfAnalysis())

    def __init__(
        self,
        boundary_conditions: Optional[dict[str, Any]] = None,
        build_preset: Optional[str] = None,
        continuous: Optional[bool] = False,
        fields: Optional[dict[str, Any]] = None,
        global_coefficients: Optional[dict[dict[str, Any]]] = None,
        simulation_volume: Optional[dict[str, Any]] = None,
        project_id: Optional[str] = None,
        domain_of_analysis: Optional[DomainOfAnalysis] = None,
    ):
        """Sets the properties of a build configuration."""
        self.boundary_conditions = boundary_conditions
        self.build_preset = build_preset
        self.continuous = continuous
        self.__fields = fields
        self.global_coefficients = global_coefficients
        self.domain_of_analysis = domain_of_analysis
        if domain_of_analysis is not None and simulation_volume is not None:
            raise InvalidArguments(
                f"Either the 'domain_of_analysis' or the 'simulation_volume' parameter could be set in the {self.__class__.__name__} constructor."
            )
        self.__simulation_volume = simulation_volume
        if self.__simulation_volume is not None:
            self.domain_of_analysis = DomainOfAnalysis(
                length=self._get_doa_axis("X"),
                width=self._get_doa_axis("Y"),
                height=self._get_doa_axis("Z"),
            )

        self.project_id = project_id

    def _get_doa_axis(self, rel_pos: str) -> DomainAxisDefinition:
        """Composes a DomainAxisDefinition from raw json."""
        pos = self.__simulation_volume.get(rel_pos)
        return DomainAxisDefinition(position=pos["type"], value=pos["value"], length=pos["length"])

    def _set_doa_axis(self, fld: DomainAxisDefinition, param: str) -> dict[str, Any]:
        """Serializes a DomainAxisDefinition to the required format for the server."""
        if fld is None:
            raise InvalidArguments(
                f"Empty parameter '{param}' found when setting the Domain of Analysis. All parameters should be set."
            )
        return {"length": fld.length, "type": fld.position, "value": fld.value}

    def _to_payload(self):
        """Constracts the payload for a build request."""
        flds = {
            "surface": self.__fields.get("surface", []),
            "surface_input": self.__fields.get("surface_input", []),
            "volume": self.__fields.get("volume", []),
        }

        simulation_volume = {
            "X": self._set_doa_axis(self.domain_of_analysis.length, "length"),
            "Y": self._set_doa_axis(self.domain_of_analysis.width, "width"),
            "Z": self._set_doa_axis(self.domain_of_analysis.height, "height"),
        }

        return {
            "boundary_conditions": (self.boundary_conditions if self.boundary_conditions else {}),
            "build_preset": self.build_preset,
            "continuous": self.continuous,
            "fields": flds,
            "global_coefficients": (self.global_coefficients if self.global_coefficients else []),
            "simulation_volume": simulation_volume,
        }


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
        project_id = configuration.project_id
        return self._model_from(
            self._client._api.launch_build(
                project_id,
                configuration._to_payload(),
                dismiss_data_with_fields_discrepancies,
                dismiss_data_with_volume_overflow,
            )
        )
