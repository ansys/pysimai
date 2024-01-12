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

from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, Optional

from ansys.simai.core.data.types import File

if TYPE_CHECKING:
    import ansys.simai.core.client


class DownloadableResult:
    """Provides the object representing a result data for a postprocessing in binary format."""

    def __init__(
        self,
        download_url: Optional[str],
        client: "ansys.simai.core.client.SimAIClient",
        request_method: str = "GET",
        request_json_body: Optional[Dict[str, Any]] = None,
    ):
        self.url = download_url
        self._client = client
        self._request_method = request_method
        self._request_json_body = request_json_body

    def download(self, file: File) -> None:
        """Download the postprocessing data to the specified file or path.

        Args:
            file: Binary file-object or path of the file to download the data into.
        """
        self._download_file(self.url, file)

    def in_memory(self) -> BytesIO:
        """Load the postprocessing data in memory.

        Returns:
            :class:`io.BytesIO` object containing the postprocessing data.
        """
        return self._download_file(self.url)

    def _download_file(self, url: str, file: Optional[File] = None) -> Optional[BytesIO]:
        return self._client._api.download_file(
            url,
            file,
            request_method=self._request_method,
            request_json_body=self._request_json_body,
        )
