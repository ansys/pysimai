# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.workspaces import GeomAIWorkspace


def test_geomai_workspace_download_mer(simai_client, httpx_mock):
    """WHEN downloading mer zip file
    THEN the content of the file matches the content of the response.
    """

    workspace: GeomAIWorkspace = simai_client.geomai._workspace_directory._model_from(
        {"id": "abc123", "name": "HL3"}
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://test.test/geomai/workspaces/{workspace.id}/model-evaluation-report",
        text="mer-geomai",
        status_code=200,
    )

    in_memory = workspace.download_model_evaluation_report()
    data_in_file = in_memory.readline()
    assert data_in_file.decode("ascii") == "mer-geomai"


def test_geomai_workspace_rename(simai_client, httpx_mock):
    workspace: GeomAIWorkspace = simai_client.geomai._workspace_directory._model_from(
        {"id": "0011", "name": "riri"}
    )

    httpx_mock.add_response(
        method="PATCH",
        url="https://test.test/geomai/workspaces/0011",
        status_code=204,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/workspaces/0011",
        json={"id": "0011", "name": "fifi"},
        status_code=200,
    )

    workspace.rename("fifi")
    assert workspace.name == "fifi"
