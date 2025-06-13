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
from inspect import signature
from typing import Callable, Dict, List, Literal, Optional, Tuple

from tqdm import tqdm
from wakepy import keep

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.geometries import Geometry
from ansys.simai.core.data.types import (
    Identifiable,
    NamedFile,
    get_id_from_identifiable,
    get_object_from_identifiable,
)
from ansys.simai.core.data.workspaces import Workspace
from ansys.simai.core.errors import InvalidArguments

logger = logging.getLogger(__name__)


class _OptimizationTrialRun(ComputableDataModel):
    """Provides the local representation of an optimization trial run object.

    The optimization trial run is an iteration of the optimization process.
    Each trial run tests a geometry and returns new parameters for the next geometry to try.
    """


# Undocumented for now, users don't really need to interact with it
class _OptimizationTrialRunDirectory(Directory[_OptimizationTrialRun]):
    _data_model = _OptimizationTrialRun

    def get(self, trial_run_id: str):
        """Get a specific trial run from the server."""
        return self._model_from(self._client._api.get_optimization_trial_run(trial_run_id))

    def _run_iteration(
        self, optimization: Identifiable["Optimization"], parameters: Dict
    ) -> _OptimizationTrialRun:
        optimization_id = get_id_from_identifiable(optimization)
        return self._model_from(
            self._client._api.run_optimization_trial(optimization_id, parameters)
        )


class Optimization(ComputableDataModel):
    """Provides the local representation of an optimization definition object."""

    def _run_iteration(self, parameters: Dict) -> "_OptimizationTrialRun":
        return self._client._optimization_trial_run_directory._run_iteration(self.id, parameters)


