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

from typing import Any, Dict, Iterator
from urllib.parse import quote

from ansys.simai.core.api.mixin import ApiClientMixin


class ProjectClientMixin(ApiClientMixin):
    def projects(self):
        return self._get("projects")

    def get_project(self, id: str):
        return self._get(f"projects/{id}")

    def get_project_by_name(self, name: str):
        return self._get(f"projects/name/{quote(name)}")

    def create_project(self, **kwargs):
        return self._post("projects", json=kwargs)

    def update_project(self, project_id: str, name: str):
        """Update a project name.

        Args:
            project_id: ID of the project.
            name: New name to give to the project.
        """
        request_json = {}
        request_json["name"] = name
        self._patch(f"projects/{project_id}", json=request_json, return_json=False)

    def iter_training_data_in_project(self, project_id: str) -> Iterator[Dict[str, Any]]:
        next_page = f"projects/{project_id}/data"
        while next_page:
            page_request = self._get(next_page, return_json=False)
            next_page = page_request.links.get("next", {}).get("url")
            yield from page_request.json()

    def set_project_sample(self, project_id: str, training_data_id: str):
        self._put(
            f"projects/{project_id}/sample",
            json={"training_data": training_data_id},
            return_json=False,
        )

    def delete_project(self, project_id: str):
        self._delete(f"projects/{project_id}", return_json=False)

    def launch_build(
        self,
        project_id: str,
        config: Dict[str, Any],
        dismiss_data_with_fields_discrepancies: bool = False,
        dismiss_data_with_volume_overflow: bool = False,
    ):
        """Launches a build for a project and according to a given configuration.

        Args:
            project_id: the ID of the project
            config: the build configuration
            dismiss_data_with_fields_discrepancies: set to True for omitting data with missing properties
            dismiss_data_with_volume_overflow: set to True for omitting data outside the Domain of Analysis

        """
        params = {
            "dismiss_data_with_fields_discrepancies": dismiss_data_with_fields_discrepancies,
            "dismiss_data_with_volume_overflow": dismiss_data_with_volume_overflow,
        }
        return self._post(f"projects/{project_id}/model", json=config, params=params)

    def is_project_trainable(self, project_id: str):
        return self._get(f"projects/{project_id}/trainable")

    def check_formula(self, project_id: str, calculette_payload: Dict[str, Any]):
        """Verify the validity of a Global Coefficient formula.

        Args:
            project_id:         the ID of the project
            calculette_payload: the payload for calculette that includes the
                                formula that describes a Global Coefficient
        """

        return self._post(
            f"projects/{project_id}/check-formula",
            json=calculette_payload,
            return_json=False,
        )

    def compute_formula(self, project_id: str, calculette_payload: Dict[str, Any]):
        """Computes the result of a Global Coefficient formula according to the project's sample.

        Args:
            project_id:         the ID of the project
            calculette_payload: the payload for calculette that includes the
                                formula that describes a Global Coefficient
        """

        return self._post(
            f"projects/{project_id}/compute-formula",
            json=calculette_payload,
            return_json=False,
        )
