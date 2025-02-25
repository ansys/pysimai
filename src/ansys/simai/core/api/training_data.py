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

import json
from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import urlencode

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.utils.pagination import PaginatedAPIRawIterator

if TYPE_CHECKING:
    from ansys.simai.core.data.types import RawFilters


class TrainingDataClientMixin(ApiClientMixin):
    def delete_training_data(self, id: str) -> None:
        self._delete(f"training-data/{id}", return_json=False)

    def get_training_data(self, id: str) -> Dict[str, Any]:
        return self._get(f"training-data/{id}")

    def iter_training_data(self, filters: Optional["RawFilters"]) -> PaginatedAPIRawIterator:
        query = urlencode(
            [("filter[]", json.dumps(f, separators=(",", ":"))) for f in (filters or [])]
        )
        return PaginatedAPIRawIterator(self, f"training-data?{query}")

    def create_training_data(self, name: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        args = {"name": name}
        if project_id:
            args["project"] = project_id
        return self._post(
            "training-data/",
            json=args,
        )

    def add_training_data_to_project(self, training_data_id: str, project_id: str):
        return self._put(
            f"training-data/{training_data_id}/project/{project_id}/association",
            return_json=False,
        )

    def remove_training_data_from_project(self, training_data_id: str, project_id: str):
        return self._delete(
            f"training-data/{training_data_id}/project/{project_id}/association",
            return_json=False,
        )

    def compute_training_data(self, training_data_id: str) -> None:
        self._post(f"training-data/{training_data_id}/compute")

    def get_training_data_subset(self, project_id: str, training_data_id: str) -> Dict[str, Any]:
        return self._get(f"projects/{project_id}/data/{training_data_id}/subset")

    def put_training_data_subset(
        self, project_id: str, training_data_id: str, subset: Optional[str]
    ) -> None:
        return self._put(
            f"projects/{project_id}/data/{training_data_id}/subset", json={"subset": subset}
        )
