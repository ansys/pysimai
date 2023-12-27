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

import io
import logging
from pathlib import Path
from typing import BinaryIO, Callable, Optional, Union

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.utils.files import file_path_to_obj_file
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

logger = logging.getLogger(__name__)


class PredictionClientMixin(ApiClientMixin):
    """Client for the Prediction ("/predictions") part of the API."""

    def predictions(self, workspace_id: str):
        """Get list of all predictions."""
        return self._get("predictions/", params={"workspace": workspace_id})

    def get_prediction(self, prediction_id: str):
        """Get information on a single prediction.

        Args:
            prediction_id: The id of the prediction to get
        """
        return self._get(f"predictions/{prediction_id}")

    def delete_prediction(self, prediction_id: str):
        """Delete a single prediction.

        Args:
            prediction_id: The id of the prediction to delete
        """
        return self._delete(
            f"predictions/{prediction_id}",
            params={"confirm": True},
            return_json=False,
        )

    def run_prediction(self, geometry_id: str, **kwargs):
        """Run a prediction on the given geometry

        Args:
            geometry_id: The id of the target geometry

        Keyword Args:
            boundary_conditions dict: The contrainsts of the problem in dictionary form.
            tolerance float: The delta under which two boundary condition components are considered equal, default is 10**-6
        """
        return self._post(f"geometries/{geometry_id}/predictions", json=kwargs)

    def send_prediction_feedback(
        self,
        prediction_id: str,
        rating: int,
        comment: str,
        solution: Optional[Union[BinaryIO, str, Path]] = None,
        monitor_callback: Optional[Callable[[int], None]] = None,
    ):
        """Args:
        prediction_id: Id of the target prediction
        rating: A rating from 0 to 4
        comment: Additional comment
        solution: The client
            solution to the prediction
        monitor_callback: Function or method that will be passed
            a :py:class:`~requests_toolbelt.multipart.encoder.MultipartEncoderMonitor`
        """
        if solution is None:
            with_solution = False
            close_file = False
        else:
            if isinstance(solution, (Path, str)):
                solution_file = file_path_to_obj_file(solution, "rb")
                close_file = True
            elif isinstance(solution, (io.RawIOBase, io.BufferedIOBase)):
                solution_file = solution
                close_file = False
            else:
                raise ValueError(
                    "Could not handle the provided solution." " Please use a path or binary file."
                )
            with_solution = True
        upload_form = {"rating": str(rating), "comment": comment}
        if with_solution:
            upload_form["solution"] = (
                "solution",
                solution_file,
                "application/octet-stream",
            )
        multipart = MultipartEncoder(upload_form)
        if monitor_callback is not None:
            multipart = MultipartEncoderMonitor(multipart, monitor_callback)

        self._post(
            f"predictions/{prediction_id}/feedback",
            data=multipart,
            headers={"Content-Type": multipart.content_type},
        )
        if close_file is True:
            solution_file.close()
