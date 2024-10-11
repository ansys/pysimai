# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

from typing import TYPE_CHECKING

import responses

if TYPE_CHECKING:
    from ansys.simai.core.data.workspaces import Workspace


@responses.activate
def test_workspace_download_mer_data(simai_client):
    """WHEN downloading mer csv file
    THEN the content of the file matches the content of the response.
    """

    workspace: Workspace = simai_client._workspace_directory._model_from(
        {"id": "0011", "name": "riri"}
    )
    responses.add(
        responses.GET,
        f"https://test.test/workspaces/{workspace.id}/mer-data",
        body=b"mer-data-geometries",
        status=200,
    )

    in_memory = workspace.download_mer_data()
    data_in_file = in_memory.readline()
    assert data_in_file.decode("ascii") == "mer-data-geometries"
