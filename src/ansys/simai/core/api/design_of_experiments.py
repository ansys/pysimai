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
from typing import BinaryIO, Optional, Union

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.data.types import File

logger = logging.getLogger(__name__)


class DesignOfExperimentsMixin(ApiClientMixin):
    """Provides the client for the design of experiments ("/design-of-experiments/") part of the API."""

    def download_design_of_experiments(
        self,
        file: Optional[File],
        format: str,
        workspace_id: str,
    ) -> Union[None, BinaryIO]:
        """Downloads the design of experiments into the file at the given path.

        Args:
            file: Binary file-object or the path of the file to put the content into.
            format: Format to download. Options are ``'xlsx'`` or ``'csv'``.
            workspace_id: ID of the workspace to download the design of experiments for.

        Return:
            ``None`` if a file is provided or a ``BytesIO`` object with the content for
            the design of experiments otherwise.
        """
        logger.debug("Attempting to download design of experiments.")
        return self.download_file(
            f"design-of-experiments/export?format={format}&workspace={workspace_id}",
            file,
        )
