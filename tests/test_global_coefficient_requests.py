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

import responses

if TYPE_CHECKING:
    from ansys.simai.core.data.global_coefficients_requests import (
        CheckGlobalCoefficient,
        ComputeGlobalCoefficient,
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
def test_check_formula_failure(global_coefficient_request_factory):
    gc_formula = "max(Pressure)"
    project_id = "xX007Xx"

    responses.add(
        responses.POST,
        f"https://test.test/projects/{project_id}/check-formula",
        status=200,
    )

    check_gc: CheckGlobalCoefficient = global_coefficient_request_factory(
        request_type="check",
        data={
            "id": f"{project_id}-check-{gc_formula}",
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
        "target": {"action": "check", "formula": gc_formula},
        "reason": reason_of_failure,
    }

    check_gc._handle_job_sse_event(sse_event)

    assert check_gc.has_failed
    assert all(keyword in check_gc.failure_reason for keyword in [reason_of_failure, gc_formula])


@responses.activate
def test_check_formula_success(global_coefficient_request_factory):
    gc_formula = "max(Pressure)"
    project_id = "xX007Xx"

    responses.add(
        responses.POST,
        f"https://test.test/projects/{project_id}/check-formula",
        status=200,
    )

    check_gc: CheckGlobalCoefficient = global_coefficient_request_factory(
        request_type="check",
        data={
            "id": f"{project_id}-check-{gc_formula}",
        },
        project_id="xX007Xx",
        gc_formula=gc_formula,
        sample_metadata=METADATA_RAW,
        bc=["Vx"],
        surface_variables=["Pressure"],
    )

    sse_event = {
        "status": "successful",
        "target": {"action": "check", "formula": gc_formula},
    }

    check_gc._handle_job_sse_event(sse_event)

    assert check_gc.is_ready


@responses.activate
def test_compute_formula_failure(global_coefficient_request_factory):
    gc_formula = "max(Pressure)"
    project_id = "xX007Xx"

    responses.add(
        responses.POST,
        f"https://test.test/projects/{project_id}/check-formula",
        status=200,
    )

    check_gc: ComputeGlobalCoefficient = global_coefficient_request_factory(
        request_type="compute",
        data={
            "id": f"{project_id}-compute-{gc_formula}",
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
        "target": {"action": "compute", "formula": gc_formula},
        "reason": reason_of_failure,
    }

    check_gc._handle_job_sse_event(sse_event)

    assert check_gc.has_failed
    assert all(keyword in check_gc.failure_reason for keyword in [reason_of_failure, gc_formula])


@responses.activate
def test_compute_formula_success(global_coefficient_request_factory):
    gc_formula = "max(Pressure)"
    project_id = "xX007Xx"

    responses.add(
        responses.POST,
        f"https://test.test/projects/{project_id}/check-formula",
        status=200,
    )

    check_gc: ComputeGlobalCoefficient = global_coefficient_request_factory(
        request_type="compute",
        data={
            "id": f"{project_id}-compute-{gc_formula}",
        },
        project_id="xX007Xx",
        gc_formula=gc_formula,
        sample_metadata=METADATA_RAW,
        bc=["Vx"],
        surface_variables=["Pressure"],
    )

    compute_result = 0.25478328
    sse_event = {
        "status": "successful",
        "target": {"action": "compute", "formula": gc_formula},
        "result": {"value": compute_result},
    }

    check_gc._handle_job_sse_event(sse_event)

    assert check_gc.is_ready
    assert check_gc.result == compute_result
