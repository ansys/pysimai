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
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import ansys.simai.core.client


class DesignOfExperimentsCollection:
    """Provides a collection of methods related to design of experiments.

    This class is accessed through ``client.design_of_experiments``.
    """

    def __init__(self, client: "ansys.simai.core.client.SimAIClient"):
        self._client = client

    def download(self, file: Union[str, Path], format: str = "xlsx") -> None:
        """Download the design of experiments data to the specified file or path.

        Args:
            file: Path of the file to put the content into.
            format: Expected format. The default is ``'xlsx'``. Options are ``'xlsx'``
                and ``'csv'``.

        Example:
            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                simai.design_of_experiments.download(file="~/exp_plan.xlsx", format="xlsx")
        """
        self._client._api.download_design_of_experiments(
            file, format, self._client.current_workspace.id
        )

    def in_memory(self, format: Optional[str] = "csv") -> io.BytesIO:
        """Load the design of experiments data in memory.

        Args:
            file: Path of the file to put the content into.
            format: Expected format. The default is ``'csv'``. Options are ``'xlsx'``
                and ``'csv'``.

        Returns:
            :class:`~io.BytesIO` object containing the design of experiments data.

        Example:
            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                data = simai.design_of_experiments.in_memory(format="csv")
                # Read data with CSV reader, ...
        """
        return self._client._api.download_design_of_experiments(
            None, format, self._client.current_workspace.id
        )
