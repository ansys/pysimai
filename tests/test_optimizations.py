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
# ruff: noqa: E731

import json
import threading

import pytest
import responses
import sseclient

from ansys.simai.core.data.optimizations import (
    _validate_bounding_boxes,
    _validate_geometry_generation_fn_signature,
    _validate_global_coefficients_for_non_parametric,
    _validate_max_displacement,
    _validate_n_iters,
    _validate_outcome_constraints,
)
from ansys.simai.core.errors import InvalidArguments


def test_geometry_generation_fn_invalid_signature(simai_client):
    """WHEN a geometry_generation_fn signature does not match geometry_parameters keys
    THEN an InvalidArgument error is raised."""

    my_geometry_generation_function = lambda param_a: f"test_geometry/param_{param_a}.vtp"

    geometry_parameters = {
        "param_a": {"bounds": (-12.5, 12.5)},
        "param_ski": {"choices": (0.1, 1.0)},
    }

    with pytest.raises(InvalidArguments) as exc:
        simai_client.optimizations.run_parametric(
            geometry_generation_fn=my_geometry_generation_function,
            geometry_parameters=geometry_parameters,
            boundary_conditions={"abc": 3.0},
            n_iters=5,
        )

    assert "geometry_generation_fn requires the following signature" in str(exc.value)


def test_validate_geometry_generation_fn_valid_signature():
    """WHEN geometry_generation_fn signature matches geometry_parameters keys
    THEN check passes"""

    my_geometry_generation_function = (
        lambda param_c, param_d: f"test_geometry/param_{param_c}_{param_d}.vtp"
    )
    geometry_parameters = {"param_c": {"bounds": (-12.5, 12.5)}, "param_d": {"choices": (0.1, 1.0)}}

    _validate_geometry_generation_fn_signature(my_geometry_generation_function, geometry_parameters)


def test_validate_bounding_boxes_success():
    bounding_boxes = [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]]

    _validate_bounding_boxes(bounding_boxes)


@pytest.mark.parametrize(
    "bounding_boxes, error_message",
    [
        ([], "bounding_boxes must be a non-empty list"),
        ([[0.1, 0.1, 0.1, 0.1]], "Bounding box at index 0 should be a list of 6 values"),
        (
            [[0.1, "foo", 0.1, 0.2, 0.1, 0.2]],
            "Bounding box at index 0 contains non-numeric values.",
        ),
        (
            [[0.1, 0.1, 0.1, 0.2, 0.1, 0.2]],
            r"Bounding box at index 0: xmin \(0\.1\) must be less than xmax \(0\.1\)",
        ),
        (
            [[0.1, 0.2, 0.1, 0.1, 0.1, 0.2]],
            r"Bounding box at index 0: ymin \(0\.1\) must be less than ymax \(0\.1\)",
        ),
        (
            [[0.1, 0.2, 0.1, 0.2, 0.1, 0.1]],
            r"Bounding box at index 0: zmin \(0\.1\) must be less than zmax \(0\.1\)",
        ),
    ],
)
def test_validate_bounding_boxes_fails(bounding_boxes, error_message):
    with pytest.raises(
        expected_exception=InvalidArguments,
        match=error_message,
    ):
        _validate_bounding_boxes(bounding_boxes)


def test_validate_global_coefficients_for_non_parametric_success():
    # Test with minimize only
    _validate_global_coefficients_for_non_parametric(minimize=["TotalForceX"], maximize=[])

    # Test with maximize only
    _validate_global_coefficients_for_non_parametric(minimize=[], maximize=["TotalForceY"])


@pytest.mark.parametrize(
    "minimize, maximize, error_message",
    [
        (
            ["TotalForceX"],
            ["TotalForceY"],
            "Only one of minimize or maximize can be provided for non parametric optimization.",
        ),
        (
            [],
            [],
            "minimize or maximize must be a list of one string for non parametric optimization.",
        ),
        (
            ["TotalForceX", "Pressure"],
            [],
            "minimize or maximize must be a list of one string for non parametric optimization.",
        ),
        (
            None,
            None,
            "minimize or maximize must be a list.",
        ),
        (
            {},
            [],
            "minimize or maximize must be a list of one string for non parametric optimization.",
        ),
        (
            [],
            None,
            "minimize or maximize must be a list of one string for non parametric optimization.",
        ),
        (
            "string_instead_of_list",
            [],
            "minimize or maximize must be a list of one string for non parametric optimization.",
        ),
    ],
)
def test_validate_global_coefficients_for_non_parametric_fails(minimize, maximize, error_message):
    with pytest.raises(
        expected_exception=InvalidArguments,
        match=error_message,
    ):
        _validate_global_coefficients_for_non_parametric(minimize, maximize)


