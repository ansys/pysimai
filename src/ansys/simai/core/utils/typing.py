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

import typing as t

if t.TYPE_CHECKING:
    P = t.ParamSpec("P")
    T = t.TypeVar("T")


def steal_kwargs_type_on_method(
    original_fn: "t.Callable[P, t.Any]",
) -> "t.Callable[[t.Callable], t.Callable[t.Concatenate[t.Any, P], T]]":
    """Takes type hints from ``original_fn`` and apply them to the decorated method.
    The ``self`` argument of the method is typed ``Any``.
    """

    def return_func(func: "t.Callable[..., T]") -> "t.Callable[t.Concatenate[t.Any, P], T]":
        return t.cast("t.Callable[t.Concatenate[t.Any, P], T]", func)

    return return_func
