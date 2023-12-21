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
        """
        Run a post-processing on the given prediction.

        If the result of the requested post-processing already exists it will not be rerun.

        Args:
            prediction_id: id of the prediction on which to run the post-processing
            post_processing_type: the type of post-processing to run on the prediction
            params: Additional json parameters as dict if required

        Returns:
            Json with the created or existing post-processing
        """
        return self._post(
            f"predictions/{prediction_id}/post-processings/{post_processing_type}",
            json=params,
        )

    def get_post_processing_result(self, post_processing_id: str) -> Dict[str, Any]:
        """
        Get the result of a post-processing.

        Args:
            post_processing_id: id of the post-processing

        Returns:
            Json with the result of the post-processing
        """
        return self._get(f"post-processings/{post_processing_id}")

    def delete_post_processing(self, post_processing_id: str):
        """
        Delete the post-processing.

        Args:
            post_processing_id: id of the post-processing to delete

        Raises:
            NotFoundError: if a post-processing with this id is not found on the server.
        """
        return self._delete(
            f"post-processings/{post_processing_id}",
            return_json=False,
        )

    def get_post_processings_in_workspace(
        self, workspace_id: str, pp_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Get all the post-processings in the given workspace.

        Args:
            workspace_id: the id of the target workspace
            pp_type: Specify a type of post-processing to return, returns all of them if empty
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
        filters: Dict[str, Any] = {},
    ) -> List[Dict[str, Any]]:
        """
        Get all the post-processings belonging to the given prediction.

        Args:
            prediction_id: the id of the target prediction
            pp_type: Specify a type of post-processing to return, returns all of them if empty
            filters: the filters to apply to the query
        """
        endpoint = f"predictions/{prediction_id}/post-processings/"
        if pp_type:
            endpoint = endpoint + pp_type
        params = {"filters": json.dumps(filters)} if filters else None
        return self._get(endpoint, params=params)

    def post_processings_export_url(self):
        return self.build_full_url_for_endpoint("post-processings/export")