def test_validate_outcome_constraints_success():
    outcome_constraints = ["TotalForceX <= 10", "Pressure >= 5.5"]

    _validate_outcome_constraints(outcome_constraints)


@pytest.mark.parametrize(
    "outcome_constraints, error_message",
    [
        (None, "outcome_constraints must be a list"),
        ([123], "Constraint at index 0 must be a string"),
        (
            ["TotalForceX > 10"],
            r"Constraint at index 0 \(TotalForceX > 10\) must contain either >= or <= operator",
        ),
        (
            ["TotalForceX <= 10 <= 20"],
            r"Constraint at index 0 \(TotalForceX <= 10 <= 20\) must be of form 'metric_name <= value'",
        ),
        (["<= 10"], r"Constraint at index 0 \(<= 10\) must have a metric name"),
        (
            ["TotalForceX <= abc"],
            r"Constraint at index 0 \(TotalForceX <= abc\): 'abc' must be a numeric value",
        ),
    ],
)
def test_validate_outcome_constraints_fails(outcome_constraints, error_message):
    with pytest.raises(
        expected_exception=InvalidArguments,
        match=error_message,
    ):
        _validate_outcome_constraints(outcome_constraints)


def test_validate_n_iters_success():
    n_iters = 10

    _validate_n_iters(n_iters)


@pytest.mark.parametrize(
    "n_iters, error_message",
    [
        (None, "n_iters must be an integer"),
        ("5", "n_iters must be an integer"),
        (0, "n_iters must be strictly positive"),
        (-5, "n_iters must be strictly positive"),
    ],
)
def test_validate_n_iters_fails(n_iters, error_message):
    with pytest.raises(
        expected_exception=InvalidArguments,
        match=error_message,
    ):
        _validate_n_iters(n_iters)


def validate_max_displacement_success():
    max_displacement = [1, 0.25]
    bounding_boxes = [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]]

    _validate_max_displacement(max_displacement, bounding_boxes)

    _validate_max_displacement(None, bounding_boxes)


@pytest.mark.parametrize(
    "max_displacement, bounding_boxes, error_message",
    [
        (
            "not_a_list",
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "max_displacement must be a list",
        ),
        (
            123,
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "max_displacement must be a list",
        ),
        (
            {},
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "max_displacement must be a list",
        ),
        (
            ["this_is_a_string"],
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "max_displacement contains non-numeric values",
        ),
        (
            [1, "perhaps_a_string"],
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "max_displacement contains non-numeric values",
        ),
        (
            [None],
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "max_displacement contains non-numeric values",
        ),
        (
            [1.0],
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "Max displacement list and bounding boxes list must have the same number of items",
        ),
        (
            [1.0, 2.0, 3.0],
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]],
            "Max displacement list and bounding boxes list must have the same number of items",
        ),
        (
            [],
            [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]],
            "Max displacement list and bounding boxes list must have the same number of items",
        ),
    ],
)
def test_validate_max_displacement_fails(max_displacement, bounding_boxes, error_message):
    with pytest.raises(
        expected_exception=InvalidArguments,
        match=error_message,
    ):
        _validate_max_displacement(max_displacement, bounding_boxes)


