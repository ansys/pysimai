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


import pytest

from ansys.simai.core.data.model_configuration import ModelConfiguration, SupportedBuildPresets
from ansys.simai.core.errors import InvalidArguments


def test_build_preset_error(simai_client):
    """WHEN build_preset gets a non-supported value
    THEN an InvalidArgument is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
    }

    project = simai_client._project_directory._model_from(raw_project)

    with pytest.raises(InvalidArguments) as excinfo:
        ModelConfiguration(
            project=project,
            build_preset="not_valid_value",
        )

        assert f"{list(SupportedBuildPresets)}" in excinfo.value


def test_model_input_not_none(simai_client):
    """WHEN ModelConfiguration.input gets a None value
    THEN an InvalidArgument is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
    }

    project = simai_client._project_directory._model_from(raw_project)

    bld_conf = ModelConfiguration(
        project=project,
    )

    with pytest.raises(InvalidArguments):
        bld_conf.input = None


def test_model_output_not_none(simai_client):
    """WHEN ModelConfiguration.input gets a None value
    THEN an InvalidArgument is raised."""

    raw_project = {
        "id": "xX007Xx",
        "name": "fifi",
    }

    project = simai_client._project_directory._model_from(raw_project)

    bld_conf = ModelConfiguration(
        project=project,
    )

    with pytest.raises(InvalidArguments):
        bld_conf.output = None
