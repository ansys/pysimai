# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

"""Utils for handling the API endpoints that support filters and sorting."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Any, Literal, TypedDict, Union

    _FilterOperator = Literal["EQ", "LIKE", "IN", "GT", "GTE", "LT", "LTE"]
    Filters = Union[
        # simple `eq` filters: dict(name="thingy")
        dict[str, Any],
        # more advanced, still simplified filters: [("name", "LIKE", "%thingy%"), ("name", "LIKE", "%thingo%")] (conditions are AND together)
        list[tuple[str, _FilterOperator, Any]],
    ]

    class _RawSingleFilter(TypedDict):
        field: str
        operator: _FilterOperator
        value: Any

    RawFilters = list[_RawSingleFilter]


def to_raw_filters(filters: Optional["Filters"]) -> Optional["RawFilters"]:
    if isinstance(filters, dict):
        return [{"field": k, "operator": "EQ", "value": v} for k, v in filters.items()]
    if isinstance(filters, list):
        return [{"field": fld, "operator": op, "value": val} for fld, op, val in filters]
