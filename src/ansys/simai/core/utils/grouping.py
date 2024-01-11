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

from typing import Any, Callable, Optional

from ansys.simai.core.utils.numerical import is_equal_with_tolerance


class _ToleranceGroup:
    """Provides a group of approximately equal values,
    as returned by ``itertools.groupby`` when using ``_ToleranceGrouper``.

    Note that with the way ``itertools.groupby`` works,
    accessing the center should be done only after accessing (iterating) the bucket's elements.
    """

    def __init__(
        self,
        initial_value: float,
        forced_central_value: Optional[float],
        tolerance: Optional[float],
    ):
        self.min = initial_value
        self.center = initial_value
        self.forced_central_value = forced_central_value
        self.tolerance = tolerance
        self.center_is_fixed = False

    def matches(self, new_value):
        if not is_equal_with_tolerance(new_value, self.center, self.tolerance):
            # The new value is just too far
            return False
        if new_value == self.forced_central_value:
            # Accept forced value to current bucket only if it's at reach for min
            # (else, refuse new value in this bucket)
            return is_equal_with_tolerance(new_value, self.min, self.tolerance)
        # Value is at reach of center (and not forced to be a new center):
        # it's all good
        return True

    def collect_value(self, new_value):
        # Check if the new value can be its center:
        # it must be at reach of bucket min,
        # and current center must not be fixed
        if not self.center_is_fixed and is_equal_with_tolerance(
            self.min, new_value, self.tolerance
        ):
            self.center = new_value
        # Fix the center of this bucket if it's the forced center
        if new_value == self.forced_central_value:
            self.center_is_fixed = True


class _ToleranceGrouper:
    """Provides a grouping class destined to be used by ``itertools.groupby`` to create
    groups of approximately equal value (according to tolerance).

    The ``_ToleranceGrouper`` class is meant to be passed as `key` argument for ``itertools.groupby``.
    It creates buckets defined by a central value and contains all values around it, plus or minus
    the tolerance. Each bucket is an instance of the ``_ToleranceGroup`` class.

    Args:
        key_func: Optional function computing a key value for each passed element.
            If no element is passed, the element itself is used.
        tolerance: Optional tolerance. The default is ``10**-6``.
        forced_central_value: Optional value that is forced to be at the
            center of its group. This means that the group spans maximally
            from forced_central_value - tolerance to forced_central_value + tolerance.
    """

    def __init__(
        self,
        key_func: Optional[Callable[[Any], float]] = None,
        tolerance: Optional[float] = None,
        forced_central_value: Optional[float] = None,
    ):
        if key_func is None:
            # if none passed, use identity function
            self.key_func = lambda x: x
        else:
            self.key_func = key_func
        self.tolerance = tolerance
        self.forced_central_value = forced_central_value
        self.current_bucket: Optional[_ToleranceGroup] = None

    def __call__(self, item: Any) -> float:
        new_value: float = self.key_func(item)
        if self.current_bucket is None or not self.current_bucket.matches(new_value):
            # Create a new bucket
            self.current_bucket = _ToleranceGroup(
                new_value,
                forced_central_value=self.forced_central_value,
                tolerance=self.tolerance,
            )
        self.current_bucket.collect_value(new_value)

        # Return bucket, which is used by groupby
        # to group all values together
        return self.current_bucket
