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

import pytest

from ansys.simai.core.errors import SimAIError
from ansys.simai.core.utils.numerical import (
    cast_values_to_float,
    convert_axis_and_coordinate_to_plane_eq_coeffs,
    is_bigger_or_equal_with_tolerance,
    is_bigger_with_tolerance,
    is_equal_with_tolerance,
    is_number,
    is_smaller_or_equal_with_tolerance,
    is_smaller_with_tolerance,
)


def test_is_number():
    assert is_number(0)
    assert is_number(3)
    assert is_number(-3)
    assert is_number(10**8)
    assert is_number(10**-7)
    assert not is_number(math.nan)
    assert not is_number(None)
    assert not is_number("10")
    assert not is_number([10])
    assert not is_number({10})
    assert not is_number({})


def test_is_equal_with_tolerance():
    assert not is_equal_with_tolerance(1, 3)
    assert not is_equal_with_tolerance(3, 1)
    assert not is_equal_with_tolerance(10**-4, 10**-3)
    assert not is_equal_with_tolerance(10**-3, 10**-4)
    assert not is_equal_with_tolerance(-3, -1)
    assert not is_equal_with_tolerance(-1, -3)
    assert is_equal_with_tolerance(0, 0)
    assert is_equal_with_tolerance(111, 111)

    # Test tolerance
    a = 55
    assert is_equal_with_tolerance(a - 10**-7, a)
    assert not is_equal_with_tolerance(a - 10**-5, a)
    assert is_equal_with_tolerance(a - 10**-5, a, tolerance=10**-4)

    assert is_equal_with_tolerance(a + 10**-7, a)
    assert not is_equal_with_tolerance(a + 10**-5, a)
    assert is_equal_with_tolerance(a + 10**-5, a, tolerance=10**-4)


def test_is_smaller_with_tolerance():
    assert is_smaller_with_tolerance(1, 3)
    assert not is_smaller_with_tolerance(3, 1)
    assert is_smaller_with_tolerance(10**-4, 10**-3)
    assert not is_smaller_with_tolerance(10**-3, 10**-4)
    assert is_smaller_with_tolerance(-3, -1)
    assert not is_smaller_with_tolerance(-1, -3)
    assert not is_smaller_with_tolerance(0, 0)
    assert not is_smaller_with_tolerance(111, 111)

    # Test tolerance
    a = 55
    assert not is_smaller_with_tolerance(a - 10**-7, a)
    assert is_smaller_with_tolerance(a - 10**-5, a)
    assert not is_smaller_with_tolerance(a - 10**-5, a, tolerance=10**-4)

    assert not is_smaller_with_tolerance(a + 10**-7, a)
    assert not is_smaller_with_tolerance(a + 10**-5, a)
    assert not is_smaller_with_tolerance(a + 10**-5, a, tolerance=10**-4)


def test_is_smaller_or_equal_with_tolerance():
    assert is_smaller_or_equal_with_tolerance(1, 3)
    assert not is_smaller_or_equal_with_tolerance(3, 1)
    assert is_smaller_or_equal_with_tolerance(10**-4, 10**-3)
    assert not is_smaller_or_equal_with_tolerance(10**-3, 10**-4)
    assert is_smaller_or_equal_with_tolerance(-3, -1)
    assert not is_smaller_or_equal_with_tolerance(-1, -3)
    assert is_smaller_or_equal_with_tolerance(0, 0)
    assert is_smaller_or_equal_with_tolerance(111, 111)

    # Test tolerance
    a = 55
    assert is_smaller_or_equal_with_tolerance(a - 10**-7, a)
    assert is_smaller_or_equal_with_tolerance(a - 10**-5, a)
    assert is_smaller_or_equal_with_tolerance(a - 10**-5, a, tolerance=10**-4)

    assert is_smaller_or_equal_with_tolerance(a + 10**-7, a)
    assert not is_smaller_or_equal_with_tolerance(a + 10**-5, a)
    assert is_smaller_or_equal_with_tolerance(a + 10**-5, a, tolerance=10**-4)


def test_is_bigger_with_tolerance():
    assert not is_bigger_with_tolerance(1, 3)
    assert is_bigger_with_tolerance(3, 1)
    assert not is_bigger_with_tolerance(10**-4, 10**-3)
    assert is_bigger_with_tolerance(10**-3, 10**-4)
    assert not is_bigger_with_tolerance(-3, -1)
    assert is_bigger_with_tolerance(-1, -3)
    assert not is_bigger_with_tolerance(0, 0)
    assert not is_bigger_with_tolerance(111, 111)

    # Test tolerance
    a = 55
    assert not is_bigger_with_tolerance(a - 10**-7, a)
    assert not is_bigger_with_tolerance(a - 10**-5, a)
    assert not is_bigger_with_tolerance(a - 10**-5, a, tolerance=10**-4)

    assert not is_bigger_with_tolerance(a + 10**-7, a)
    assert is_bigger_with_tolerance(a + 10**-5, a)
    assert not is_bigger_with_tolerance(a + 10**-5, a, tolerance=10**-4)


def test_is_bigger_or_equal_with_tolerance():
    assert not is_bigger_or_equal_with_tolerance(1, 3)
    assert is_bigger_or_equal_with_tolerance(3, 1)
    assert not is_bigger_or_equal_with_tolerance(10**-4, 10**-3)
    assert is_bigger_or_equal_with_tolerance(10**-3, 10**-4)
    assert not is_bigger_or_equal_with_tolerance(-3, -1)
    assert is_bigger_or_equal_with_tolerance(-1, -3)
    assert is_bigger_or_equal_with_tolerance(0, 0)
    assert is_bigger_or_equal_with_tolerance(111, 111)

    # Test tolerance
    a = 55
    assert is_bigger_or_equal_with_tolerance(a - 10**-7, a)
    assert not is_bigger_or_equal_with_tolerance(a - 10**-5, a)
    assert is_bigger_or_equal_with_tolerance(a - 10**-5, a, tolerance=10**-4)

    assert is_bigger_or_equal_with_tolerance(a + 10**-7, a)
    assert is_bigger_or_equal_with_tolerance(a + 10**-5, a)
    assert is_bigger_or_equal_with_tolerance(a + 10**-5, a, tolerance=10**-4)


def test_convert_axis_and_coordinate_to_plane_eq_coeffs():
    assert convert_axis_and_coordinate_to_plane_eq_coeffs("x", 10) == (1, 0, 0, 10)
    assert convert_axis_and_coordinate_to_plane_eq_coeffs("y", 10) == (0, 1, 0, 10)
    assert convert_axis_and_coordinate_to_plane_eq_coeffs("z", 10) == (0, 0, 1, 10)
    assert convert_axis_and_coordinate_to_plane_eq_coeffs("z", 100.5) == (
        0,
        0,
        1,
        100.5,
    )


def test_cast_values_to_float():
    input = {"convert": "NaN", "also_convert": "-inf"}
    output = cast_values_to_float(input)
    assert math.isnan(output["convert"])
    assert math.isinf(output["also_convert"])


def test_cast_values_to_float_invalid_type_raises():
    input = {"convert": "woops"}
    with pytest.raises(SimAIError):
        cast_values_to_float(input)
