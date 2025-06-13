# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

from typing import Any, Dict, Iterator
from urllib.parse import quote

from ansys.simai.core.api.mixin import ApiClientMixin


class GeomAIProjectClientMixin(ApiClientMixin):
    def geomai_projects(self):
        return self._get("geomai/projects")

    def get_geomai_project(self, id: str):
        return self._get(f"geomai/projects/{id}")

    def get_geomai_project_by_name(self, name: str):
        return self._get(f"geomai/projects/name/{quote(name)}")

    def create_geomai_project(self, **kwargs):
        return self._post("geomai/projects", json=kwargs)

    def update_geomai_project(self, project_id: str, name: str):
        request_json = {}
        request_json["name"] = name
        self._patch(f"geomai/projects/{project_id}", json=request_json, return_json=False)

    def iter_training_data_in_geomai_project(self, project_id: str) -> Iterator[Dict[str, Any]]:
        next_page = f"geomai/projects/{project_id}/training-data"
        while next_page:
            page_request = self._get(next_page, return_json=False)
            next_page = page_request.links.get("next", {}).get("url")
            yield from page_request.json()

    def delete_geomai_project(self, project_id: str):
        self._delete(f"geomai/projects/{project_id}", return_json=False)

    def get_geomai_project_related_workspaces(self, project_id: str):
        return self._get(f"geomai/projects/{project_id}/workspaces")

    def launch_geomai_build(
        self,
        project_id: str,
        config: Dict[str, Any],
    ):
        return self._post(f"geomai/projects/{project_id}/models", json=config)

    def cancel_geomai_build(self, project_id: str):
        return self._post(f"geomai/projects/{project_id}/cancel-training", return_json=False)
