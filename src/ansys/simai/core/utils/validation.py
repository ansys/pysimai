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

from typing import Any, Callable, List, TypeVar, Union

T = TypeVar("T")


def _list_elements_pass_predicate(items_list: List[T], predicate: Callable[[Any], bool]) -> bool:
    return isinstance(items_list, List) and all(predicate(item) for item in items_list)


def _enforce_as_list_passing_predicate(
    parameter: Union[T, List[T]], predicate: Callable[[Any], bool], error_message: str
) -> List[T]:
    """
    Makes sure the passed parameter either is a single element passing predicate,
    or is a list of elements all passing predicate.
    In both case return a list.
    If other cases, raises a TypeError with error_message.

    Useful for validating a type of parameter, i.e. either accept a Geometry
    or a list of Geometries.
    """
    if predicate(parameter):
        return [parameter]
    if _list_elements_pass_predicate(parameter, predicate):
        return parameter
    raise TypeError(error_message)
