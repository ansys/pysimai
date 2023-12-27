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

import itertools

from ansys.simai.core.utils.grouping import _ToleranceGroup, _ToleranceGrouper
from ansys.simai.core.utils.numerical import is_equal_with_tolerance


def test_tolerance_grouper_basic():
    """WHEN using _ToleranceGrouper with a basic list and default or negligible tolerance,
    THEN each group contain distinct elements in the data list
    ALSO, forced_central_value has no effect.
    """
    data = [1, 1, 2, 3, 3, 3, 4, 5]
    for tolerance in [None, 10**-7, 10**-1]:
        for forced_central_value in [None, 2, 2.1, 22]:
            grouper = _ToleranceGrouper(
                forced_central_value=forced_central_value, tolerance=tolerance
            )
            result_groups = itertools.groupby(data, grouper)

            for i, group in enumerate(result_groups):
                num = i + 1
                bucket, items = group
                assert isinstance(bucket, _ToleranceGroup)
                assert bucket.center == num

                if num == 1:
                    assert list(items) == 2 * [num]
                elif num == 3:
                    assert list(items) == 3 * [num]
                else:
                    assert list(items) == [num]


def test_tolerance_grouper_tolerance():
    """WHEN using tolerance grouper with tolerance
    THEN groups of values that can all be grouped around a central value
    (approx. equal to this central value) are grouped together
    """
    data = [1, 1.001, 1.996, 2, 2.005, 4, 4, 4.005, 4.011, 4.019, 4.996, 5.002]
    tolerance = 10**-2
    grouper = _ToleranceGrouper(tolerance=tolerance)
    result_groups = itertools.groupby(data, grouper)

    for i, group in enumerate(result_groups):
        bucket, items = group
        assert isinstance(bucket, _ToleranceGroup)
        items = list(items)

        if i == 0:
            assert items == [1, 1.001]
            assert is_equal_with_tolerance(bucket.center, 1, tolerance=tolerance)
        elif i == 1:
            assert items == [1.996, 2, 2.005]
            assert is_equal_with_tolerance(bucket.center, 2, tolerance=tolerance)
        elif i == 2:
            # This bucket contains all those items,
            # as we can create a bucket around 4.005 : 4 ~= 4.005 ~= 4.011
            assert items == [4, 4, 4.005, 4.011]
            assert bucket.center == 4.005
        elif i == 3:
            assert items == [4.019]
            assert bucket.center == 4.019
        else:
            assert items == [4.996, 5.002]
            assert is_equal_with_tolerance(bucket.center, 5, tolerance=tolerance)


def test_tolerance_grouper_tolerance_with_forced_central_value():
    """WHEN using tolerance grouper with forced central value
    THEN those forced value must not be further than epsilon
        from their own bucket boundaries
    """
    data = [4, 4, 4.005, 4.011, 4.019]
    tolerance = 10**-2
    for forced_central_value in [4, 4.011]:
        grouper = _ToleranceGrouper(tolerance=tolerance, forced_central_value=forced_central_value)
        result_groups = itertools.groupby(data, grouper)

        for i, group in enumerate(result_groups):
            bucket, items = group
            assert isinstance(bucket, _ToleranceGroup)

            if i == 0:
                assert list(items) == [4, 4, 4.005]
                if forced_central_value == 4:
                    assert bucket.center == 4
            else:
                assert list(items) == [4.011, 4.019]
