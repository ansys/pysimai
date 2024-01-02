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

import json

import pytest
import responses

from ansys.simai.core.data.selections import Selection
from ansys.simai.core.errors import MultipleErrors


@pytest.fixture()
def four_geometries_test_set(geometry_factory, prediction_factory):
    """A list of 4 geometries with xbow in [21, 23, 25, 27]"""
    geometries = []
    for i in [21, 23, 25, 27]:
        if i == 21:
            predictions = [
                prediction_factory(id="pred19.8", boundary_conditions={"Vx": 19.8}),
                prediction_factory(id="pred20.2", boundary_conditions={"Vx": 20.2}),
                prediction_factory(id="pred20.5", boundary_conditions={"Vx": 20.5}),
            ]
        else:
            predictions = []
        geometry = geometry_factory(id=f"xbow-{i}", predictions=predictions, metadata={"xbow": i})
        geometries.append(geometry)
    yield geometries


def test_selection_content(four_geometries_test_set):
    """WHEN creating a Selection from a list of geometries and boundary conditions
    THEN the selection contains all geometry—boundary-condition combinations
    """
    speeds = [20.2, 20.4, 20.6]
    boundary_conditions = [{"Vx": v} for v in speeds]
    selection = Selection(four_geometries_test_set, boundary_conditions)
    # 4 geometries * 3 boundary conditions
    points = selection.points
    assert len(points) == 12

    received_xbow_speed_combinations = {
        (p.geometry.metadata["xbow"], p.boundary_conditions["Vx"]) for p in points
    }
    expected_combinations = set()
    for speed in speeds:
        for xbow in [21, 23, 25, 27]:
            expected_combinations.add((xbow, speed))
    assert received_xbow_speed_combinations == expected_combinations


def test_selection_get_predictions(four_geometries_test_set):
    """WHEN accessing the selection's predictions
    THEN predictions existing for the geometry­—boundary-condition couple are returned
    """
    boundary_conditions = [{"Vx": v} for v in [20.2, 20.4, 20.6]]
    selection = Selection(four_geometries_test_set, boundary_conditions)

    predictions = selection.get_predictions()
    assert len(predictions) == 1
    assert predictions[0].id == "pred20.2"

    points_with_prediction = [p for p in selection.points if p.prediction is not None]
    assert len(points_with_prediction) == 1
    point = points_with_prediction[0]
    assert point.geometry.id == "xbow-21"
    assert point.boundary_conditions == {"Vx": 20.2}


@responses.activate
def test_selection_run_predictions(geometry_factory, prediction_factory):
    """WHEN calling run_prediction() on a selection
    THEN a POST request is launched for each not-existing prediction
    AND after the call, selection.predictions contains values for
        all combinations of geometries and boundary condition
    """
    # We create 2 geometries, geom 77777 having 1 prediction, geom 88888 having none
    geometries = [
        geometry_factory(
            id="77777",
            predictions=[prediction_factory(id="k6k6k6", boundary_conditions={"Vx": 4.5})],
        ),
        geometry_factory(id="88888", predictions=[]),
    ]

    # Select 3 speeds
    interesting_speeds_x = {4.5, 5.5, 6.5}
    boundary_conditions = [{"Vx": v} for v in interesting_speeds_x]

    selection = Selection(geometries, boundary_conditions)

    # Selection contains 6 points (2 geom * 2 BC)
    assert len(selection.points) == 6
    # Selection contains only 1 prediction (geom 0001 - speed 4.5)
    assert len(selection.predictions) == 1
    assert selection.predictions[0].boundary_conditions["Vx"] == 4.5
    assert len(selection.get_runnable_predictions()) == 5

    # Endpoints for prediction creations
    def geometry1_pred_request_callback(request):
        payload = json.loads(request.body)
        boundary_conditions = payload["boundary_conditions"]
        # geometry1 had a pred for speed 4.5, it should not be recreated
        assert boundary_conditions["Vx"] in {5.5, 6.5}
        return (
            200,
            {},
            json.dumps(
                {
                    "id": f"pred{boundary_conditions}",
                    "status": "queued",
                    "boundary_conditions": boundary_conditions,
                }
            ),
        )

    def geometry2_pred_request_callback(request):
        payload = json.loads(request.body)
        boundary_conditions = payload["boundary_conditions"]
        # geometry2 had no pred, preds for all speed will be created
        assert boundary_conditions["Vx"] in {4.5, 5.5, 6.5}
        return (
            200,
            {},
            json.dumps(
                {
                    "id": f"pred{boundary_conditions}",
                    "status": "queued",
                    "boundary_conditions": boundary_conditions,
                }
            ),
        )

    responses.add_callback(
        responses.POST,
        "https://test.test/geometries/77777/predictions",
        callback=geometry1_pred_request_callback,
    )
    responses.add_callback(
        responses.POST,
        "https://test.test/geometries/88888/predictions",
        callback=geometry2_pred_request_callback,
    )

    # Let's run all predictions in the selection
    selection.run_predictions()

    # Now selection contains 6 predictions, for both geometries and all expected speeds
    assert len(selection.points) == 6
    assert len(selection.predictions) == 6

    expected_combinations = set()
    for geom in geometries:
        for speed_x in interesting_speeds_x:
            expected_combinations.add((geom.id, speed_x))
    received_combinations = {
        (p.geometry.id, p.boundary_conditions["Vx"])
        for p in selection.points_with_prediction
        if p is not None
    }
    assert expected_combinations == received_combinations

    assert len(selection.get_runnable_predictions()) == 0


