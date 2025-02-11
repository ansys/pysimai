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

from typing import Any, Dict, List, Tuple

from ansys.simai.core.api.mixin import ApiClientMixin


class TrainingDataPartClientMixin(ApiClientMixin):
    def create_training_data_part(
        self, training_data_id: str, name: str, extension: str
    ) -> Tuple[Dict[str, Any], str]:
        """Create a part under the given training data without uploading the data.

        Args:
            training_data_id: ID of the parent training data.
            name: Name of the part to create.
            extension: Extension of the file or part.

        Returns:
            Tuple containing the ``TrainingDataPart`` object and the upload ID
            to use for further requests.
        """
        post_data = {"name": name, "file_extension": extension}
        response = self._post(f"training-data/{training_data_id}/parts/", json=post_data)
        return (response["training_data_part"], response["upload_id"])

    def get_training_data_part(self, id: str) -> Dict[str, Any]:
        return self._get(f"training-data-parts/{id}")

    def complete_training_data_part_upload(
        self, id: str, upload_id: str, parts: List[Dict[str, Any]]
    ):
        self._post(
            f"training-data-parts/{id}/complete",
            json={"upload_id": upload_id, "parts": parts},
        )
