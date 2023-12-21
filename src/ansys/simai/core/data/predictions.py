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
from ansys.simai.core.data.types import BoundaryConditions, build_boundary_conditions

logger = logging.getLogger(__name__)


class Prediction(ComputableDataModel):
    """
    Local representation of a prediction object.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._post_processings = PredictionPostProcessings(self)
        self._geometry = None

    @property
    def geometry_id(self) -> str:
        """
        The id of the parent geometry.

        See Also:
            - :attr:`geometry`: Get the parent geometry
        """
        return self.fields["geometry_id"]

    @property
    def geometry(self) -> Geometry:
        """
        The parent geometry.

        It will be queried if not already known by the current SDK session.

        See Also:
            - :attr:`geometry_id`: Return the parent geometry's id without query
        """
        if self._geometry is None:
            if self.geometry_id in self._client.geometries._registry:
                self._geometry = self._client.geometries._registry[self.geometry_id]
            else:
                self._geometry = self._client.geometries.get(id=self.geometry_id)
        return self._geometry

    @property
    def boundary_conditions(self) -> BoundaryConditions:
        """The boundary conditions of the prediction."""
        return self.fields["boundary_conditions"]

    @property
    def post(self) -> PredictionPostProcessings:
        """
        Namespace containing methods to post-process the result of a prediction.

        See :py:class:`~ansys.simai.core.data.post_processings.PredictionPostProcessings` for more information
        """
        return self._post_processings

    @property
    def confidence_score(self) -> str:
        """
        The confidence score. Either *high* or *low*.

        This method will block until the confidence score is computed.
        """
        self.wait()
        return self.fields["confidence_score"]

    def delete(self) -> None:
        """Remove a prediction from the server."""
        self._client._api.delete_prediction(self.id)
        self._unregister()

    def feedback(self, **kwargs):
        """
        Give us your feedback on a prediction to help us improve.

        This method enables you to give a rating (from 0 to 4) and a comment on a
        prediction.
        Moreover you can upload your computed solution.
        This feedback will help us make our predictions more accurate for you.

        Keyword Args:
            rating (int): A rating from 0 to 4
            comment (str): Additional comment
            solution (Optional[File]): Your solution to the
                prediction
        """
        self._client._api.send_prediction_feedback(self.id, **kwargs)

    def _wait_all(self):
        """
        Wait until both this prediction, and any post-processing launched on it
        have finished processing.

        Blocking method, which once called, blocks until both the prediction,
        and any post-processing launched locally, have either finished processing,
        or have failed.

        Post-processing launched by other SDK sessions or on the front-end
        are not waited upon.
        """
        # wait for own creation Event
        logger.debug("prediction: waiting for own loading")
        super().wait()
        if self.has_failed:
            return
        # Wait for its post-processings if any
        if self.post._local_post_processings:
            logger.debug("prediction: waiting for post-processings loading")
            for post_processing in self.post._local_post_processings:
                post_processing.wait()

    def _merge_fields_from_results(self, results: dict):
        super()._merge_fields_from_results(results)

        # confidence_score is in result/data/values
        values = results.get("data", {}).get("values", {})
        if "confidence_score" in values:
            self.fields["confidence_score"] = values["confidence_score"]


class PredictionDirectory(Directory[Prediction]):
    """
    Collection of methods related to model predictions

    Accessed through ``client.prediction``.

    Example:
        .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.predictions.list()
    """

    _data_model = Prediction

    @property
    def boundary_conditions(self) -> Dict[str, Any]:
        """Information on the boundary conditions expected by the model of the current workspace, i.e. the prediction's input."""
        return self._client.current_workspace.model.boundary_conditions

    @property
    def physical_quantities(self) -> Dict[str, Any]:
        """Information on the physical quantities generated by the model, i.e. the prediction's output."""
        return self._client.current_workspace.model.physical_quantities

    @property
    def info(self):
        """
        Information on the predictions inputs and outputs.

        Example:
            .. code-block:: python

                from pprint import pprint
                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                prediction_info = simai.predictions.info
                pprint(prediction_info)
        """
        return dict(
            boundary_conditions=self.boundary_conditions,
            physical_quantities=self.physical_quantities,
        )

    def list(self, workspace_id: Optional[str] = None) -> List[Prediction]:
        """
        List all predictions on the server that belong to the currently set workspace or the specified one.

        Args:
            workspace_id: The id of the workspace for which to list the predictions,
                only necessary if no workspace is set for the client.
        """
        if not workspace_id:
            workspace_id = self._client.current_workspace.id
        return [
            self._model_from(prediction)
            for prediction in self._client._api.predictions(workspace_id)
        ]

    def get(self, id: str) -> Prediction:
        """
        Get a specific prediction object from the server.

        Args:
            id: The id of the prediction to get

        Returns:
            The :py:class:`Prediction` with the given id if it exists

        Raises:
            :py:class:`NotFoundError`: No prediction with the given id exists
        """
        return self._model_from(self._client._api.get_prediction(id))

    def delete(self, prediction_id: str) -> None:
        """
        Delete a specific prediction from the server.

        Args:
            prediction_id: The id of the prediction to delete

        Raises:
            :py:class:`ansys.simai.core.errors.NotFoundError`: No prediction with the given id exists
        """
        self._client._api.delete_prediction(prediction_id)
        self._unregister_item_with_id(prediction_id)

    def run(
        self,
        geometry_id: str,
        boundary_conditions: Optional[BoundaryConditions] = {},
        **kwargs,
    ) -> Prediction:
        """
        Run a SimAI prediction on the given geometry with the given boundary conditions.

        Boundary conditions can be passed as a dictionary or as kwargs.

        To learn more about the expected boundary conditions in your workspace you can do
        ``simai.current_workspace.model.boundary_conditions`` or ``simai.predictions.boundary_conditions``
        where ``ex`` is your `~ansys.simai.core.client.SimAIClient` object.

        Args:
            geometry_id: The id of the target geometry
            boundary_conditions: The boundary conditions to apply, in dictionary form

        Returns:
            The created prediction object

        Raises:
            ProcessingError: If the server failed to process the request.

        Examples:
            .. code-block:: python

                simai = ansys.simai.core.from_config()
                geometry = simai.geometries.list()[0]
                prediction = simai.predictions.run(geometry.id, dict(Vx=10.5, Vy=2))

            Using kwargs:

            .. code-block:: python

                prediction = simai.predictions.run(geometry.id, Vx=10.5, Vy=2)
        """
        bc = build_boundary_conditions(boundary_conditions, **kwargs)
        geometry = self._client.geometries.get(id=geometry_id)
        prediction = geometry.run_prediction(boundary_conditions=bc)
        for location, warning_message in prediction.fields.get("warnings", {}).items():
            logger.warning(f"{location}: {warning_message}")
        return prediction

    def feedback(self, prediction_id: str, **kwargs) -> None:
        """
        Give us your feedback on a prediction to help us improve.

        This method enables you to give a rating (from 0 to 4) and a comment on a
        prediction.
        Moreover you can upload your computed solution.
        This feedback will help us make our predictions more accurate for you.

        Args:
            prediction_id: The id of the prediction.

        Keyword Args:
            rating (int): A rating from 0 to 4, required
            comment (str): Additional comment, required
            solution (typing.Optional[File]): Your solution to the
                prediction, optional
        """
        self._client._api.send_prediction_feedback(prediction_id, **kwargs)
