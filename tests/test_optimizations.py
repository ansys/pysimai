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

from ansys.simai.core.data.optimizations import _validate_geometry_generation_fn_signature
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
        bounding_boxes=[[1, 1, 1, 1, 1, 1]],
        symmetries=["x", "y", "z"],
        minimize=["TotalForceX"],
        boundary_conditions={"VelocityX": 10.5},
        n_iters=3,
    )
    assert results == [{"objective": i} for i in range(1, 4)]
