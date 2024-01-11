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

import math
from numbers import Number
from typing import Any, Optional, Tuple

DEFAULT_COMPARISON_EPSILON = 10**-6


def is_number(value: Any):
    return isinstance(value, Number) and not math.isnan(value)


def is_smaller_with_tolerance(a: float, b: float, tolerance: Optional[float] = None):
    """Run the `less than`(<) comparison with a tolerance.

    The default for the tolerance is ``.000001``.

    If the difference between the two numbers is less
    than the tolerance, ``a`` is considered equal, not smaller.
    """
    if tolerance is None:
        tolerance = DEFAULT_COMPARISON_EPSILON
    return a < b - tolerance


def is_bigger_with_tolerance(a: float, b: float, tolerance: Optional[float] = None):
    """Run the `greater than` (>) comparison with a tolerance.

    The default for the tolerance is ``.000001``.

    If the difference between the two numbers is greater
    than the tolerance, ``b`` is considered equal, not larger.
    """
    if tolerance is None:
        tolerance = DEFAULT_COMPARISON_EPSILON
    return a > b + tolerance


def is_smaller_or_equal_with_tolerance(a: float, b: float, tolerance: Optional[float] = None):
    """Run the `less than or equal to` (<=) comparison with a tolerance.

    The default for the tolerance is ``.000001``.

    If the difference between the two numbers is smaller
    than the tolerance, ``b`` is considered equal.
    """
    return not is_bigger_with_tolerance(a, b, tolerance)


def is_bigger_or_equal_with_tolerance(a: float, b: float, tolerance: Optional[float] = None):
    """Run the `greater than or equal to` (>=) comparison with a tolerance.

    The default for the tolerance is ``.000001``.

    If the difference between the two numbers is smaller
    than the tolerance, ``b`` is considered equal.
    """
    return not is_smaller_with_tolerance(a, b, tolerance)


def is_equal_with_tolerance(a: float, b: float, tolerance: Optional[float] = None):
    """Compare the equality of two numbers with a tolerance.

    The default toleranance is ``.000001``.

    If the difference between the two numbers is smaller
    than the tolerance, they are considered equal.
    """
    if tolerance is None:
        tolerance = DEFAULT_COMPARISON_EPSILON

    return abs(a - b) <= tolerance


def convert_axis_and_coordinate_to_plane_eq_coeffs(
    axis: str, coordinate: float
) -> Tuple[float, float, float, float]:
    default_coeffs = [0, 0, 0, coordinate]
    if axis == "x":
        default_coeffs[0] = 1
    elif axis == "y":
        default_coeffs[1] = 1
    elif axis == "z":
        default_coeffs[2] = 1
    return tuple(default_coeffs)


def validate_tolerance_parameter(tolerance: Optional[Number]):
    if tolerance is None:
        return
    if not is_number(tolerance):
        raise TypeError(f"The tolerance argument must be a number >= 0 (passed {tolerance})")
    if tolerance < 0:
        raise ValueError(f"The tolerance argument must be a number >= 0 (passed {tolerance})")
