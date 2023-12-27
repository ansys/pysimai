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
def geometries_with_one_metadata(create_mock_geometry):
    """A list of geometries with:
    - 1 numerical metadata (length), range 0 to 9
    Used to test basic sweep on 1 dimension.
    """
    geometries = []
    for i in range(10):
        geometries.append(create_mock_geometry(id=f"l-{i}", length=i))
    yield geometries


@pytest.fixture()
def geometries_with_one_usable_metadata(create_mock_geometry):
    """A list of geometries with:
    - 1 numerical metadata (length), range 0 to 9,
    - 1 string metadata (type)
    Used to test conditions when string metadata is included or ignored
    """
    geometries = []
    for i in range(10):
        geometries.append(create_mock_geometry(id=f"l-{i}", length=i, type=str(i)))
    yield geometries


@pytest.fixture()
def geometries_with_no_usable_metadata(create_mock_geometry):
    """A list of geometries with no numerical metadata (only a string one)
    Used to test failure case
    """
    geometries = []
    for i in range(10):
        geometries.append(create_mock_geometry(id=f"l-{i}", type=str(i)))
    yield geometries


def test_sweep_one_dimension_gives_two_neighbors(geometry_directory, geometries_with_one_metadata):
    """WHEN Running a sweep in the middle of a single dimension
    THEN two neighbors are returned
    ALSO include_diagonals has no effect with 1 metadata
    """
    candidate = geometries_with_one_metadata[5]
    assert candidate.metadata["length"] == 5
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {4, 6}


def test_sweep_one_dimension_with_include_center_gives_three_results(
    geometry_directory, geometries_with_one_metadata
):
    """WHEN Running a sweep in the middle of a single dimension with include_center
    THEN three neighbors are returned
    ALSO include_diagonals has no effect with 1 metadata
    """
    candidate = geometries_with_one_metadata[5]
    assert candidate.metadata["length"] == 5
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            include_center=True,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {4, 5, 6}


def test_sweep_one_dimension_along_explicit_variable(
    geometry_directory, geometries_with_one_metadata
):
    """WHEN Running a sweep along explicit variable
    THEN two neighbors are returned
    ALSO include_diagonals has no effect with 1 metadata
    """
    candidate = geometries_with_one_metadata[5]
    assert candidate.metadata["length"] == 5
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            swept_metadata="length",
            geometries=geometries_with_one_metadata,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {4, 6}

        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            swept_metadata=["length"],
            geometries=geometries_with_one_metadata,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {4, 6}


def test_sweep_one_dimension_with_order(geometry_directory, geometries_with_one_metadata):
    """WHEN Running a sweep in the middle of a single dimension with an order parameter
    THEN 2 * order neighbors are returned if possible
    ALSO include_diagonals has no effect with 1 metadata
    """
    candidate = geometries_with_one_metadata[5]
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            order=2,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {3, 4, 6, 7}

    candidate = geometries_with_one_metadata[1]
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            order=3,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {0, 2, 3, 4}

    candidate = geometries_with_one_metadata[0]
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            order=3,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {1, 2, 3}


def test_sweep_one_dimension_with_order_and_include_center(
    geometry_directory, geometries_with_one_metadata
):
    """WHEN Running a sweep in the middle of a single dimension with order and include_center
    THEN 2 * order + 1 neighbors are returned when possible
    ALSO include_diagonals has no effect with 1 metadata
    """
    candidate = geometries_with_one_metadata[5]
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            order=2,
            include_center=True,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {3, 4, 5, 6, 7}

    candidate = geometries_with_one_metadata[1]
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            order=3,
            include_center=True,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {0, 1, 2, 3, 4}

    candidate = geometries_with_one_metadata[0]
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            order=3,
            include_center=True,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {0, 1, 2, 3}


def test_sweep_one_dimension_at_min_gives_one_neighbor(
    geometry_directory, geometries_with_one_metadata
):
    """WHEN Running a sweep at the min border of a single dimension
    THEN only one neighbor is returned
    """
    candidate = geometries_with_one_metadata[0]
    assert candidate.metadata["length"] == 0
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            include_diagonals=include_diagonals,
        )
        assert len(swept) == 1
        assert swept[0].metadata["length"] == 1


def test_sweep_one_dimension_at_max_gives_one_neighbor(
    geometry_directory, geometries_with_one_metadata
):
    """WHEN Running a sweep at the max border of a single dimension
    THEN only one neighbor is returned
    """
    candidate = geometries_with_one_metadata[9]
    assert candidate.metadata["length"] == 9
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            include_diagonals=include_diagonals,
        )
        assert len(swept) == 1
        assert swept[0].metadata["length"] == 8


