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

import pytest


@pytest.fixture()
def geometries_with_epsilon_values(create_mock_geometry):
    """A list of geometries with a numerical metadata, with values separated
    by steps of 10**-2 and 10**-4, so tolerance can be tested.
    """
    geometries = []
    for length in [
        0.99,
        0.9999,
        1,
        1.0001,
        1.01,
        1.99,
        1.9999,
        2,
        2.0001,
        2.01,
        2.99,
        2.9999,
        3,
        3.0001,
        3.01,
        3.99,
        3.9999,
        4,
        4.0001,
        4.01,
    ]:
        geometries.append(create_mock_geometry(id=f"l{length}", length=length))
    yield geometries


def test_sweep_tolerance_default(geometry_directory, geometries_with_epsilon_values):
    """WHEN Running a sweep with a default tolerance, smaller than the epsilon in metadata values
    THEN every value in the metadata represent a step
      (every increasing order gives 1 more geometry).
    """
    candidate = next(g for g in geometries_with_epsilon_values if g.metadata["length"] == 3)
    assert candidate.metadata["length"] == 3
    swept = geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_epsilon_values,
        include_center=False,
    )
    assert {g.metadata["length"] for g in swept} == {2.9999, 3.0001}

    swept = geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_epsilon_values,
        order=3,
        include_center=False,
    )
    assert {g.metadata["length"] for g in swept} == {
        2.01,
        2.99,
        2.9999,
        3.0001,
        3.01,
        3.99,
    }


def test_sweep_tolerance_negligible(geometry_directory, geometries_with_epsilon_values):
    """WHEN Running a sweep with a tolerance 10**-5 smaller than the epsilon in values (10**-4)
    THEN every value in the metadata represent a step
        (every increasing order gives 1 more geometry).
    """
    candidate = next(g for g in geometries_with_epsilon_values if g.metadata["length"] == 3)
    swept = geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_epsilon_values,
        order=3,
        include_center=False,
        tolerance=10**-5,
    )
    assert {g.metadata["length"] for g in swept} == {
        2.01,
        2.99,
        2.9999,
        3.0001,
        3.01,
        3.99,
    }


def test_sweep_default_tolerance_10_minus_3(geometry_directory, geometries_with_epsilon_values):
    """WHEN Running a sweep with tolerance greater than some diffs in values
    THEN those values are counted together when concerning sweep order (depth)
    """

    tolerance = 10**-3
    candidate = next(g for g in geometries_with_epsilon_values if g.metadata["length"] == 3)
    assert candidate.metadata["length"] == 3
    swept = geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_epsilon_values,
        include_center=False,
        tolerance=tolerance,
    )
    # with tolerance 10**-3, 2.9999 is equal to 3, so the 2 neighbors are those:
    expected_without_center = {2.99, 3.01}
    assert {g.metadata["length"] for g in swept} == expected_without_center

    swept = geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_epsilon_values,
        include_center=True,
        tolerance=tolerance,
    )
    expected_with_center = expected_without_center.union({2.9999, 3, 3.0001})
    assert {g.metadata["length"] for g in swept} == expected_with_center


def test_sweep_default_tolerance_10_minus_3_order_3(
    geometry_directory, geometries_with_epsilon_values
):
    """WHEN Running a sweep with tolerance greater than some diffs in values
    THEN those values are grouped together when concerning sweep order (depth)
    """
    tolerance = 10**-3
    candidate = next(g for g in geometries_with_epsilon_values if g.metadata["length"] == 3)
    assert candidate.metadata["length"] == 3
    swept = geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_epsilon_values,
        include_center=False,
        order=3,
        tolerance=tolerance,
    )
    # With tolerance 10**-3, 2.9999 is equal to 3,
    # Also 1.9999, 2, and 2.0001 are equal so they are counted as 1 step,
    # same with 3.9999, 4, 4.0001.
    expected_without_center = {
        1.9999,
        2,
        2.0001,
        2.01,
        2.99,
        3.01,
        3.99,
        3.9999,
        4,
        4.0001,
    }
    assert {g.metadata["length"] for g in swept} == expected_without_center

    swept = geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_epsilon_values,
        include_center=True,
        order=3,
        tolerance=tolerance,
    )
    expected_with_center = expected_without_center.union({2.9999, 3, 3.0001})
    assert {g.metadata["length"] for g in swept} == expected_with_center
