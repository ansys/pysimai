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
def geometries_with_two_metadata(create_mock_geometry):
    """A list of geometries with 2 numerical metadata:
    - 1 int metadata (length), range 0 to 6
    - 1 float metadata (width), range 0.0 to 0.6
    """
    geometries = []
    for i in range(7):
        for j in range(7):
            geometries.append(create_mock_geometry(id=f"l-{i}-w-{j}", length=i, width=j / 10))
    yield geometries


@pytest.fixture()
def geometries_with_two_metadata_and_incomplete_ones(create_mock_geometry):
    """A list of geometries with 2 numerical metadata:
    - 1 int metadata (length), range 0 to 6
    - 1 float metadata (width), range 0.0 to 0.6
    """
    geometries = []
    for i in range(7):
        for j in range(7):
            geometries.append(create_mock_geometry(id=f"l-{i}-w-{j}", length=i, width=j / 10))
    # create a double of 2-2
    geometries.append(create_mock_geometry(id="l-2-w-2-bis", length=2, width=0.2))
    # add incomplete geometries
    geometries.append(create_mock_geometry(id="l-3", length=3))
    geometries.append(create_mock_geometry(id="w-5", width=0.5))
    yield geometries


def create_length_width_set(geometries):
    return {(g.metadata["length"], g.metadata["width"]) for g in geometries}


def test_sweep_2_dimensions_center(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a (2, 0.3) geometry,
    THEN 4 geometries are returned: (1, 0.3), (3, 0.3), (2, 0.2), (2, 0.4)
    IF including diagonals,
    THEN 4 additional corner geometries are returned: (1, 0.2), (1, 0.4), (3, 0.2), (3, 0.4)
    IF including center
    THEN the candidate (2, 0.3) is included in the results
    """

    candidate = geometries_with_two_metadata[17]
    assert candidate.metadata["length"] == 2
    assert candidate.metadata["width"] == 0.3

    direct_neighbors = {(1, 0.3), (3, 0.3), (2, 0.2), (2, 0.4)}
    all_neighbors = direct_neighbors.union({(1, 0.2), (1, 0.4), (3, 0.2), (3, 0.4)})

    for include_diagonals in [False, True]:
        for include_center in [False, True]:
            swept = geometry_directory.sweep(
                candidate_geometry=candidate,
                geometries=geometries_with_two_metadata,
                include_center=include_center,
                include_diagonals=include_diagonals,
            )
            length_widths = create_length_width_set(swept)
            expected_neighbors = all_neighbors if include_diagonals else direct_neighbors
            if include_center:
                expected_neighbors.add((2, 0.3))
            assert length_widths == expected_neighbors


def test_sweep_2_dimensions_center_order_2(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a (2, 0.3) geometry with order 2
    THEN 8 geometries are returned:
        (0, 0.3), (1, 0.3), (3, 0.3), (4, 0.3),
        (2, 0.1), (2, 0.2), (2, 0.4), (2, 0.5)
    IF including center
    THEN the candidate (2, 0.3) is included in the results
    """

    candidate = geometries_with_two_metadata[17]
    assert candidate.metadata["length"] == 2
    assert candidate.metadata["width"] == 0.3

    direct_neighbors = {
        (0, 0.3),
        (1, 0.3),
        (3, 0.3),
        (4, 0.3),
        (2, 0.1),
        (2, 0.2),
        (2, 0.4),
        (2, 0.5),
    }

    for include_center in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_two_metadata,
            order=2,
            include_center=include_center,
        )
        length_widths = create_length_width_set(swept)
        expected_neighbors = direct_neighbors
        if include_center:
            expected_neighbors.add((2, 0.3))
        assert length_widths == expected_neighbors


