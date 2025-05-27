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

from typing import TYPE_CHECKING

import pytest
import responses

if TYPE_CHECKING:
    from ansys.simai.core.data.global_coefficients_requests import (
        ProcessGlobalCoefficient,
    )

METADATA_RAW = {
    "boundary_conditions": {
        "fields": [
            {
                "format": "value",
                "keys": None,
                "name": "Vx",
                "unit": None,
                "value": -5.569587230682373,
            }
        ]
    },
    "surface": {
        "fields": [
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "Pressure",
                "unit": None,
            },
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "TurbulentViscosity",
                "unit": None,
            },
        ]
    },
    "volume": {
        "fields": [
            {
                "format": "value",
                "keys": None,
                "location": "cell",
                "name": "Pressure",
                "unit": None,
            }
        ]
    },
}


@responses.activate
def test_process_formula_success(global_coefficient_request_factory):
    gc_formula = "max(Pressure)"
    project_id = "xX007Xx"
    responses.add(
        responses.POST,
        f"https://test.test/projects/{project_id}/process-formula",
        status=204,
    )
    process_gc: ProcessGlobalCoefficient = global_coefficient_request_factory(
        data={
            "id": f"{project_id}-process-{gc_formula}",
        },
        project_id="xX007Xx",
        gc_formula=gc_formula,
        sample_metadata=METADATA_RAW,
        bc=["Vx"],
        surface_variables=["Pressure"],
    )
    check_sse_event = {
        "status": "successful",
        "target": {"action": "check", "formula": gc_formula},
    }
    compute_result = 0.25478328
    compute_sse_event = {
        "status": "successful",
        "target": {"action": "compute", "formula": gc_formula},
        "result": {"value": compute_result},
    }

    process_gc.run()

    assert not process_gc.is_ready

    process_gc._handle_job_sse_event(check_sse_event)

    assert not process_gc.is_ready
    assert process_gc.result is None

    process_gc._handle_job_sse_event(compute_sse_event)

    assert process_gc.is_ready
    assert process_gc.result == compute_result


@responses.activate
def test_process_formula_success_with_cache(global_coefficient_request_factory):
    gc_formula = "max(Pressure)"
    project_id = "xX007Xx"
    compute_result = 0.25478328
    responses.add(
        responses.POST,
        f"https://test.test/projects/{project_id}/process-formula",
        status=200,
        json={"result": compute_result},
    )
    process_gc: ProcessGlobalCoefficient = global_coefficient_request_factory(
        data={
            "id": f"{project_id}-process-{gc_formula}",
        },
        project_id="xX007Xx",
        gc_formula=gc_formula,
        sample_metadata=METADATA_RAW,
        bc=["Vx"],
        surface_variables=["Pressure"],
    )

    process_gc.run()

    assert process_gc.is_ready
    assert process_gc.result == compute_result


@pytest.mark.parametrize("action", ["check", "compute"])
@responses.activate
def test_process_formula_failure(global_coefficient_request_factory, action):
    gc_formula = "max(Pressure)"
    project_id = "xX007Xx"
    responses.add(
        responses.POST,
        f"https://test.test/projects/{project_id}/process-formula",
        status=204,
    )
    process_gc: ProcessGlobalCoefficient = global_coefficient_request_factory(
        request_type=action,
        data={
            "id": f"{project_id}-process-{gc_formula}",
        },
        project_id="xX007Xx",
        gc_formula=gc_formula,
        sample_metadata=METADATA_RAW,
        bc=["Vx"],
        surface_variables=["Pressure"],
    )
    reason_of_failure = "wrong shoes"
    sse_event = {
        "status": "failure",
        "target": {"action": action, "formula": gc_formula},
        "reason": reason_of_failure,
    }

    process_gc.run()

    assert not process_gc.is_ready

    process_gc._handle_job_sse_event(sse_event)

    assert process_gc.has_failed
    assert all(keyword in process_gc.failure_reason for keyword in [reason_of_failure, gc_formula])
