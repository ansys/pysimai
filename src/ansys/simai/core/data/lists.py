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

import warnings
from typing import TYPE_CHECKING, Callable, Dict, Generic, List, Optional, TypeVar, Union

from ansys.simai.core.data.downloads import DownloadableResult
from ansys.simai.core.data.post_processings import PostProcessing

if TYPE_CHECKING:
    from ansys.simai.core.data.predictions import Prediction
    from ansys.simai.core.data.selections import Selection

from ansys.simai.core.errors import InvalidArguments, _foreach_despite_errors, _map_despite_errors

T = TypeVar("T", bound=PostProcessing)


class PPList(List, Generic[T]):
    """Provides a subclass of the :class:`list` class for storing postprocessings and adding a few shortcut methods.

    As a :class:`list` subclass, the ``PPList`` class supports any list operation.
    Its elements can be iterated on and accessed by index.
    """

    def __init__(self, selection: "Selection", post: Callable[["Prediction"], PostProcessing]):  # noqa: D107
        self._selection = selection
        # Even in case of errors, all post-processings will be queued.
        # but if some fail, an exception will be raised.
        post_processings = _map_despite_errors(lambda pred: post(pred), self._selection.predictions)
        super().__init__(post_processings)

    @property
    def data(self) -> Union[List[Dict[str, List]], List[DownloadableResult]]:
        """List containing the data of the underlying postprocessings.

        This is a blocking method, which returns once the data of all
        postprocessings is ready.
        """
        return [pp.data for pp in self]

    def wait(self):
        """Wait for all concerned postprocessings to finish."""
        _foreach_despite_errors(lambda pp: pp.wait(), self)


class ExportablePPList(PPList, Generic[T]):
    """Provides a subclass of the :class:`PPList` class for downloading the results of a group of postprocessings.

    As a :class:`list` subclass, the ``ExportablePPList`` class supports any list operation.
    Its elements can be iterated on and accessed by index.
    """

    def export(self, format: Optional[str] = "json") -> DownloadableResult:
        """Export the postprocessing results in the desired format.

        Accessing this property blocks until the data is ready.

        Args:
            format: format to exported data in. The default is ``'json'``.
                Options are ``'csv.zip'``, ``'json'``, and ``'xlsx'``.
                Note that the ``'csv.zip'`` option exports a ZIP file containing
                multiple CSV sheets.

        Returns:
            :class:`~ansys.simai.core.data.downloads.DownloadableResult` object for
            downloading the exported data into a file or access it in memory.
        """
        if format not in ["json", "csv.zip", "xlsx", "csv"]:
            raise InvalidArguments(
                f"Export format must be json, csv.zip, or xlsx (passed {format})."
            )
        if format == "csv":
            warnings.warn(
                "The ``csv`` option is being deprecated. Use the ``csv.zip`` option instead",
                PendingDeprecationWarning,
                stacklevel=1,
            )
        if len(self) < 1:
            raise InvalidArguments("Selection contains no exportable postprocessing.")
        # Wait for all concerned post-processings to finish (and raise if errors)
        self.wait()
        client = self[0]._client
        return DownloadableResult(
            client._api.post_processings_export_url(),
            client,
            request_method="POST",
            request_json_body={"ids": [pp.id for pp in self], "format": format},
        )
