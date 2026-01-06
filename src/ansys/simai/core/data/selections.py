# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from typing import Dict, List, Optional, Union

from ansys.simai.core.data.geometries import Geometry
from ansys.simai.core.data.predictions import Prediction
from ansys.simai.core.data.selection_post_processings import SelectionPostProcessingsMethods
from ansys.simai.core.data.types import (
    BoundaryConditions,
    Scalars,
    are_scalars_equal,
    is_scalars,
)
from ansys.simai.core.errors import _foreach_despite_errors
from ansys.simai.core.utils.numerical import (
    DEFAULT_COMPARISON_EPSILON,
    validate_tolerance_parameter,
)
from ansys.simai.core.utils.validation import _enforce_as_list_passing_predicate

logger = logging.getLogger(__name__)


class Point:
    """Provides a ``Point`` object, where a prediction can be run.

    A point is at the intersection of a :class:`~ansys.simai.core.data.geometries.Geometry`
    isstance and :class:`~ansys.simai.core.data.types.Scalars` instance.
    """

    def __init__(
        self,
        geometry: Geometry,
        scalars: Optional[Scalars] = None,
        boundary_conditions: Optional[BoundaryConditions] = None,
    ):
        # DEPRECATED
        if scalars is None and boundary_conditions is None:
            raise ValueError("Provide either 'scalars' or 'boundary_conditions'")
        if boundary_conditions is not None:
            logger.warning(
                "The 'boundary_conditions' parameter is deprecated and will be removed in a future release. Please use the 'scalars' parameter instead."
            )

        self._geometry = geometry
        self._scalars = scalars or boundary_conditions
        self._prediction: Optional[Prediction] = None

    @property
    def geometry(self) -> Geometry:
        """:class:`~ansys.simai.core.data.geometries.Geometry` object for the :class:`Point` instance."""
        return self._geometry

    @property
    def boundary_conditions(self) -> Scalars:
        """**(Deprecated)** :class:`~ansys.simai.core.data.types.BoundaryConditions` object for the :class:`Point`
        instance.
        """
        logger.warning(
            "'boundary_conditions' is deprecated and will be removed in a future release. Please use 'scalars' instead."
        )
        return self._scalars

    @property
    def scalars(self) -> Scalars:
        """:class:`~ansys.simai.core.data.types.Scalars` object for the :class:`Point`
        instance.
        """
        return self._scalars

    @property
    def prediction(self) -> Union[Prediction, None]:
        """:class:`~ansys.simai.core.data.predictions.Prediction` instance
        corresponding to the point or ``None`` if no prediction has yet been run.
        """
        return self._prediction

    def run_prediction(
        self,
        scalars: Optional[Scalars] = None,
        boundary_conditions: Optional[BoundaryConditions] = None,
    ):
        """Run the prediction on the geometry for this scalar."""
        if boundary_conditions is not None:
            logger.warning(
                "The 'boundary_conditions' parameter is deprecated and will be removed in a future release. Please use the 'scalars' parameter instead."
            )
            scalars = boundary_conditions

        if scalars is None and boundary_conditions is None:
            raise ValueError("Provide either 'scalars' or 'boundary_conditions'")
        self._prediction = self._geometry.run_prediction(scalars=scalars)

    def __repr__(self):
        return "{}(geometry: {}, scalar: {}, prediction: {})".format(
            self.__class__, self._geometry, self._scalars, self.prediction
        )