def test_sweep_all_columns_text_metadata_ignored(
    geometry_directory, geometries_with_one_usable_metadata
):
    """WHEN Running a sweep without specifying columns
    THEN textual metadata is ignored, and sweep only uses numerical metadata
    """
    candidate = geometries_with_one_usable_metadata[1]
    for include_diagonals in [False, True]:
        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_usable_metadata,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {0, 2}

        swept = geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_usable_metadata,
            include_center=True,
            include_diagonals=include_diagonals,
        )
        assert {g.metadata["length"] for g in swept} == {0, 1, 2}


def test_sweep_unknown_metadata_column_raises(
    geometry_directory, geometries_with_one_usable_metadata
):
    """WHEN Running a sweep with specifying an unknown metadata column
    THEN a ValueError is raised
    """
    candidate = geometries_with_one_usable_metadata[4]
    for include_diagonals in [False, True]:
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=["length", "not-existing"],
                geometries=geometries_with_one_usable_metadata,
                include_diagonals=include_diagonals,
            )
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=["toto"],
                geometries=geometries_with_one_usable_metadata,
                include_diagonals=include_diagonals,
            )


def test_sweep_with_text_metadata_fails(geometry_directory, geometries_with_one_usable_metadata):
    """WHEN Running a sweep using a text metadata
    THEN a ValueError is raised
    """
    candidate = geometries_with_one_usable_metadata[4]
    for include_diagonals in [False, True]:
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=["length", "type"],
                geometries=geometries_with_one_usable_metadata,
                include_diagonals=include_diagonals,
            )
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=["type"],
                geometries=geometries_with_one_usable_metadata,
                include_diagonals=include_diagonals,
            )


def test_sweep_with_no_metadata_fails(geometry_directory, geometries_with_no_usable_metadata):
    """WHEN Running a sweep using no metadata column
    THEN a ValueError is raised
    """
    candidate = geometries_with_no_usable_metadata[4]
    for include_diagonals in [False, True]:
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                geometries=geometries_with_no_usable_metadata,
                include_diagonals=include_diagonals,
            )
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=["type"],
                geometries=geometries_with_no_usable_metadata,
                include_diagonals=include_diagonals,
            )


def test_sweep_incorrect_metadata_argument(geometry_directory, geometries_with_one_metadata):
    """WHEN Running a sweep passing a metadata argument neither List[str] nor str,
    THEN a TypeError is raised
    """
    candidate = geometries_with_one_metadata[4]
    for include_diagonals in [False, True]:
        with pytest.raises(TypeError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=6,
                geometries=geometries_with_one_metadata,
                include_diagonals=include_diagonals,
            )
        with pytest.raises(TypeError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=[6],
                geometries=geometries_with_one_metadata,
                include_diagonals=include_diagonals,
            )


def test_sweep_incorrect_order_argument(geometry_directory, geometries_with_one_metadata):
    """WHEN Running a sweep passing an order argument not int
    THEN a TypeError is raised
    WHEN Running a sweep passing an order argument int < 1
    THEN a ValueError is raised
    """
    candidate = geometries_with_one_metadata[4]
    for include_diagonals in [False, True]:
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                geometries=geometries_with_one_metadata,
                order=0,
                include_diagonals=include_diagonals,
            )
        with pytest.raises(ValueError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=[6],
                geometries=geometries_with_one_metadata,
                order=-3,
                include_diagonals=include_diagonals,
            )
        with pytest.raises(TypeError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                geometries=geometries_with_one_metadata,
                order=2.4,
                include_diagonals=include_diagonals,
            )
        with pytest.raises(TypeError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=[6],
                geometries=geometries_with_one_metadata,
                order="blabla",
                include_diagonals=include_diagonals,
            )
        with pytest.raises(TypeError):
            geometry_directory.sweep(
                candidate_geometry=candidate,
                swept_metadata=[6],
                geometries=geometries_with_one_metadata,
                order=[4],
                include_diagonals=include_diagonals,
            )


def test_sweep_incorrect_tolerance_argument(geometry_directory, geometries_with_one_metadata):
    """WHEN Running a tolerance passing an order argument not number
    THEN a TypeError is raised
    WHEN Running a sweep passing an tolerance argument < 0
    THEN a ValueError is raised
    """
    candidate = geometries_with_one_metadata[4]
    geometry_directory.sweep(
        candidate_geometry=candidate,
        geometries=geometries_with_one_metadata,
        tolerance=0,
    )
    with pytest.raises(ValueError):
        geometry_directory.sweep(
            candidate_geometry=candidate,
            swept_metadata=[6],
            geometries=geometries_with_one_metadata,
            tolerance=-3,
        )
    with pytest.raises(TypeError):
        geometry_directory.sweep(
            candidate_geometry=candidate,
            geometries=geometries_with_one_metadata,
            tolerance="zzz",
        )
    with pytest.raises(TypeError):
        geometry_directory.sweep(
            candidate_geometry=candidate,
            swept_metadata=[6],
            geometries=geometries_with_one_metadata,
            tolerance=[4],
        )
