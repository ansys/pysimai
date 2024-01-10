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
from typing import Any, Dict, List, Optional

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.geometries import Geometry
from ansys.simai.core.data.post_processings import PredictionPostProcessings
from ansys.simai.core.data.types import (
    BoundaryConditions,
    Identifiable,
    build_boundary_conditions,
    get_id_from_identifiable,
)
from ansys.simai.core.data.workspaces import Workspace

logger = logging.getLogger(__name__)


class Prediction(ComputableDataModel):
    """Provides the local representation of a prediction object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._post_processings = PredictionPostProcessings(self)
        self._geometry = None

    @property
    def geometry_id(self) -> str:
        """ID of the parent geometry.

        See Also:
            - :attr:`geometry`: Get the parent geometry.
        """
        return self.fields["geometry_id"]

    @property
    def geometry(self) -> Geometry:
        """Parent geometry.

        The parent geometry is queried if is not already known by the current
        SimAI client session.

        See Also:
            - :attr:`geometry_id`: Get the parent geometry's ID without query.
        """
        if self._geometry is None:
            if self.geometry_id in self._client.geometries._registry:
                self._geometry = self._client.geometries._registry[self.geometry_id]
            else:
                self._geometry = self._client.geometries.get(id=self.geometry_id)
        return self._geometry

    @property
    def boundary_conditions(self) -> BoundaryConditions:
        """Boundary conditions of the prediction."""
        return self.fields["boundary_conditions"]

    @property
    def post(self) -> PredictionPostProcessings:
        """Namespace containing methods for postprocessing the result of a prediction.

        For more information, see the :py:class:`~ansys.simai.core.data.post_processings.PredictionPostProcessings`
        class.
        """
        return self._post_processings

    @property
    def confidence_score(self) -> str:
        """Confidence score, which is either ``high`` or ``low``.

        This method blocks until the confidence score is computed.
        """
        self.wait()
        return self.fields["confidence_score"]

    def delete(self) -> None:
        """Remove a prediction from the server."""
        self._client._api.delete_prediction(self.id)
        self._unregister()

    def _wait_all(self):
        """Wait until both this prediction and any postprocessing launched on it
        have finished processing.

        This method blocks until both the prediction and any postprocessing launched
        locally have either finished processing or have failed.

        Postprocessing launched by other SimAI client sessions or on the front-end
        are not waited upon.
        """
        # wait for own creation Event
        logger.debug("prediction: waiting for own loading")
        super().wait()
        if self.has_failed:
            return
        # Wait for its post-processings if any
        if self.post._local_post_processings:
            logger.debug("prediction: waiting for postprocessings loading")
            for post_processing in self.post._local_post_processings:
                post_processing.wait()

    def _merge_fields_from_results(self, results: dict):
        super()._merge_fields_from_results(results)

        # confidence_score is in result/data/values
        values = results.get("data", {}).get("values", {})
        if "confidence_score" in values:
            self.fields["confidence_score"] = values["confidence_score"]


class PredictionDirectory(Directory[Prediction]):
    """Provides a collection of methods related to model predictions.

    This method is accessed through ``client.prediction``.

    Example:
        .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.predictions.list()
    """

    _data_model = Prediction

    @property
    def boundary_conditions(self) -> Dict[str, Any]:
        """Information on the boundary conditions expected by the model of the current workspace.
        For example, the prediction's input.
        """
        return self._client.current_workspace.model.boundary_conditions

    @property
    def physical_quantities(self) -> Dict[str, Any]:
        """Information on the physical quantities generated by the model. For example, the
        prediction's output.
        """
        return self._client.current_workspace.model.physical_quantities

    @property
    def info(self):
        """Information on the prediction's inputs and outputs.

        Example:
            .. code-block:: python

                from pprint import pprint
                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                prediction_info = simai.predictions.info
                pprint(prediction_info)
        """
        return {
            "boundary_conditions": self.boundary_conditions,
            "physical_quantities": self.physical_quantities,
        }

    def list(self, workspace: Optional[Identifiable[Workspace]] = None) -> List[Prediction]:
        """List all predictions on the server that belong to the specified workspace or the configured one.

        Args:
            workspace: ID or :class:`model <.workspaces.Workspace>` of the workspace to list the predictions for.
                This parameter is necessary if no workspace is set for the client.
        """
        return [
            self._model_from(prediction)
            for prediction in self._client._api.predictions(
                get_id_from_identifiable(workspace, default=self._client.current_workspace)
            )
        ]

    def get(self, id: str) -> Prediction:
        """Get a specific prediction object from the server by ID.

        Args:
            id: ID of the prediction.

        Returns:
            :class:`Prediction` instance with the given ID if it exists.

        Raises:
            :class:`NotFoundError`: No prediction with the given ID exists.
        """
        return self._model_from(self._client._api.get_prediction(id))

    def delete(self, prediction: Identifiable[Prediction]) -> None:
        """Delete a specific prediction from the server.

        Args:
            prediction: ID or :class:`model <Prediction>` of the prediction.

        Raises:
            :py:class:`ansys.simai.core.errors.NotFoundError`: No prediction with the given ID exists.
        """
        prediction_id = get_id_from_identifiable(prediction)
        self._client._api.delete_prediction(prediction_id)
        self._unregister_item_with_id(prediction_id)

    def run(  # noqa: D417
        self,
        geometry: Identifiable[Geometry],
        boundary_conditions: Optional[BoundaryConditions] = None,
        **kwargs,
    ) -> Prediction:
        """Run a prediction on a given geometry with a given boundary conditions.

        Boundary conditions can be passed as a dictionary or as kwargs.

        To learn more about the expected boundary conditions in your workspace, you can use the
        ``simai.current_workspace.model.boundary_conditions`` or ``simai.predictions.boundary_conditions``
        method, where ``ex`` is your `~ansys.simai.core.client.SimAIClient` object.

        Args:
            geometry: ID or :class:`model <.geometries.Geometry>` of the target geometry.
            boundary_conditions: Boundary conditions to apply in dictionary form.

        Returns:
            Created prediction object.

        Raises:
            ProcessingError: If the server failed to process the request.

        Examples:
            .. code-block:: python

                simai = ansys.simai.core.from_config()
                geometry = simai.geometries.list()[0]
                prediction = simai.predictions.run(geometry, dict(Vx=10.5, Vy=2))

            Using kwargs:

            .. code-block:: python

                prediction = simai.predictions.run(geometry_id, Vx=10.5, Vy=2)
        """
        bc = build_boundary_conditions(boundary_conditions, **kwargs)
        geometry = self._client.geometries.get(id=get_id_from_identifiable(geometry))
        prediction = geometry.run_prediction(boundary_conditions=bc)
        for location, warning_message in prediction.fields.get("warnings", {}).items():
            logger.warning(f"{location}: {warning_message}")
        return prediction
