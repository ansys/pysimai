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
from typing import Callable, Dict, List, Optional, Tuple

from tqdm import tqdm
from wakepy import keep

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.geometries import Geometry
from ansys.simai.core.data.types import Identifiable, NamedFile, get_id_from_identifiable
from ansys.simai.core.data.workspaces import Workspace
from ansys.simai.core.errors import InvalidArguments

logger = logging.getLogger(__name__)


class Optimization(ComputableDataModel):
    """Provides the local representation of an optimization definition object."""

    def _try_geometry(
        self, geometry: Identifiable[Geometry], geometry_parameters: Dict
    ) -> "OptimizationTrialRun":
        return self._client._optimization_trial_run_directory.try_geometry(
            self.id, geometry, geometry_parameters
        )


class OptimizationTrialRun(ComputableDataModel):
    """Provides the local representation of an optimization trial run object.

    The optimization trial run is an iteration of the optimization process.
    Each trial run tests a geometry and returns new parameters for the next geometry to try.
    """


class OptimizationDirectory(Directory[Optimization]):
    """Provides a collection of methods related to optimizations.

    This class is accessed through ``client.optimizations``.

    Example:
        .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.optimizations.run(...)
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

    def run(
        self,
        geometry_generation_fn: Callable[..., NamedFile],
        geometry_parameters: Dict[str, Tuple[float, float]],
        boundary_conditions: Dict[str, float],
        n_iters: int,
        minimize: Optional[List[str]] = None,
        maximize: Optional[List[str]] = None,
        outcome_constraints: Optional[List[str]] = None,
        show_progress: bool = False,
        workspace: Optional[Identifiable[Workspace]] = None,
    ) -> List[Dict]:
        """Run an optimization process.

        Args:
            geometry_generation_fn: Function to call to generate a new geometry
                with the generated parameters. This parameter should return a
                :obj:`~ansys.simai.core.data.types.NamedFile` object.
            geometry_parameters: Name of the geometry parameters and their bounds or possible values (choices).
            boundary_conditions: Values of the boundary conditions to perform the optimization at.
                The values should map to existing boundary conditions in your project/workspace.
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

            n_iters: Number of iterations of the optimization loop.
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

            results = simai.optimizations.run(
                geometry_generation_fn=my_geometry_generation_function,
                geometry_parameters={
                    "param_a": {"bounds": (-12.5, 12.5)},
                    "param_b": {"choices": (0, 1)},
                },
                minimize=["TotalForceX"],
                boundary_conditions={"VelocityX": 10.5},
                outcome_constraints=["TotalForceX <= 10"],
                n_iters=100,
            )

            print(results)
        """
        workspace_id = get_id_from_identifiable(workspace, False, self._client._current_workspace)
        if not minimize and not maximize:
            raise InvalidArguments("No global coefficient to optimize.")
        objective = {}
        if minimize:
            for global_coefficient in minimize:
                objective[global_coefficient] = {"minimize": True}
        if maximize:
            for global_coefficient in maximize:
                objective[global_coefficient] = {"minimize": False}
        optimization_parameters = {
            "boundary_conditions": boundary_conditions,
            "geometry_parameters": geometry_parameters,
            "n_iters": n_iters,
            "objective": objective,
            "outcome_constraints": outcome_constraints or [],
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
            with keep.running() as k:
                if not k.success:
                    logger.info("Failed to get sleep inhibition lock.")
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
                    trial_run = optimization.try_geometry(geometry, geometry_parameters)
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


# Undocumented for now, users don't really need to interact with it
class OptimizationTrialRunDirectory(Directory[OptimizationTrialRun]):
    _data_model = OptimizationTrialRun

    def get(self, trial_run_id: str):
        """Get a specific trial run from the server."""
        return self._model_from(self._client._api.get_optimization_trial_run(trial_run_id))

    def _try_geometry(
        self,
        optimization: Identifiable[Optimization],
        geometry: Identifiable[Geometry],
        geometry_parameters: Dict,
    ) -> OptimizationTrialRun:
        geometry_id = get_id_from_identifiable(geometry)
        optimization_id = get_id_from_identifiable(optimization)
        return self._model_from(
            self._client._api.run_optimization_trial(
                optimization_id, geometry_id, geometry_parameters
            )
        )
