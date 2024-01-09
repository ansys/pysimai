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

import collections
import itertools
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

from ansys.simai.core.data.types import Range, _HollowRange
from ansys.simai.core.utils.grouping import _ToleranceGrouper
from ansys.simai.core.utils.numerical import (
    DEFAULT_COMPARISON_EPSILON,
    is_equal_with_tolerance,
    is_number,
    is_smaller_with_tolerance,
    validate_tolerance_parameter,
)
from ansys.simai.core.utils.validation import _enforce_as_list_passing_predicate

if TYPE_CHECKING:
    from ansys.simai.core.data.geometries import Geometry


def _sweep(
    candidate_geometry: "Geometry",
    geometries: List["Geometry"],
    swept_metadata: Optional[Union[str, List[str]]] = None,
    fixed_metadata: Optional[List[str]] = None,
    order: Optional[int] = None,
    include_center: Optional[bool] = None,
    include_diagonals: Optional[bool] = None,
    tolerance: Optional[float] = None,
) -> List["Geometry"]:
    if order is None:
        order = 1
    if not isinstance(order, int):
        raise TypeError(f"The 'order' argument must be a positive integer (passed {order}).")
    if order < 1:
        raise ValueError(f"The 'order' argument must be a positive integer (passed {order}).")
    if tolerance is None:
        tolerance = DEFAULT_COMPARISON_EPSILON
    validate_tolerance_parameter(tolerance)

    if include_center is None:
        include_center = False
    if include_diagonals is None:
        include_diagonals = False

    if swept_metadata:
        swept_metadata = _enforce_as_list_passing_predicate(
            swept_metadata,
            lambda s: isinstance(s, str),
            """The 'swept_metadata' argument must be a geometry metadata name
            or a list of metadata names.
            """,
        )

        # Make sure all passed variables exist in geometry metadata
        # and that the data is numerical
        for variable in swept_metadata:
            if variable not in candidate_geometry.metadata:
                raise ValueError(f"Metadata {variable} not found in candidate geometry")
            if not is_number(candidate_geometry.metadata[variable]):
                raise ValueError(f"Metadata {variable} is not numerical")
    else:
        # No variable passed: use all numerical axes
        swept_metadata = [
            name
            for name in candidate_geometry.metadata
            if is_number(candidate_geometry.metadata[name])
        ]
        if len(swept_metadata) == 0:
            raise ValueError("No numerical metadata column found in candidate geometry")

    if fixed_metadata is None:
        fixed_metadata = []
    # consider swept variables as fixed
    eventually_fixed_metadata = list(set(fixed_metadata + swept_metadata))

    # Collect geometries in a set,
    # as when using include_center, a same geometry can be collected
    # via multiple variables
    neighboring_geometries: Set["Geometry"] = set()

    # if include_diagonal, collect boundaries
    if include_diagonals:
        boundaries: Dict[str, Tuple[float, float]] = {}

    # Go through each variable to find neighbors for those
    for checked_variable in swept_metadata:
        candidate_value: float = candidate_geometry.metadata[checked_variable]  # type: ignore
        fixed_variables = [v for v in eventually_fixed_metadata if v != checked_variable]
        # 1. Find geometries whose metadata contain checked_variable
        # and match fixed values
        matching_geometries = [
            geometry
            for geometry in geometries
            if (
                checked_variable in geometry.metadata
                and _are_geometries_metadata_equal(
                    left_geometry=candidate_geometry,
                    right_geometry=geometry,
                    compared_variables=fixed_variables,
                )
            )
        ]
        # 2. Sort them by checked_variable, so they can be passed to groupby
        sorted_geometries: List[Geometry] = sorted(
            matching_geometries, key=lambda g: g.metadata[checked_variable]
        )
        # 2. Group into buckets of equal value.
        # Use itertools.groupby to group.
        # As we want equality with a tolerance,
        # also that candidate geometry is at the center of its bucket,
        # we need this custom comparator
        groupby_bucketizer = _ToleranceGrouper(
            # FIXME: fix the B023 issue
            key_func=lambda g: g.metadata[checked_variable],  # noqa: B023
            tolerance=tolerance,
            forced_central_value=candidate_value,
        )
        buckets = itertools.groupby(sorted_geometries, groupby_bucketizer)

        # 3. Now keep only as many smaller and bigger buckets as `order`.
        # Keep the central values if include_center is True.

        # Smaller neighbors are selected by a deque of max size=`order`:
        # we push in it all the smaller values; the deque
        # keeps only as many as we want (nb=`order`)
        smaller_groups = collections.deque([], order)
        # Bigger_geometries are collected in a list by counting directly
        equal_and_bigger_groups = []
        found_bigger_buckets = 0
        for bucket, geometry_group in buckets:
            if is_smaller_with_tolerance(bucket.center, candidate_value, tolerance=tolerance):
                # smaller: add to the deque
                smaller_groups.append((bucket, list(geometry_group)))
            elif is_equal_with_tolerance(bucket.center, candidate_value, tolerance=tolerance):
                # equal: only add if include_center
                if include_center:
                    equal_and_bigger_groups.append((bucket, list(geometry_group)))
            else:
                # bigger: add to equal_and_bigger_groups
                equal_and_bigger_groups.append((bucket, list(geometry_group)))
                found_bigger_buckets += 1
                if found_bigger_buckets >= order:
                    # we found as many bigger as we were looking for: stop
                    break
        # Store everything in neighboring_geometries
        if include_diagonals:
            min_boundary = None
            max_boundary = None
        for _bucket, geometry_group in itertools.chain(smaller_groups, equal_and_bigger_groups):
            neighboring_geometries.update(geometry_group)
            if include_diagonals:
                if min_boundary is None:
                    min_boundary = _bucket.center
                max_boundary = _bucket.center
        if include_diagonals:
            boundaries[checked_variable] = (min_boundary, max_boundary)
    if include_diagonals:
        # build the list of ranges matching all boundaries.
        # selected geometries must match all those ranges.
        all_ranges: Dict[str, Range] = {}
        for variable, (min_boundary, max_boundary) in boundaries.items():
            # If not include_center, we want the geometries
            # *not* to match the candidate's value.
            # Thus use the HollowRange to exclude it
            excluded_value: Optional[float] = None
            if not include_center:
                excluded_value = candidate_geometry.metadata[variable]
            all_ranges[variable] = _HollowRange(
                min=min_boundary,
                max=max_boundary,
                tolerance=tolerance,
                excluded_value=excluded_value,
            )

        # We loop again through all geometries
        # and select those matching both all limits on swept geometries
        # and fixed value
        for geometry in geometries:
            if geometry in neighboring_geometries:
                continue
            if not _geometry_matches_range_constraints(geometry, all_ranges):
                continue
            if not _are_geometries_metadata_equal(
                left_geometry=candidate_geometry,
                right_geometry=geometry,
                compared_variables=fixed_metadata,
            ):
                continue
            neighboring_geometries.add(geometry)

    return list(neighboring_geometries)


