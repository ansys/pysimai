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
    """Provides a ``Point`` object, where a prediction can be run.

    A point is at the intersection of a :class:`~ansys.simai.core.data.geometries.Geometry`
    isstance and :class:`~ansys.simai.core.data.types.BoundaryConditions` instance.
    """

    def __init__(self, geometry: Geometry, boundary_conditions: BoundaryConditions):
        self._geometry = geometry
        self._boundary_conditions = boundary_conditions
        self._prediction: Optional[Prediction] = None

    @property
    def geometry(self) -> Geometry:
        """:class:`~ansys.simai.core.data.geometries.Geometry` object for the :class:`Point` instance."""
        return self._geometry

    @property
    def boundary_conditions(self) -> BoundaryConditions:
        """:class:`~ansys.simai.core.data.types.BoundaryConditions` object for the :class:`Point`
        instance.
        """
        return self._boundary_conditions

    @property
    def prediction(self) -> Union[Prediction, None]:
        """:class:`~ansys.simai.core.data.predictions.Prediction` instance
        corresponding to the point or ``None`` if no prediction has yet been run.
        """
        return self._prediction

    def run_prediction(self, boundary_conditions: BoundaryConditions):
        """Run the prediction on the geometry for this boundary condition."""
        self._prediction = self._geometry.run_prediction(boundary_conditions=boundary_conditions)

    def __repr__(self):
        return "{}(geometry: {}, boundary_condition: {}, prediction: {})".format(
            self.__class__, self._geometry, self._boundary_conditions, self.prediction
        )


class Selection:
    """Provides a ``Selection`` object, which is a collection of :class:`Points <Point>` instances.

    Selections are built from a list of :class:`Geometries <ansys.simai.core.data.geometries.Geometry>`
    instances and a list of :class:`~ansys.simai.core.data.types.BoundaryConditions` instances.

    The resulting selection contains all combinations between the geometries
    and the boundary conditions.

    Args:
        geometries: Geometries to include in the selection.
        boundary_conditions: Boundary conditions to include in the selection.
        tolerance: Optional delta to apply to boundary condition equality.
                The default is ``10**-6``. If the difference between two boundary
                conditions is lower than the tolerance, the two boundary conditions
                are considered as equal.
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
            "'geometries' must be a geometry or a list of 'Geometry' objects.",
        )
        boundary_conditions = _enforce_as_list_passing_predicate(
            boundary_conditions,
            lambda bc: is_boundary_conditions(bc),
            "'boundary_conditions' must be a dictionary of numbers.",
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
    def boundary_conditions(self) -> List[BoundaryConditions]:
        """List of all existing :class:`BoundaryConditions <ansys.simai.core.data.types.BoundaryConditions>`
        instances in the selection.
        """
        return self._boundary_conditions

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
            lambda point: point.run_prediction(boundary_conditions=point.boundary_conditions),
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
        """Namespace containing methods to access and run postprocessings
        for the predictions in the selection.

        For more information, see the :py:class:`~ansys.simai.core.data.selection_post_processings.SelectionPostProcessingsMethods`
        class.

        """
        return self._post_processings