class Selection:
    """Provides a ``Selection`` object, which is a collection of :class:`Points <Point>` instances.

    Selections are built from a list of :class:`Geometries <ansys.simai.core.data.geometries.Geometry>`
    instances and a list of :class:`~ansys.simai.core.data.types.Scalars` instances.

    The resulting selection contains all combinations between the geometries
    and the scalars.

    Args:
        geometries: Geometries to include in the selection.
        scalars: Scalars to include in the selection.
        tolerance: Optional delta to apply to scalar equality.
                The default is ``10**-6``. If the difference between two boundary
                conditions is lower than the tolerance, the two scalars
                are considered as equal.
    """

    def __init__(
        self,
        geometries: Union[Geometry, List[Geometry]],
        scalars: Optional[Union[Scalars, List[Scalars]]] = None,
        tolerance: Optional[float] = None,
        boundary_conditions: Optional[Union[Scalars, List[Scalars]]] = None,
    ):
        # DEPRECATED
        if scalars is None and boundary_conditions is None:
            raise ValueError("Provide either 'scalars' or 'boundary_conditions'")
        if boundary_conditions is not None:
            logger.warning(
                "The 'boundary_conditions' parameter is deprecated and will be removed in a future release. Please use the 'scalars' parameter instead."
            )
            scalars = boundary_conditions

        # Validate parameters
        geometries = _enforce_as_list_passing_predicate(
            geometries,
            lambda g: isinstance(g, Geometry),
            "'geometries' must be a geometry or a list of 'Geometry' objects.",
        )
        scalars = _enforce_as_list_passing_predicate(
            scalars,
            lambda bc: is_scalars(bc),
            "'scalars' must be a dictionary of numbers.",
        )
        if tolerance is None:
            tolerance = DEFAULT_COMPARISON_EPSILON
        validate_tolerance_parameter(tolerance)
        self.tolerance = tolerance

        points = []
        for geometry in geometries:
            for scalar in scalars:
                points.append(Point(geometry, scalar))
        self._geometries = geometries
        self._scalars = scalars
        self._points = points
        self._post_processings = SelectionPostProcessingsMethods(self)
        self.reload()

    @property
    def points(self) -> List[Point]:
        """List of all :class:`Points <Point>` instances in the selection."""
        return self._points

    @property
    def predictions(self) -> List[Prediction]:
        """List of all existing :class:`Prediction <ansys.simai.core.data.predictions.Prediction>`
        instances in the selection.
        """
        return self.get_predictions()

    @property
    def geometries(self) -> List[Geometry]:
        """List of all existing :class:`Geometries <ansys.simai.core.data.geometries.Geometry>`
        instances in the selection.
        """
        return self._geometries

    @property
    def boundary_conditions(self) -> List[Scalars]:
        """**(Deprecated)** List of all existing :class:`Boundary conditions <ansys.simai.core.data.types.BoundaryConditions>`
        instances in the selection.
        """
        logger.warning(
            "'boundary_conditions' is deprecated and will be removed in a future release. Please use 'scalars' instead."
        )
        return self._scalars

    @property
    def scalars(self) -> List[Scalars]:
        """List of all existing :class:`Scalars <ansys.simai.core.data.types.Scalars>`
        instances in the selection.
        """
        return self._scalars

    @property
    def points_with_prediction(self) -> List[Optional[Point]]:
        """List of all :class:`Points <Point>` instances in the selection where predictions exist."""
        return [(point if point.prediction else None) for point in self.points]

    @property
    def points_without_prediction(self) -> List[Optional[Point]]:
        """List of all :class:`Points <Point>` instances in the selection where predictions don't exist."""
        return [(point if point.prediction is None else None) for point in self.points]

    def get_predictions(self) -> List[Prediction]:  # noqa D102
        return [point.prediction for point in self.points if point.prediction is not None]

    def get_runnable_predictions(self) -> List[Point]:
        """List of all :class:`Points <Point>` instances in the selection where predictions haven't
        been run yet.
        """
        return [point for point in self.points if point.prediction is None]

    def run_predictions(self) -> None:
        """Run all missing predictions in the selection."""
        _foreach_despite_errors(
            lambda point: point.run_prediction(scalars=point.scalars),
            self.get_runnable_predictions(),
        )

    def wait(self) -> None:
        """Wait for all ongoing operations (predictions and postprocessings)
        in the selection to finish.

        Raises:
            ansys.simai.core.errors.SimAIError: If a single error occurred when computing this selection's operations.
            ansys.simai.core.errors.MultipleErrors: If multiple exceptions occurred when computing this selection's operations.
        """
        _foreach_despite_errors(lambda prediction: prediction._wait_all(), self.get_predictions())

    def reload(self) -> None:
        """Refreshes the predictions in the selection.

        This method loads any predictions run from another session and
        removes possible deleted predictions.
        """
        _predictions_by_geometry_id: Dict[str, List[Prediction]] = {}
        for point in self.points:
            geometry = point.geometry
            if geometry.id not in _predictions_by_geometry_id:
                _predictions_by_geometry_id[geometry.id] = geometry.get_predictions()
            predictions = _predictions_by_geometry_id[geometry.id]

            try:
                point._prediction = next(
                    (
                        s
                        for s in predictions
                        if are_scalars_equal(
                            s.scalars,
                            point.scalars,
                            self.tolerance,
                        )
                    )
                )
            except StopIteration:
                point._prediction = None

    @property
    def post(self) -> SelectionPostProcessingsMethods:
        """Namespace containing methods to access and run postprocessings
        for the predictions in the selection.

        For more information, see the :py:class:`~ansys.simai.core.data.selection_post_processings.SelectionPostProcessingsMethods`
        class.

        """
        return self._post_processings