def test_sweep_2_dimensions_center_order_2_with_diagonals(
    geometry_directory, geometries_with_two_metadata
):
    """WHEN running a sweep around a (2, 0.3) geometry with order 2 including diagonals
    THEN all those geometries are returned:
        (0, 0.1), (1, 0.1), (2, 0.1), (3, 0.1), (4, 0.1)
        (0, 0.2), (1, 0.2), (2, 0.2), (3, 0.2), (4, 0.2)
        (0, 0.3), (1, 0.3),           (3, 0.3), (4, 0.3)
        (0, 0.4), (1, 0.4), (2, 0.4), (3, 0.4), (4, 0.4)
        (0, 0.5), (1, 0.5), (2, 0.5), (3, 0.5), (4, 0.5)
    IF including center
    THEN the candidate (2, 0.3) is included in the results
    """

    candidate = geometries_with_two_metadata[17]
    assert candidate.metadata["length"] == 2
    assert candidate.metadata["width"] == 0.3

    neighbors = {
        (0, 0.1),
        (1, 0.1),
        (2, 0.1),
        (3, 0.1),
        (4, 0.1),
        (0, 0.2),
        (1, 0.2),
        (2, 0.2),
        (3, 0.2),
        (4, 0.2),
        (0, 0.3),
        (1, 0.3),
        (3, 0.3),
        (4, 0.3),
        (0, 0.4),
        (1, 0.4),
        (2, 0.4),
        (3, 0.4),
        (4, 0.4),
        (0, 0.5),
        (1, 0.5),
        (2, 0.5),
        (3, 0.5),
        (4, 0.5),
    }

    for include_center in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_two_metadata,
            order=2,
            include_center=include_center,
            include_diagonals=True,
        )
        length_widths = create_length_width_set(swept)
        expected_neighbors = neighbors
        if include_center:
            expected_neighbors.add((2, 0.3))
        assert length_widths == neighbors


