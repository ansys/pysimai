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

from typing import Dict, List, Optional, Union

from ansys.simai.core.data.geometries import Geometry
from ansys.simai.core.data.predictions import Prediction
from ansys.simai.core.data.selection_post_processings import SelectionPostProcessingsMethods
from ansys.simai.core.data.types import (
    BoundaryConditions,
    are_boundary_conditions_equal,
    is_boundary_conditions,
)
from ansys.simai.core.errors import _foreach_despite_errors
from ansys.simai.core.utils.numerical import (
    DEFAULT_COMPARISON_EPSILON,
    validate_tolerance_parameter,
)
from ansys.simai.core.utils.validation import _enforce_as_list_passing_predicate


class Point:
    """A Point object, where a Prediction can be run.

    A Point is at the intersection of a :class:`~ansys.simai.core.data.geometries.Geometry` and :class:`~ansys.simai.core.data.types.BoundaryConditions`.
    """

    def __init__(self, geometry: Geometry, boundary_conditions: BoundaryConditions):
        self._geometry = geometry
        self._boundary_conditions = boundary_conditions
        self._prediction: Optional[Prediction] = None

    @property
    def geometry(self) -> Geometry:
        """Returns the :class:`~ansys.simai.core.data.geometries.Geometry` object for this :class:`Point`."""
        return self._geometry

    @property
    def boundary_conditions(self) -> BoundaryConditions:
        """Returns the :class:`~ansys.simai.core.data.types.BoundaryConditions` for this :class:`Point`."""
        return self._boundary_conditions

    @property
    def prediction(self) -> Union[Prediction, None]:
        """Returns the :class:`~ansys.simai.core.data.predictions.Prediction`
        corresponding to this Point, or None if no prediction has yet been ran.
        """
        return self._prediction

    def run_prediction(self, boundary_conditions: BoundaryConditions):
        """Runs the prediction on this Geometry for this boundary condition."""
        self._prediction = self._geometry.run_prediction(boundary_conditions=boundary_conditions)

    def __repr__(self):
        return "{}(geometry: {}, boundary_condition: {}, prediction: {})".format(
            self.__class__, self._geometry, self._boundary_conditions, self.prediction
        )


class Selection:
    """A Selection object, which is a collection of :class:`Points <Point>`.

    Selections are built from a list of :class:`Geometries <ansys.simai.core.data.geometries.Geometry>`
    and a list of :class:`~ansys.simai.core.data.types.BoundaryConditions`.

    The resulting Selection contains all combinations between the geometries
    and the boundary conditions.

    Args:
        geometries: the geometries to include in the selection
        boundary_conditions: the boundary conditions to include in the selection
        tolerance: Optional delta applied to boundary condition equality;
                if the difference between two boundary conditions
                is lower than tolerance, they are considered as equal
                (default 10**-6).
    """

    def __init__(
        self,
        geometries: Union[Geometry, List[Geometry]],
        boundary_conditions: Union[BoundaryConditions, List[BoundaryConditions]],
        tolerance: Optional[float] = None,
    ):
        # Validate parameters
        geometries = _enforce_as_list_passing_predicate(
            geometries,
            lambda g: isinstance(g, Geometry),
            "geometries must be a Geometry or a list of Geometry objects",
        )
        boundary_conditions = _enforce_as_list_passing_predicate(
            boundary_conditions,
            lambda bc: is_boundary_conditions(bc),
            "boundary_conditions must be a dict of numbers",
        )
        if tolerance is None:
            tolerance = DEFAULT_COMPARISON_EPSILON
        validate_tolerance_parameter(tolerance)
        self.tolerance = tolerance

        points = []
        for geometry in geometries:
            for boundary_condition in boundary_conditions:
                points.append(Point(geometry, boundary_condition))
        self._geometries = geometries
        self._boundary_conditions = boundary_conditions
        self._points = points
        self._post_processings = SelectionPostProcessingsMethods(self)
        self.reload()

    @property
    def points(self) -> List[Point]:
        """Returns a list of all the :class:`Points <Point>` composing this Selection."""
        return self._points

    @property
    def predictions(self) -> List[Prediction]:
        """Returns a list of all the existing :class:`Predictions <ansys.simai.core.data.predictions.Prediction>` in this selection."""
        return self.get_predictions()

    @property
    def geometries(self) -> List[Geometry]:
        """Returns a list of all the existing :class:`Geometries <ansys.simai.core.data.geometries.Geometry>` in this selection."""
        return self._geometries

    @property
    def boundary_conditions(self) -> List[BoundaryConditions]:
        """Returns a list of all the existing :class:`BoundaryConditions <ansys.simai.core.data.types.BoundaryConditions>` in this selection."""
        return self._boundary_conditions

    @property
    def points_with_prediction(self) -> List[Optional[Point]]:
        """Returns a list of all the points :class:`Points <Point>` in this selection for which a prediction exists."""
        return [(point if point.prediction else None) for point in self.points]

    @property
    def points_without_prediction(self) -> List[Optional[Point]]:
        """Returns a list of all the points :class:`Points <Point>` in this selection for which no prediction exists."""
        return [(point if point.prediction is None else None) for point in self.points]

    def get_predictions(self) -> List[Prediction]:  # noqa D102
        return [point.prediction for point in self.points if point.prediction is not None]

    def get_runnable_predictions(self) -> List[Point]:
        """Return a list of :class:`Points <Point>` in this selection
        for which predictions haven't been ran yet.
        """
        return [point for point in self.points if point.prediction is None]

    def run_predictions(self) -> None:
        """Run all the missing predictions in this selection."""
        _foreach_despite_errors(
            lambda point: point.run_prediction(boundary_conditions=point.boundary_conditions),
            self.get_runnable_predictions(),
        )

    def wait(self) -> None:
        """Wait for all the ongoing operations (predictions, post-processings)
        in this selection to finish.

        Raises:
            ansys.simai.core.errors.SimAIError: if a single error occurred during computing this selection's operations
            ansys.simai.core.errors.MultipleErrors: if multiple exceptions occurred when computing this selection's operations
        """
        _foreach_despite_errors(lambda prediction: prediction._wait_all(), self.get_predictions())

    def reload(self) -> None:
        """Refreshes the predictions in this selection.
        Loads any prediction ran from another session,
        or removes possible deleted predictions.
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
                        if are_boundary_conditions_equal(
                            s.boundary_conditions,
                            point.boundary_conditions,
                            self.tolerance,
                        )
                    )
                )
            except StopIteration:
                point._prediction = None

    @property
    def post(self) -> SelectionPostProcessingsMethods:
        """Namespace containing methods to access and run post-processings
        for predictions in this selection.

        See :py:class:`~ansys.simai.core.data.selection_post_processings.SelectionPostProcessingsMethods`
        for more information.
        """
        return self._post_processings