class OptimizationDirectory(Directory[Optimization]):
    """Provides a collection of methods related to optimizations.

    This class is accessed through ``client.optimizations``.

    Example:
        .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.optimizations.run_parametric(
                ...
            )  # or simai.optimizations.run_non_parametric(...)
    """

    _data_model = Optimization

    def get(self, optimization_id: str) -> Optimization:
        """Get a specific optimization object from the server.

        Args:
            optimization_id: ID of the optimization.

        Returns:
            :py:class:`Optimization`.
        """
        return self._model_from(self._client._api.get_optimization(optimization_id))

    def run_parametric(
        self,
        geometry_generation_fn: Callable[..., NamedFile],
        geometry_parameters: Dict[str, Tuple[float, float]],
        n_iters: int,
        boundary_conditions: Optional[Dict[str, float]] = None,
        minimize: Optional[List[str]] = None,
        maximize: Optional[List[str]] = None,
        outcome_constraints: Optional[List[str]] = None,
        show_progress: bool = False,
        workspace: Optional[Identifiable[Workspace]] = None,
    ) -> List[Dict]:
        """Run an optimization loop with client-side parametric geometry generation.

        Args:
            geometry_generation_fn: Function to call to generate a new geometry
                with the generated parameters. This parameter should return a
                :obj:`~ansys.simai.core.data.types.NamedFile` object.
            geometry_parameters: Name of the geometry parameters and their bounds or possible values (choices).
            boundary_conditions: Values of the boundary conditions to perform the optimization at.
                The values should map to existing boundary conditions in your project/workspace.
            n_iters: Number of iterations of the optimization loop.
            minimize: List of global coefficients to minimize.
                The global coefficients should map to existing coefficients in your project/workspace.
            maximize: List of global coefficients to maximize.
                The global coefficients should map to existing coefficients in your project/workspace.
            outcome_constraints: List of strings representing a linear inequality constraint
                on a global coefficient. The outcome constraint should be in the form ``gc >= x``,
                where:

                - ``gc`` is a valid global coefficient name.
                - ``x`` is a float bound.
                - The comparison operator is ``>=`` or ``<=``.

            show_progress: Whether to print progress on stdout.
            workspace: Workspace to run the optimization in. If a workspace is
                not specified, the default is the configured workspace.

        Returns:
            List of dictionaries representing the result of each iteration. when constraints
            are specified, the list can be shorter than the number of iterations.

        Warning:
            This is a long-running process and your computer must be powered on to generate the iterations.
            This method attempts to prevent your computer from sleeping, keeping your computer open
            during the process.

        Example:
          .. code-block:: python

            import ansys.simai.core


            # Function takes the parameters
            def my_geometry_generation_function(param_a, param_b):
                # Implementation
                return "/path/to/generated/geometry.stl"


            simai = ansys.simai.core.from_config(workspace="optimization-workspace")

            simai.optimizations.run_parametric(
                geometry_generation_fn=my_geometry_generation_function,
                geometry_parameters={
                    "param_a": {"bounds": (-12.5, 12.5)},
                    "param_b": {"choices": (0, 1)},
                },
                minimize=["TotalForceX"],
                boundary_conditions={"VelocityX": 10.5},
                outcome_constraints=["TotalForceY <= 10"],
                n_iters=100,
            )
        """
        workspace_id = get_id_from_identifiable(workspace, True, self._client._current_workspace)
        outcome_constraints = outcome_constraints or []
        _validate_n_iters(n_iters)
        _validate_geometry_parameters(geometry_parameters)
        _validate_geometry_generation_fn_signature(geometry_generation_fn, geometry_parameters)
        _validate_outcome_constraints(outcome_constraints)
        objective = _build_objective(minimize, maximize)
        optimization_parameters = {
            "boundary_conditions": boundary_conditions or {},
            "n_iters": n_iters,
            "objective": objective,
            "type": "parametric",
            "outcome_constraints": outcome_constraints,
            "geometry_generation": {
                "geometry_parameters": geometry_parameters,
            },
        }
        with tqdm(total=n_iters, disable=not show_progress) as progress_bar:
            progress_bar.set_description("Creating optimization definition.")
            optimization = self._model_from(
                self._client._api.define_optimization(workspace_id, optimization_parameters)
            )
            optimization.wait()
            geometry_parameters = optimization.fields["initial_geometry_parameters"]
            logger.debug("Optimization defined. Starting optimization loop.")
            iterations_results: List[Dict] = []
            with keep.running(on_fail="warn"):
                while geometry_parameters:
                    logger.debug(f"Generating geometry with parameters {geometry_parameters}.")
                    progress_bar.set_description("Generating geometry.")
                    # TODO: Somehow keep session alive for long geometry generation
                    generated_geometry = geometry_generation_fn(**geometry_parameters)
                    logger.debug("Uploading geometry.")
                    progress_bar.set_description("Uploading geometry.")
                    # TODO: Name geometry ourselves ? Then we need to know the output format
                    geometry = self._client.geometries.upload(
                        generated_geometry,
                        metadata=geometry_parameters,
                        workspace_id=workspace_id,
                    )
                    logger.debug("Running trial.")
                    progress_bar.set_description("Running trial.")
                    trial_run = optimization._run_iteration(
                        {"geometry": geometry.id, "geometry_parameters": geometry_parameters}
                    )
                    trial_run.wait()
                    iteration_result = {
                        "parameters": geometry_parameters,
                        "objective": trial_run.fields["outcome_values"],
                    }
                    progress_bar.set_postfix(**iteration_result)
                    if trial_run.fields.get("is_feasible", True):
                        iterations_results.append(iteration_result)
                    else:
                        logger.debug("Trial run results did not match constraints. Skipping.")
                    geometry_parameters = trial_run.fields["next_geometry_parameters"]
                    logger.debug("Trial complete.")
                    progress_bar.update(1)
                logger.debug("Optimization complete.")
                progress_bar.set_description("Optimization complete.")
            return iterations_results

    def run_non_parametric(
        self,
        geometry: Identifiable[Geometry],
        bounding_boxes: List[List[float]],
        symmetries: List[Literal["x", "y", "z", "X", "Y", "Z"]],
        n_iters: int,
        boundary_conditions: Optional[Dict[str, float]] = None,
        minimize: Optional[List[str]] = None,
        maximize: Optional[List[str]] = None,
        max_displacement: Optional[List[float]] = None,
        show_progress: bool = False,
    ):
        """Run an optimization loop with server-side geometry generation using automorphism.

        Args:
            geometry: The base geometry on which to perform the automorphism. The optimization will
                run in the same workspace as the geometry.
            bounding_boxes: list of the bounds of the different boxes that will define the locations
                of the geometry to optimize.
                The format is [
                [box1_xmin, box1_xmax, box1_ymin, box1_ymax, box1_zmin, box1_zmax],
                [box2_xmin, box2_xmax, box2_ymin, box2_ymax, box2_zmin, box2_zmax],
                ...
                ]
            symmetries: list of symmetry axes, axes being x, y or z
            boundary_conditions: Values of the boundary conditions to perform the optimization at.
                The values should map to existing boundary conditions in your project/workspace.
            n_iters: Number of iterations of the optimization loop.
            minimize: List of global coefficients to minimize.
                The global coefficients should map to existing coefficients in your project/workspace.
            maximize: List of global coefficients to maximize.
                The global coefficients should map to existing coefficients in your project/workspace.
            max_displacement: User-defined constraint on the maximum allowable deformation of the initial mesh in non-parametric optimization.
                It is specified as a list (max_displacement) matching the number of bounding boxes (box_bounds_list). Each value limits the displacement within the corresponding bounding box, using the same metric as the bounding box coordinates.
            show_progress: Whether to print progress on stdout.

        Warning:
            This feature is in beta. Results are not guaranteed.

        Example:
          .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config(workspace="optimization-workspace")
            geometry = simai.geometries.list()[0]

            simai.optimizations.run_non_parametric(
                geometry,
                bounding_boxes=[[0, 1, 0, 1, 0, 1]],
                boundary_conditions={"VelocityX": 10.5},
                symmetries=["y"],
                n_iters=10,
                minimize=["TotalForceX"],
                show_progress=True,
            )
        """
        _validate_n_iters(n_iters)
        _validate_global_coefficients_for_non_parametric(minimize, maximize)
        _validate_bounding_boxes(bounding_boxes)
        _validate_max_displacement(max_displacement, bounding_boxes)
        geometry = get_object_from_identifiable(geometry, self._client._geometry_directory)
        objective = _build_objective(minimize, maximize)
        optimization_parameters = {
            "boundary_conditions": boundary_conditions or {},
            "n_iters": n_iters,
            "objective": objective,
            "type": "non_parametric",
            "geometry_generation": {
                "geometry": geometry.id,
                "box_bounds_list": bounding_boxes,
                "symmetries": symmetries,
                "max_displacement": max_displacement,
            },
        }
        with tqdm(total=n_iters, disable=not show_progress) as progress_bar:
            progress_bar.set_description("Creating optimization definition.")
            optimization = self._model_from(
                self._client._api.define_optimization(
                    geometry._fields["workspace_id"], optimization_parameters
                )
            )
            optimization.wait()
            logger.debug("Optimization defined. Starting optimization loop.")
            iterations_results: List[Dict] = []
            with keep.running(on_fail="warn"):
                for _ in range(n_iters):
                    logger.debug("Running iteration")
                    progress_bar.set_description("Running iteration")
                    trial_run = optimization._run_iteration({})
                    trial_run.wait()
                    iteration_result = {
                        "objective": trial_run.fields["outcome_values"],
                    }
                    progress_bar.set_postfix(**iteration_result)
                    if trial_run.fields.get("is_feasible", True):
                        iterations_results.append(iteration_result)
                    else:
                        logger.debug("Trial run results did not match constraints. Skipping.")
                    logger.debug("Trial complete.")
                    progress_bar.update(1)
                logger.debug("Optimization complete.")
                progress_bar.set_description("Optimization complete.")
            return iterations_results