@responses.activate
def test_run_parametric_optimization(simai_client, mocker):
    workspace_id = "insert_cool_reference"
    mocker.patch("ansys.simai.core.data.optimizations._validate_geometry_generation_fn_signature")
    geometry_upload = mocker.patch.object(simai_client.geometries, "upload")
    geometry_upload.return_value = simai_client.geometries._model_from({"id": "geomx"})

    responses.add(
        responses.POST,
        f"https://test.test/workspaces/{workspace_id}/optimizations",
        status=202,
        json={"id": "wow", "state": "requested", "trial_runs": []},
    )
    responses.add(
        responses.POST,
        "https://test.test/optimizations/wow/trial-runs",
        status=202,
        json={"id": "wow1", "state": "requested"},
    )
    responses.add(
        responses.POST,
        "https://test.test/optimizations/wow/trial-runs",
        status=202,
        json={"id": "wow2", "state": "requested"},
    )
    responses.add(
        responses.POST,
        "https://test.test/optimizations/wow/trial-runs",
        status=202,
        json={"id": "wow3", "state": "requested"},
    )
    threading.Timer(
        0.1,
        simai_client._api._handle_sse_event,
        args=[
            sseclient.Event(
                data=json.dumps(
                    {
                        "type": "job",
                        "status": "successful",
                        "record": {
                            "id": "wow",
                            "state": "successful",
                            "initial_geometry_parameters": {"a": 1},
                        },
                        "target": {"type": "optimization", "id": "wow"},
                    }
                )
            )
        ],
    ).start()
    for i in range(1, 4):
        threading.Timer(
            i / 10 + 0.1,
            simai_client._api._handle_sse_event,
            args=[
                sseclient.Event(
                    data=json.dumps(
                        {
                            "type": "job",
                            "status": "successful",
                            "record": {
                                "id": f"wow{i}",
                                "state": "successful",
                                "is_feasible": "true",
                                "outcome_values": i,
                                "next_geometry_parameters": {"a": i + 1} if i != 3 else None,
                            },
                            "target": {"type": "optimization_trial_run", "id": f"wow{i}"},
                        }
                    )
                )
            ],
        ).start()
    geometry_generation_fn = mocker.stub(name="geometry_gen")
    results = simai_client.optimizations.run_parametric(
        geometry_generation_fn=geometry_generation_fn,
        geometry_parameters={
            "a": {"bounds": (-12.5, 12.5)},
        },
        minimize=["TotalForceX"],
        boundary_conditions={"VelocityX": 10.5},
        outcome_constraints=["TotalForceX <= 10"],
        n_iters=3,
        workspace=workspace_id,
    )
    assert results == [{"objective": i, "parameters": {"a": i}} for i in range(1, 4)]


@responses.activate
def test_run_non_parametric_optimization(simai_client, geometry_factory):
    workspace_id = "insert_cool_reference"
    geometry = geometry_factory(workspace_id=workspace_id)

    responses.add(
        responses.POST,
        f"https://test.test/workspaces/{workspace_id}/optimizations",
        status=202,
        json={"id": "wow", "state": "requested", "trial_runs": []},
    )
    responses.add(
        responses.POST,
        "https://test.test/optimizations/wow/trial-runs",
        status=202,
        json={"id": "wow1", "state": "requested"},
    )
    responses.add(
        responses.POST,
        "https://test.test/optimizations/wow/trial-runs",
        status=202,
        json={"id": "wow2", "state": "requested"},
    )
    responses.add(
        responses.POST,
        "https://test.test/optimizations/wow/trial-runs",
        status=202,
        json={"id": "wow3", "state": "requested"},
    )
    threading.Timer(
        0.1,
        simai_client._api._handle_sse_event,
        args=[
            sseclient.Event(
                data=json.dumps(
                    {
                        "type": "job",
                        "status": "successful",
                        "record": {
                            "id": "wow",
                            "state": "successful",
                            "initial_geometry_parameters": None,
                        },
                        "target": {"type": "optimization", "id": "wow"},
                    }
                )
            )
        ],
    ).start()
    for i in range(1, 4):
        threading.Timer(
            i / 10 + 0.1,
            simai_client._api._handle_sse_event,
            args=[
                sseclient.Event(
                    data=json.dumps(
                        {
                            "type": "job",
                            "status": "successful",
                            "record": {
                                "id": f"wow{i}",
                                "state": "successful",
                                "is_feasible": "true",
                                "outcome_values": i,
                                "next_geometry_parameters": None,
                            },
                            "target": {"type": "optimization_trial_run", "id": f"wow{i}"},
                        }
                    )
                )
            ],
        ).start()
    results = simai_client.optimizations.run_non_parametric(
        geometry=geometry,
        bounding_boxes=[[0.1, 1, 0.1, 1, 0.1, 1]],
        symmetries=["x", "y", "z"],
        minimize=["TotalForceX"],
        boundary_conditions={"VelocityX": 10.5},
        n_iters=3,
    )
    assert results == [{"objective": i} for i in range(1, 4)]
