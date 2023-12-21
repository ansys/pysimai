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
import tempfile

import responses


@responses.activate
def test_design_of_experiments_export_csv(simai_client):
    """
    WHEN Calling simai_client.design_of_experiments.in_memory with Format.CSV
    THEN a call is made to design-of-experiments/export?format=csv
    ALSO the returned content is loaded in a BytesIO object
    """
    responses.add(
        responses.GET,
        f"https://test.test/design-of-experiments/export?format=csv&workspace={simai_client.current_workspace.id}",
        body="this,is,a,plan",
        status=200,
    )

    xp_plan_data = simai_client.design_of_experiments.in_memory(format="csv")
    assert isinstance(xp_plan_data, BytesIO)
    data_line = xp_plan_data.readline()
    assert data_line.decode("ascii") == "this,is,a,plan"


@responses.activate
def test_design_of_experiments_export_excel(simai_client):
    """
    WHEN Calling design_of_experiments.download with Format.Excel
    THEN a call is made to /design-of-experiments/export?format=xlsx
    ALSO the returned content is written into the provided file
    """
    responses.add(
        responses.GET,
        f"https://test.test/design-of-experiments/export?format=xlsx&workspace={simai_client.current_workspace.id}",
        body=b"xp-plan-binary-data",
        status=200,
    )

    with tempfile.TemporaryFile() as tmp_file:
        simai_client.design_of_experiments.download(file=tmp_file, format="xlsx")
        tmp_file.seek(0)
        data_line = tmp_file.readline()
        assert data_line.decode("ascii") == "xp-plan-binary-data"
