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
from typing import TYPE_CHECKING, Any, Literal, Optional

if TYPE_CHECKING:
    from ansys.simai.core.data.projects import Project


@dataclass
class GlobalCoefficientUnit:
    """Single Global Coefficient field.

    Args:
        formula: the Global Coefficient formula.
        name: the name of the Global Coefficient.
    """

    formula: str
    name: str


@dataclass
class ModelInput:
    """The inputs of a model.

    Args:
        surface: the input surface variables.
        boundary_conditions: the boundary conditions.
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

                    | *debug*: < 30 min

                    | *short*: < 24 hours

                    | *default*: < 2 days, default value.

                    | *long*: < 1 week
        continuous: indicates if continuous learning is enabled. Default is False.
        input: the inputs of the model.
        output: the outputs of the model.
        global_coefficients: the Global Coefficients of the model.

    Example:
        Define a new configuration and launch a build.

        .. code-block:: python

            import ansys.simai.core as asc
            from ansys.simai.core.data.model_configuration import (
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

            # Define the model coefficient
            global_coefficients = [("max(Pressure)", "maxpress")]

            # Define the build configuration for the model
            new_conf = ModelConfiguration(
                project=aero_dyn_project,
                build_preset="debug",
                continuous=False,
                input=model_input,
                output=model_output,
                global_coefficients=global_coefficients,
                simulation_volume=simulation_volume,
            )

            # Launch a mode build with the new configuration
            new_model = simai.models.build(new_conf)
    """

    project: "Project" = None
    build_preset: Literal[
        "debug",
        "short",
        "default",
        "long",
    ] = "default"
    continuous: bool = False
    input: ModelInput = ModelInput()
    output: ModelOutput = ModelOutput()

    def __set_gc(self, gcs: list[tuple | GlobalCoefficientUnit]):
        verified_gcs = []
        for gc in gcs:
            gc_unit = GlobalCoefficientUnit(*gc) if isinstance(gc, tuple) else gc
            self.project.verify_gc_formula(
                gc_unit.formula, self.input.boundary_conditions, self.output.surface
            )
            verified_gcs += [gc_unit]
        self.__dict__["global_coefficients"] = verified_gcs

    def __get_gc(self):
        return self.__dict__.get("global_coefficients")

    global_coefficients: ModelOutput = property(__get_gc, __set_gc)

    def __init__(
        self,
        boundary_conditions: Optional[dict[str, Any]] = None,
        build_preset: Optional[str] = None,
        continuous: Optional[bool] = False,
        fields: Optional[dict[str, Any]] = None,
        global_coefficients: Optional[dict[dict[str, Any]] | GlobalCoefficientUnit] = None,
        simulation_volume: Optional[dict[str, Any]] = None,
        project: Optional["Project"] = None,
        input: Optional[ModelInput] = None,
        output: Optional[ModelOutput] = None,
    ):
        """Sets the properties of a build configuration."""
        self.project = project
        if boundary_conditions is not None:
            self.input.boundary_conditions = list(boundary_conditions.keys())
        self.build_preset = build_preset
        self.continuous = continuous
        if fields is not None:
            if fields.get("surface_input"):
                self.input.surface = [fd.get("name") for fd in fields["surface_input"]]

            if fields.get("surface"):
                self.output.surface = [fd.get("name") for fd in fields["surface"]]

            if fields.get("volume"):
                self.output.volume = [fd.get("name") for fd in fields["volume"]]

        self.simulation_volume = simulation_volume
        if global_coefficients is not None:
            gcs = [
                GlobalCoefficientUnit(**gc) if isinstance(gc, dict) else gc
                for gc in global_coefficients
            ]
            self.global_coefficients = gcs
        if input is not None:
            self.input = input
        if output is not None:
            self.output = output

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
        }
        return {
            "boundary_conditions": bcs,
            "build_preset": self.build_preset,
            "continuous": self.continuous,
            "fields": flds,
            "global_coefficients": gcs,
            "simulation_volume": self.simulation_volume,
        }

    def compute_global_coefficient(self):
        """Computes the results of the formula for all Global Coefficients with respect to the project's sample."""

        return [
            self.project.compute_gc_formula(
                gc.formula, self.input.boundary_conditions, self.output.surface
            )
            for gc in self.output.global_coefficients
        ]
