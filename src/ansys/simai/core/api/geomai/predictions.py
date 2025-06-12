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

import logging
from typing import Dict, Optional

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.data.types import File

logger = logging.getLogger(__name__)


class GeomAIPredictionClientMixin(ApiClientMixin):
    """Provides the client for the Prediction ("/predictions") part of the API."""

    def geomai_predictions(self, workspace_id: str):
        """Get a list of all predictions in a workspace."""
        return self._get(f"geomai/workspaces/{workspace_id}/predictions")

    def get_geomai_prediction(self, prediction_id: str):
        """Get information on a single prediction.

        Args:
            prediction_id: ID of the prediction.
        """
        return self._get(f"geomai/predictions/{prediction_id}")

    def delete_geomai_prediction(self, prediction_id: str):
        """Delete a single prediction.

        Args:
            prediction_id: ID of the prediction.
        """
        return self._delete(
            f"predictions/{prediction_id}",
            return_json=False,
        )

    def run_geomai_prediction(self, workspace_id: str, configuration: Dict):  # noqa: D417
        return self._post(f"geomai/workspaces/{workspace_id}/predictions", json=configuration)

    def download_geomai_prediction(self, prediction_id: str, file: Optional[File]):
        return self.download_file(f"geomai/predictions/{prediction_id}/download", file)
