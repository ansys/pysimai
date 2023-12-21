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

from typing import Any, Dict, Iterable, Optional

from ansys.simai.core.api.mixin import ApiClientMixin


class TrainingDataClientMixin(ApiClientMixin):
    def delete_training_data(self, id: str) -> None:
        self._delete(f"training_data/{id}", return_json=False)

    def get_training_data(self, id: str) -> Dict[str, Any]:
        return self._get(f"training_data/{id}")

    def iter_training_data(self) -> Iterable[Dict[str, Any]]:
        next_page = "training_data"
        while next_page:
            page_request = self._get(next_page, return_json=False)
            next_page = page_request.links.get("next", {}).get("url")
            yield from page_request.json()

    def create_training_data(self, name: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        args = {"name": name}
        if project_id:
            args["project"] = project_id
        return self._post(
            "training_data/",
            json=args,
        )

    def add_training_data_to_project(self, training_data_id: str, project_id: str):
        return self._put(
            f"training_data/{training_data_id}/project/{project_id}/association",
            return_json=False,
        )

    def remove_training_data_from_project(self, training_data_id: str, project_id: str):
        return self._delete(
            f"training_data/{training_data_id}/project/{project_id}/association",
            return_json=False,
        )

    def compute_training_data(self, training_data_id: str) -> None:
        self._post(f"training_data/{training_data_id}/compute")
