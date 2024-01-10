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

import logging

from ansys.simai.core.api.mixin import ApiClientMixin

logger = logging.getLogger(__name__)


class PredictionClientMixin(ApiClientMixin):
    """Provides the client for the Prediction ("/predictions") part of the API."""

    def predictions(self, workspace_id: str):
        """Get a list of all predictions."""
        return self._get("predictions/", params={"workspace": workspace_id})

    def get_prediction(self, prediction_id: str):
        """Get information on a single prediction.

        Args:
            prediction_id: ID of the prediction.
        """
        return self._get(f"predictions/{prediction_id}")

    def delete_prediction(self, prediction_id: str):
        """Delete a single prediction.

        Args:
            prediction_id: ID of the prediction.
        """
        return self._delete(
            f"predictions/{prediction_id}",
            params={"confirm": True},
            return_json=False,
        )

    def run_prediction(self, geometry_id: str, **kwargs):  # noqa: D417
        """Run a prediction on a given geometry.

        Args:
            geometry_id: ID of the target geometry.

        Keyword Arguments:
            boundary_conditions dict: Constraints of the problem in dictionary form.
            tolerance float: Delta under which two boundary condition components
                are considered equal. The default is ``10**-6``.
        """
        return self._post(f"geometries/{geometry_id}/predictions", json=kwargs)
