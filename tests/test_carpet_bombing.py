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

from ansys.simai.core.data.types import Range


@pytest.fixture
def geometries_with_two_metadata():
    """A list of geometries with 2 numerical metadata:
    - length: 10 values ranging from 0.0 to 90.0
    - width: 10 values ranging from 0 to 9
    """

    def query_geometries_data(workspace_id, server_filters=None):
        geometries = []
        for i in range(10):
            for j in range(10):
                geometries.append(
                    {"id": f"l-{i}-w-{j}", "metadata": {"length": i * 10.0, "width": j}}
                )
        return geometries

    yield query_geometries_data


@pytest.fixture(scope="function")
def extra_client(simai_client, geometries_with_two_metadata):
    simai_client._api.geometries = geometries_with_two_metadata
    yield simai_client


def test_no_filter(extra_client):
    """WHEN getting geometries with no Range filter
    THEN all geometries are returned
    """
    geometries = extra_client.geometries.list()
    assert len(geometries) == 100

    geometries = extra_client.geometries.list(filters={})
    assert len(geometries) == 100


def test_filtering_range_simple(extra_client):
    """WHEN getting geometries with filtering with a Range
    THEN geometries with metadata >= min and < max are returned
    """
    geometries = extra_client.geometries.list(filters={"length": Range(27, 45)})
    assert len(geometries) == 20
    for geometry in geometries:
        assert geometry.metadata["length"] in [30, 40]


def test_filtering_range_bounds_inclusion(extra_client):
    """WHEN filtering geometries with a Range
    THEN both bounds are included in results
    """
    geometries = extra_client.geometries.list(filters={"length": Range(30, 40)})
    assert len(geometries) == 20
    for geometry in geometries:
        assert geometry.metadata["length"] in [30, 40]


def test_filtering_same_min_max(extra_client):
    """WHEN filtering with a Range whose bounds are equal
    THEN only geometries matching bounds are returned
    """
    geometries = extra_client.geometries.list(filters={"length": Range(20, 20)})
    assert len(geometries) == 10

    geometries = extra_client.geometries.list(filters={"length": Range(46, 46)})
    assert len(geometries) == 0


def test_filtering_two_metadata(extra_client):
    """WHEN filtering with Range objects on two metadata
    THEN geometries whose metadata each matching its Range are returned
    """
    geometries = extra_client.geometries.list(
        filters={"length": Range(35, 55), "width": Range(7.0, 9.0)}
    )
    assert len(geometries) == 6
    for geometry in geometries:
        assert geometry.metadata["length"] in [40, 50]
        assert geometry.metadata["width"] in [7, 8, 9]


def test_filtering_with_only_lower_bound(extra_client):
    """WHEN filtering with a Range having only a lower bound
    THEN geometries whose metadata >= this bound are returned
    """
    geometries = extra_client.geometries.list(filters={"length": Range(min=80)})
    assert len(geometries) == 20
    for geometry in geometries:
        assert geometry.metadata["length"] in [80, 90]


def test_filtering_with_only_upper_bound(extra_client):
    """WHEN filtering with a Range having only a upper bound
    THEN geometries whose metadata <= this bound are returned
    """
    geometries = extra_client.geometries.list(filters={"length": Range(max=40)})
    assert len(geometries) == 50
    for geometry in geometries:
        assert geometry.metadata["length"] in [0, 10, 20, 30, 40]


def test_filtering_tolerance_upper(extra_client):
    """WHEN filtering with Ranges with a tolerance
    THEN values just above the min bound are included
    AND values just above to the max bound are included
    """
    epsilon = 5 * 10**-2
    geometries = extra_client.geometries.list(
        filters={"length": Range(30 + epsilon, 50 + epsilon, tolerance=0.1)}
    )
    assert len(geometries) == 30
    for geometry in geometries:
        assert geometry.metadata["length"] in [30, 40, 50]


def test_filtering_default_tolerance_upper(extra_client):
    """WHEN filtering with Ranges without passing a tolerance
    THEN tolerance of 10**-6 is used
    AND values just above the min bound are included
    AND values just above to the max bound are included
    """
    epsilon = 5 * 10**-7
    geometries = extra_client.geometries.list(filters={"length": Range(30 + epsilon, 50 + epsilon)})
    assert len(geometries) == 30
    for geometry in geometries:
        assert geometry.metadata["length"] in [30, 40, 50]


def test_filtering_above_tolerance(extra_client):
    """WHEN filtering with Ranges using default 10**-6 tolerance
    THEN values differing more than tolerance are considered different
    """
    epsilon = 5 * 10**-5
    geometries = extra_client.geometries.list(filters={"length": Range(30 + epsilon, 50 + epsilon)})
    assert len(geometries) == 20
    for geometry in geometries:
        assert geometry.metadata["length"] in [40, 50]


def test_filtering_tolerance_lower(extra_client):
    """WHEN filtering with Ranges with a given tolerance
    THEN values just below the min bound are included
    AND values just below the max bound are included
    """
    epsilon = 5 * 10**-2
    geometries = extra_client.geometries.list(
        filters={"length": Range(30 - epsilon, 50 - epsilon, tolerance=0.1)}
    )
    assert len(geometries) == 30
    for geometry in geometries:
        assert geometry.metadata["length"] in [30, 40, 50]


def test_filtering_default_tolerance_lower(extra_client):
    """WHEN filtering with Ranges without passing a tolerance
    THEN tolerance of 10**-6 is used
    AND values just below the min bound are included
    AND values just below the max bound are included
    """
    epsilon = 5 * 10**-7
    geometries = extra_client.geometries.list(filters={"length": Range(30 - epsilon, 50 - epsilon)})
    assert len(geometries) == 30
    for geometry in geometries:
        assert geometry.metadata["length"] in [30, 40, 50]