def test_selection_tolerance(geometry_factory, prediction_factory):
    """WHEN creating a selection with the default tolerance
    THEN an prediction with a boundary condition differing from less than
        10**-6 is included in the selection
    """
    small_epsilon = 10**-8
    big_epsilon = 10**-5
    geometry = geometry_factory(
        predictions=[
            prediction_factory(id="here-i-am", boundary_conditions={"Vx": 11 + small_epsilon}),
            prediction_factory(id="i-am-not", boundary_conditions={"Vx": 11 + big_epsilon}),
        ],
    )
    boundary_conditions = [{"Vx": 11}, {"Vx": 12}]

    selection = Selection([geometry], boundary_conditions)
    predictions = selection.get_predictions()
    assert len(predictions) == 1
    assert predictions[0].id == "here-i-am"


@responses.activate
def test_selection_run_prediction_error(geometry_factory):
    """WHEN calling run_predictions, and some calls return an error
    THEN all the predictions are ran nevertheless
    AND at the end a MultipleErrors is raised
    """
    geometry = geometry_factory()
    speeds = [-11, -10, -9]
    selection = Selection([geometry], [{"Vx": v} for v in speeds])

    nb_calls = 0

    def pred_creation_callback(request):
        nonlocal nb_calls
        nb_calls += 1
        payload = json.loads(request.body)
        boundary_conditions = payload["boundary_conditions"]
        # send 422 error for the first 2 calls, 200 for the last one
        if nb_calls < 3:
            return (
                422,
                {},
                json.dumps(
                    {
                        "code": 422,
                        "errors": {"json": {"speed": "Planets are not aligned"}},
                        "status": "Stellar Entity",
                    }
                ),
            )
        else:
            return (
                200,
                {},
                json.dumps(
                    {
                        "id": "saturn",
                        "status": "queued",
                        "boundary_conditions": boundary_conditions,
                    }
                ),
            )

    responses.add_callback(
        responses.POST,
        f"https://test.test/geometries/{geometry.id}/predictions",
        callback=pred_creation_callback,
    )

    with pytest.raises(MultipleErrors):
        selection.run_predictions()

    # assert 3 calls have been made despite the first two having failed
    assert len(responses.calls) == 3
    assert len(selection.predictions) == 1
    assert selection.predictions[0].id == "saturn"


def test_selection_parameters(four_geometries_test_set):
    """WHEN creating a Selection
    IF I don't pass a Geometry or list thereof, and a BoundaryCondition or list thereof
    THEN a TypeError is raised
    """

    boundary_conditions = [{"Vx": v} for v in [-11.9, -5, 0, 50, 900.4]]

    Selection(four_geometries_test_set, boundary_conditions)
    Selection(four_geometries_test_set[0], boundary_conditions)
    Selection(four_geometries_test_set, boundary_conditions[0])
    Selection(four_geometries_test_set[0], boundary_conditions[0])
    Selection(four_geometries_test_set, {"Vx": 1})

    with pytest.raises(TypeError):
        Selection(boundary_conditions, four_geometries_test_set)
    with pytest.raises(TypeError):
        Selection(None, boundary_conditions)
    with pytest.raises(TypeError):
        Selection(12.5, boundary_conditions)

    with pytest.raises(TypeError):
        Selection(four_geometries_test_set, [{"Vx": "a", "Vy": "b", "Vz": "c"}])
    with pytest.raises(TypeError):
        Selection(four_geometries_test_set, [(1, 0, 0, 0)])

    with pytest.raises(TypeError):
        Selection(four_geometries_test_set, 1)
    with pytest.raises(TypeError):
        Selection(four_geometries_test_set, 1, 0, 0)
    with pytest.raises(TypeError):
        Selection(four_geometries_test_set, boundary_conditions, tolerance="")
    with pytest.raises(ValueError):
        Selection(four_geometries_test_set, boundary_conditions, tolerance=-10)
