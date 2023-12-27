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
    """Collection of methods related to the whole Design of Experiments.
    Accessed through ``client.design_of_experiments``.
    """

    def __init__(self, client: "ansys.simai.core.client.SimAIClient"):
        self._client = client

    def download(self, file: Union[str, Path], format: str = "xlsx") -> None:
        """Downloads the design of experiments data to the specified file or path.

        Args:
            file: the path of the file to put the content into
            format: the expected format, either ``xlsx`` for excel or ``csv`` (by default ``xlsx``).

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
        """Loads the design of experiments data in memory.

        Args:
            file: the path of the file to put the content into
            format: the expected format, either ``xlsx`` for excel or ``csv`` (by default ``csv``).

        Returns:
            A :class:`~io.BytesIO` object containing the design of experiments data.

        Example:
            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                data = simai.design_of_experiments.in_memory(format="csv")
                # Read data with CSV Reader, ...
        """
        return self._client._api.download_design_of_experiments(
            None, format, self._client.current_workspace.id
        )
