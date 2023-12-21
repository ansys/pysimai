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

from typing import TYPE_CHECKING, Callable, Dict, Generic, List, Optional, TypeVar, Union
import warnings

from ansys.simai.core.data.downloads import DownloadableResult
from ansys.simai.core.data.post_processings import PostProcessing

if TYPE_CHECKING:
    from ansys.simai.core.data.predictions import Prediction
    from ansys.simai.core.data.selections import Selection

from ansys.simai.core.errors import InvalidArguments, _foreach_despite_errors, _map_despite_errors

T = TypeVar("T", bound=PostProcessing)


class PPList(List, Generic[T]):
    """A subclass of :class:`list` for storing post-processings,
    adding a few shortcut methods.

    As a :class:`list` subclass, PPList support any list operation:
    its elements can be iterated on and accessed by index."""

    def __init__(self, selection: "Selection", post: Callable[["Prediction"], PostProcessing]):
        self._selection = selection
        # Even in case of errors, all post-processings will be queued.
        # but if some fail, an exception will be raised.
        post_processings = _map_despite_errors(lambda pred: post(pred), self._selection.predictions)
        super().__init__(post_processings)

    @property
    def data(self) -> Union[List[Dict[str, List]], List[DownloadableResult]]:
        """Returns a list containing the data of the underlying post-processings.

        This is a blocking method, which will return once the data of all
        post-processings is ready.
        """
        return [pp.data for pp in self]

    def wait(self):
        """Wait for all concerned post-processings to finish"""
        _foreach_despite_errors(lambda pp: pp.wait(), self)


class ExportablePPList(PPList, Generic[T]):
    """A subclass of :class:`PPList` allowing to download the results of a group of post-processings.

    As a :class:`list` subclass, ExportablePPList support any list operation:
        its elements can be iterated on and accessed by index.
    """

    def export(self, format: Optional[str] = "json") -> DownloadableResult:
        """
        Exports the post-processings results in the desired format.

        Accessing this property will block until the data is ready.

        Args:
            format: format in which the data is to be exported:
                one of ``json``, ``csv.zip`` or ``xlsx``, defaults to ``json``.
                Please note that ``csv.zip`` exports a zip archive containing
                multiple csv sheets.

        Returns:
            A :class:`~ansys.simai.core.data.downloads.DownloadableResult` object allowing
            to download the exported data into a file
            or access it in memory.
        """
        if not format in ["json", "csv.zip", "xlsx", "csv"]:
            raise InvalidArguments(
                f"Export format must be among json, csv.zip, xlsx (passed {format})."
            )
        if format == "csv":
            warnings.warn(
                "csv format will be deprecated, use csv.zip instead",
                PendingDeprecationWarning,
            )
        if len(self) < 1:
            raise InvalidArguments("Selection contains no exportable post-processing.")
        # Wait for all concerned post-processings to finish (and raise if errors)
        self.wait()
        client = self[0]._client
        return DownloadableResult(
            client._api.post_processings_export_url(),
            client,
            request_method="POST",
            request_json_body={"ids": [pp.id for pp in self], "format": format},
        )