def _validate_geometry_parameters(params: Dict):
    if not isinstance(params, Dict):
        raise InvalidArguments("geometry_parameters: must be a dict.")
    if not params:
        raise InvalidArguments("geometry_parameters: must not be empty.")
    for key, value in params.items():
        bounds = value.get("bounds")
        choices = value.get("choices")
        if not bounds and not choices:
            raise InvalidArguments(f"geometry_parameters: no bounds or choices specified for {key}")
        if bounds and choices:
            raise InvalidArguments(
                f"geometry_parameters: only one of bounds or choices must be specified for {key}"
            )


def _validate_geometry_generation_fn_signature(geometry_generation_fn, geometry_parameters):
    geometry_generation_fn_args = signature(geometry_generation_fn).parameters
    if geometry_generation_fn_args.keys() != geometry_parameters.keys():
        raise InvalidArguments(
            f"geometry_generation_fn requires the following signature: {list(geometry_parameters.keys())}, but got: {list(geometry_generation_fn_args.keys())}"
        )


def _validate_bounding_boxes(bounding_boxes: list[list[float]]) -> None:
    if not isinstance(bounding_boxes, list) or not bounding_boxes:
        raise InvalidArguments("bounding_boxes must be a non-empty list.")

    for i, box in enumerate(bounding_boxes):
        if not isinstance(box, list) or len(box) != 6:
            raise InvalidArguments(
                f"Bounding box at index {i} should be a list of 6 values "
                f"[xmin, xmax, ymin, ymax, zmin, zmax]."
            )

        if not all(isinstance(value, (int, float)) for value in box):
            raise InvalidArguments(f"Bounding box at index {i} contains non-numeric values.")

        dimensions = ("x", "y", "z")
        for j in range(3):
            min_index = j * 2
            max_index = min_index + 1
            if not (box[min_index] < box[max_index]):
                raise InvalidArguments(
                    f"Bounding box at index {i}: {dimensions[j]}min ({box[min_index]}) "
                    f"must be less than {dimensions[j]}max ({box[max_index]})."
                )