def test_sweep_2_dimensions_min_corner(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a "min corner" (0, 0.0) geometry,
    THEN 2 geometries are returned: (1, 0) and (0, 0.1)
    IF including center
    THEN the candidate is included
    IF including diagonals
    THEN the diagonal geometry is returned: (1, 0.1)
    """
    candidate = geometries_with_two_metadata[0]
    assert candidate.metadata["length"] == 0
    assert candidate.metadata["width"] == 0

    for include_diagonals in [False, True]:
        for include_center in [False, True]:
            swept = geometry_directory.sweep(
                candidate_geometry=candidate,
                geometries=geometries_with_two_metadata,
                include_center=include_center,
                include_diagonals=include_diagonals,
            )
            length_widths = create_length_width_set(swept)
            expected_neighbors = {(1, 0), (0, 0.1)}
            if include_center:
                expected_neighbors.add((0, 0.0))
            if include_diagonals:
                expected_neighbors.add((1, 0.1))
            assert length_widths == expected_neighbors


def test_sweep_2_dimensions_max_corner(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a "max corner" (6, 0.6) geometry,
    THEN 2 geometries are returned: (5, 0.6) and (6, 0.5)
    IF including center
    THEN the candidate is included
    IF include diagonals
    THEN (5, 0.5) is also returned
    """
    candidate = geometries_with_two_metadata[48]
    assert candidate.metadata["length"] == 6
    assert candidate.metadata["width"] == 0.6

    for include_diagonals in [False, True]:
        for include_center in [False, True]:
            swept = geometry_directory.sweep(
                candidate_geometry=candidate,
                geometries=geometries_with_two_metadata,
                include_center=include_center,
                include_diagonals=include_diagonals,
            )
            length_widths = create_length_width_set(swept)

            expected_neighbors = {(6, 0.5), (5, 0.6)}
            if include_center:
                expected_neighbors.add((6, 0.6))
            if include_diagonals:
                expected_neighbors.add((5, 0.5))
            assert length_widths == expected_neighbors


def test_sweep_2_dimensions_length_border(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a "border" (0, 0.3) geometry,
    THEN 3 geometries are returned: (1, 0.3), (0, 0.2), (0, 0.4)
    """
    candidate = geometries_with_two_metadata[3]
    assert candidate.metadata["length"] == 0
    assert candidate.metadata["width"] == 0.3
    swept = geometry_directory.sweep(
        candidate_geometry=candidate, geometries=geometries_with_two_metadata
    )
    length_widths = create_length_width_set(swept)

    assert length_widths == {(1, 0.3), (0, 0.2), (0, 0.4)}


def test_sweep_2_dimensions_width_border(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a "border" (4, 0.6) geometry,
    THEN 3 geometries are returned: (3, 0.6), (5, 0.6), (4, 0.5)
    """
    candidate = geometries_with_two_metadata[34]
    assert candidate.metadata["length"] == 4
    assert candidate.metadata["width"] == 0.6
    swept = geometry_directory.sweep(
        candidate_geometry=candidate, geometries=geometries_with_two_metadata
    )
    length_widths = create_length_width_set(swept)
    assert length_widths == {(3, 0.6), (5, 0.6), (4, 0.5)}


def test_sweep_2_dimensions_ignoring_length(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a (3, 0.3) geometry along the second (width) metadata,
    THEN 14 geometries are returned:
    - all 7 geometries with width=0.2 (whatever length), and
    - all 7 geometries with width=0.4 (whatever length).
    ALSO if including center
    THEN results include all 7 geometries with width=0.3 (whatever length)
    ALSO including diagonals has no effect as we sweep only 1 variable
    """
    candidate = geometries_with_two_metadata[24]
    assert candidate.metadata["length"] == 3
    assert candidate.metadata["width"] == 0.3

    for include_diagonals in [False, True]:
        for include_center in [False, True]:
            swept = geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=["width"],
                geometries=geometries_with_two_metadata,
                include_center=include_center,
                include_diagonals=include_diagonals,
            )
            assert len(swept) == (21 if include_center else 14)
            length_widths = create_length_width_set(swept)
            expected_results = set()
            for w in [0.2, 0.3, 0.4] if include_center else [0.2, 0.4]:
                for l in range(7):  # noqa: E741
                    expected_results.add((l, w))
            assert length_widths == expected_results


def test_sweep_2_dimensions_fixing_length(geometry_directory, geometries_with_two_metadata):
    """WHEN running a sweep around a (3, 0.3) geometry along the second (width) metadata,
      and fixing the length metadata
    THEN 2 geometries are returned:
    - geometry with width=0.2 and length=3, and
    - geometry with width=0.4 and length=3
    IF including center, then the candidate is returned
    ALSO including diagonals has no effect as we sweep only 1 variable
    """
    candidate = geometries_with_two_metadata[24]
    assert candidate.metadata["length"] == 3
    assert candidate.metadata["width"] == 0.3

    for include_diagonals in [False, True]:
        for include_center in [False, True]:
            swept = geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=["width"],
                fixed_metadata=["length"],
                geometries=geometries_with_two_metadata,
                include_center=include_center,
                include_diagonals=include_diagonals,
            )
            length_widths = create_length_width_set(swept)
            if include_center:
                assert length_widths == {(3, 0.2), (3, 0.3), (3, 0.4)}
            else:
                assert length_widths == {(3, 0.2), (3, 0.4)}


def test_sweep_2_dimensions_center_big_order_including_diagonals(
    geometry_directory, geometries_with_two_metadata
):
    """WHEN running a sweep around a (2, 0.3) geometry with very large order and including diagonals
    THEN all geometries are returned, candidate only if include_center
    """

    candidate = geometries_with_two_metadata[17]
    assert candidate.metadata["length"] == 2
    assert candidate.metadata["width"] == 0.3

    set_of_all = create_length_width_set(geometries_with_two_metadata)

    for include_center in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_two_metadata,
            order=20,
            include_center=include_center,
            include_diagonals=True,
        )
        length_widths = create_length_width_set(swept)

        if include_center:
            assert length_widths == set_of_all
        else:
            assert length_widths == set_of_all - {(2, 0.3)}
