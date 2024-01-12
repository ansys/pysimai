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
import logging
from typing import Any, Dict, List, Optional

from ansys.simai.core.api.mixin import ApiClientMixin

logger = logging.getLogger(__name__)


class PostProcessingClientMixin(ApiClientMixin):
    def run_post_processing(
        self,
        prediction_id: str,
        post_processing_type: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run a postprocessing on the given prediction.

        If the result of the requested postprocessing already exists, the postprocessing
        is not rerun.

        Args:
            prediction_id: ID of the prediction.
            post_processing_type: Type of postprocessing to run on the prediction.
            params: Additional JSON parameters as dictionary if required.

        Returns:
            JSON with the created or existing postprocessing.
        """
        return self._post(
            f"predictions/{prediction_id}/post-processings/{post_processing_type}",
            json=params,
        )

    def get_post_processing_result(self, post_processing_id: str) -> Dict[str, Any]:
        """Get the result of a postprocessing.

        Args:
            post_processing_id: ID of the postprocessing.

        Returns:
            JSON with the result of the postprocessing.
        """
        return self._get(f"post-processings/{post_processing_id}")

    def delete_post_processing(self, post_processing_id: str):
        """Delete a postprocessing.

        Args:
            post_processing_id: ID of the postprocessing.

        Raises:
            NotFoundError: If a postprocessing with this ID is not found on the server.
        """
        return self._delete(
            f"post-processings/{post_processing_id}",
            return_json=False,
        )

    def get_post_processings_in_workspace(
        self, workspace_id: str, pp_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get all postprocessings in the given workspace.

        Args:
            workspace_id: ID of the target workspace.
            pp_type: Type of postprocessings to return. If this parameter is empty, all
            postprocessings are returned.
        """
        endpoint = f"post-processings/type/{pp_type}" if pp_type else "post-processings/"
        # The content of this endpoint can be paginated
        initial_request = self._get(endpoint, params={"workspace": workspace_id}, return_json=False)
        pagination_info = json.loads(initial_request.headers.get("X-Pagination", "{}"))
        post_processings = initial_request.json()

        for page in range(2, pagination_info.get("total_pages", 1) + 1):
            page_request = self._get(endpoint, params={"workspace": workspace_id, "page": page})
            post_processings.extend(page_request)
        return post_processings

    def get_post_processings_for_prediction(
        self,
        prediction_id: str,
        pp_type: Optional[str],
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all postprocessings belonging to the given prediction.

        Args:
            prediction_id: ID of the target prediction.
            pp_type: Type of postprocessings to return. If this parameter is empty, all
                postprocessings are returned.
            filters: Filters to apply to the query, if any.
        """
        endpoint = f"predictions/{prediction_id}/post-processings/"
        if pp_type:
            endpoint = endpoint + pp_type
        params = {"filters": json.dumps(filters)} if filters else None
        return self._get(endpoint, params=params)

    def post_processings_export_url(self):
        return self.build_full_url_for_endpoint("post-processings/export")