def _validate_global_coefficients_for_non_parametric(minimize: List[str], maximize: List[str]):
    if minimize and maximize:
        raise InvalidArguments(
            "Only one of minimize or maximize can be provided for non parametric optimization."
        )

    active_list = minimize if minimize else maximize
    if not isinstance(active_list, list) or (
        isinstance(active_list, list) and len(active_list) != 1
    ):
        raise InvalidArguments(
            "minimize or maximize must be a list of one string for non parametric optimization."
        )


def _validate_outcome_constraints(outcome_constraints: list) -> None:
    if not isinstance(outcome_constraints, list):
        raise InvalidArguments("outcome_constraints must be a list")

    for i, constraint in enumerate(outcome_constraints):
        if not isinstance(constraint, str):
            raise InvalidArguments(f"Constraint at index {i} must be a string")

        # Check if constraint contains either >= or <=
        if ">=" in constraint:
            operator = ">="
        elif "<=" in constraint:
            operator = "<="
        else:
            raise InvalidArguments(
                f"Constraint at index {i} ({constraint}) must contain either >= or <= operator"
            )

        parts = constraint.split(operator)
        if len(parts) != 2:
            raise InvalidArguments(
                f"Constraint at index {i} ({constraint}) must be of form 'metric_name {operator} value'"
            )

        metric_name = parts[0].strip()
        value = parts[1].strip()

        if not metric_name:
            raise InvalidArguments(
                f"Constraint at index {i} ({constraint}) must have a metric name"
            )

        try:
            float(value)
        except ValueError as error:
            raise InvalidArguments(
                f"Constraint at index {i} ({constraint}): '{value}' must be a numeric value"
            ) from error


def _validate_n_iters(n_iters) -> None:
    if not isinstance(n_iters, int):
        raise InvalidArguments("n_iters must be an integer")

    if n_iters <= 0:
        raise InvalidArguments("n_iters must be strictly positive")


def _validate_max_displacement(
    max_displacement: Optional[List[float]], bounding_boxes: List[List[float]]
) -> None:
    if max_displacement is None:
        return

    if not isinstance(max_displacement, list):
        raise InvalidArguments("max_displacement must be a list")

    if not all(isinstance(value, (int, float)) for value in max_displacement):
        raise InvalidArguments("max_displacement contains non-numeric values")

    if len(max_displacement) != len(bounding_boxes):
        raise InvalidArguments(
            "Max displacement list and bounding boxes list must have the same number of items"
        )


def _build_objective(minimize: list[str], maximize: list[str]) -> dict:
    if not minimize and not maximize:
        raise InvalidArguments("No global coefficient to optimize.")
    objective = {}
    if minimize:
        for global_coefficient in minimize:
            objective[global_coefficient] = {"minimize": True}
    if maximize:
        for global_coefficient in maximize:
            objective[global_coefficient] = {"minimize": False}
    return objective
