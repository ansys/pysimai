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

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Optional

from ansys.simai.core.errors import InvalidArguments, ProcessingError

if TYPE_CHECKING:
    from ansys.simai.core.data.projects import Project


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
class GlobalCoefficientDefinition:
    """Global coefficient definition/parameter field.

    Args:
        formula: Global Coefficient formula.
        name: Global Coefficient name.
    """

    formula: str
    name: str


@dataclass
class ModelInput:
    """Model inputs.

    Args:
        surface: Input surface variables.
        boundary_conditions: Boundary conditions.
    """

    surface: list[str] = None
    boundary_conditions: list[str] = None


@dataclass
class ModelOutput:
    """The outputs of a model.

    Args:
        surface: the output surface variables.
        volume: the output volume variables.
    """

    surface: list[str] = None
    volume: list[str] = None


@dataclass
class ModelConfiguration:
    """Configures the build of a model.

    Args:
        project: the project of the configuration.
        build_preset: indicates the build duration. Available options:

                    | *debug*: < 30 min, only 4 dat

                    | *short*: < 24 hours

                    | *default*: < 2 days, default value.

                    | *long*: < 1 week
        continuous: indicates if continuous learning is enabled. Default is False.
        input: the inputs of the model.
        output: the outputs of the model.
        global_coefficients: the Global Coefficients of the model.
        domain_of_analysis: The Domain of Analysis of the model configuration.

    Example:
        Define a new configuration and launch a build.

        .. code-block:: python

            import ansys.simai.core as asc
            from ansys.simai.core.data.model_configuration import (
                DomainAxisDefinition,
                DomainOfAnalysis,
                ModelConfiguration,
                ModelInput,
                ModelOutput,
            )

            simai = asc.from_config()

            # Get the project of interest
            aero_dyn_project = simai.projects.get(name="aero-dyn")

            # Define the inputs of the model
            model_input = ModelInput(surface=["Velocity"], boundary_conditions=["Vx"])

            # Define the outputs of the model
            model_output = ModelOutput(
                surface=["Pressure", "WallShearStress_0"], volume=["Velocity_0", "Pressure"]
            )

            # Define the model coefficients
            global_coefficients = [("max(Pressure)", "maxpress")]

            # Set the Domain of Analysis
            doa = DomainOfAnalysis(
                length=("relative_to_max", 5, 8.1),
                width=("relative_to_max", 5, 8.1),
                height=("absolute", -4.5, 0.1),
            )

            # Define the build configuration for the model
            new_conf = ModelConfiguration(
                project=aero_dyn_project,
                build_preset="debug",
                continuous=False,
                input=model_input,
                output=model_output,
                global_coefficients=global_coefficients,
                domain_of_analysis=doa,
            )

            # Launch a mode build with the new configuration
            new_model = simai.models.build(new_conf)
    """

    project: "Optional[Project]" = None
    build_preset: Literal[
        "debug",
        "short",
        "default",
        "long",
    ] = "default"
    continuous: bool = False
    input: ModelInput = field(default_factory=lambda: ModelInput())
    output: ModelOutput = field(default_factory=lambda: ModelOutput())
    domain_of_analysis: DomainOfAnalysis = field(default_factory=lambda: DomainOfAnalysis())

    def __set_gc(self, gcs: list[GlobalCoefficientDefinition]):
        verified_gcs = []

        for gc in gcs:
            gc_unit = GlobalCoefficientDefinition(*gc) if isinstance(gc, tuple) else gc
            if self.project is None:
                raise ProcessingError(
                    f"{self.__class__.__name__}: a project must be defined for setting global coefficients."
                ) from None

            self.project.verify_gc_formula(
                gc_unit.formula, self.input.boundary_conditions, self.output.surface
            )
            verified_gcs.append(gc_unit)
        self.__dict__["global_coefficients"] = verified_gcs

    def __get_gc(self):
        return self.__dict__.get("global_coefficients")

    global_coefficients: list[GlobalCoefficientDefinition] = property(__get_gc, __set_gc)

    def __init__(
        self,
        project: "Project",
        boundary_conditions: Optional[dict[str, Any]] = None,
        build_preset: Optional[str] = None,
        continuous: bool = False,
        fields: Optional[dict[str, Any]] = None,
        global_coefficients: Optional[list[GlobalCoefficientDefinition]] = None,
        simulation_volume: Optional[dict[str, Any]] = None,
        input: Optional[ModelInput] = None,
        output: Optional[ModelOutput] = None,
        domain_of_analysis: Optional[DomainOfAnalysis] = None,
        surface_pp_input: Optional[list] = None,
    ):
        """Sets the properties of a build configuration."""
        if surface_pp_input is None:
            surface_pp_input = []
        self.project = project
        self.input = ModelInput()
        if input is not None:
            self.input = input
        self.output = ModelOutput()
        if output is not None:
            self.output = output
        if boundary_conditions is not None and self.input.boundary_conditions is None:
            self.input.boundary_conditions = list(boundary_conditions.keys())
        self.build_preset = build_preset
        self.continuous = continuous
        self.surface_pp_input = surface_pp_input
        if fields is not None:
            if fields.get("surface_input"):
                self.input.surface = [fd.get("name") for fd in fields["surface_input"]]

            if fields.get("surface"):
                self.output.surface = [fd.get("name") for fd in fields["surface"]]

            if fields.get("volume"):
                self.output.volume = [fd.get("name") for fd in fields["volume"]]

            self.surface_pp_input = fields.get("surface_pp_input", [])

        self.domain_of_analysis = domain_of_analysis
        if simulation_volume is not None:
            self.domain_of_analysis = DomainOfAnalysis(
                length=self._get_doa_axis(simulation_volume, "X"),
                width=self._get_doa_axis(simulation_volume, "Y"),
                height=self._get_doa_axis(simulation_volume, "Z"),
            )

        if global_coefficients is not None:
            gcs = [
                GlobalCoefficientDefinition(**gc) if isinstance(gc, dict) else gc
                for gc in global_coefficients
            ]
            self.global_coefficients = gcs

    def _get_doa_axis(self, sim_vol: dict, rel_pos: str) -> DomainAxisDefinition:
        """Composes a DomainAxisDefinition from raw json."""
        pos = sim_vol.get(rel_pos)
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

        bcs = {}
        if self.input.boundary_conditions is not None:
            bcs = {bc_name: {} for bc_name in self.input.boundary_conditions}

        sample_metadata = self.project.sample.fields.get("extracted_metadata")

        surface_input_fld = []
        if self.input.surface is not None:
            surface_input_fld = [
                fd
                for fd in sample_metadata.get("surface").get("fields")
                if fd.get("name") in self.input.surface
            ]

        surface_fld = []
        if self.output.surface is not None:
            surface_fld = [
                fd
                for fd in sample_metadata.get("surface").get("fields")
                if fd.get("name") in self.output.surface
            ]

        volume_fld = []
        if self.output.volume is not None:
            volume_fld = [
                fd
                for fd in sample_metadata.get("volume").get("fields")
                if fd.get("name") in self.output.volume
            ]

        gcs = []
        if self.global_coefficients is not None:
            gcs = [asdict(gc) for gc in self.global_coefficients]

        flds = {
            "surface": surface_fld,
            "surface_input": surface_input_fld,
            "volume": volume_fld,
            "surface_pp_input": self.surface_pp_input if self.surface_pp_input else [],
        }

        simulation_volume = {
            "X": self._set_doa_axis(self.domain_of_analysis.length, "length"),
            "Y": self._set_doa_axis(self.domain_of_analysis.width, "width"),
            "Z": self._set_doa_axis(self.domain_of_analysis.height, "height"),
        }

        return {
            "boundary_conditions": bcs,
            "build_preset": self.build_preset,
            "continuous": self.continuous,
            "fields": flds,
            "global_coefficients": gcs,
            "simulation_volume": simulation_volume,
        }

    def compute_global_coefficient(self):
        """Computes the results of the formula for all global coefficients with respect to the project's sample."""

        if self.project is None:
            raise ProcessingError(
                f"{self.__class__.__name__}: a project must be a defined for computing the global coefficient formula."
            ) from None

        return [
            self.project.compute_gc_formula(
                gc.formula, self.input.boundary_conditions, self.output.surface
            )
            for gc in self.global_coefficients
        ]