def _are_geometries_metadata_equal(
    left_geometry: "Geometry",
    right_geometry: "Geometry",
    compared_variables: List[str],
    tolerance: Optional[float] = None,
) -> bool:
    """Test if all compared metadata are equal between two geometries.

    If a metadata is absent, consider the comparison as false.

    Returns:
        ``True`` if the metadata are equal for considered columns.

    Raises:
        ValueError: If one considered column contains numerical
            data and the other column contains non-numerical data.
    """
    for variable in compared_variables:
        if variable not in left_geometry.metadata or variable not in right_geometry.metadata:
            return False
        left_val: float = left_geometry.metadata.get(variable)  # type: ignore
        right_val: float = right_geometry.metadata.get(variable)  # type: ignore
        if is_number(left_val) != is_number(right_val):
            raise ValueError("Mixed numerical and non-numerical values in metadata {variable}.")
        if is_number(left_val):
            if not is_equal_with_tolerance(left_val, right_val, tolerance=tolerance):
                return False
        else:
            if left_val != right_val:
                return False
    return True


def _geometry_matches_range_constraints(
    geometry: "Geometry", ranges: Optional[Dict[str, Range]] = None
) -> bool:
    if ranges is None:
        return True
    for metadata_name, range in ranges.items():
        value = geometry.metadata.get(metadata_name, None)
        if value is None:
            # this metadata is not filled for this geometry: no match
            return False
        if not is_number(value):
            # metadata is filled but is not a number: raise
            raise TypeError(
                """
                Range constraint can only be used
                on numerical metadata."""
            )
        if not range.match_value(value):
            return False
    return True
