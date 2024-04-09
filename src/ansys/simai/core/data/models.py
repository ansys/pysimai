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

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from ansys.simai.core.data.base import ComputableDataModel, Directory


@dataclass
class BuildConfiguration:
    """Build configuration."""

    boundary_conditions: Dict[str, Any] = None
    build_preset: str = None
    continuous: bool = False
    fields: Dict[str, Any] = None
    global_coefficients: List[Dict[str, Any]] = None
    simulation_volume: Dict[str, Any] = None
    project_id: str = None


class Model(ComputableDataModel):
    """Training model representation."""

    def __repr__(self) -> str:
        return f"<Model: {self.id}>"

    @property
    def configuration(self):
        """The build configuration of model."""
        return BuildConfiguration(**self.fields["configuration"])


class ModelDirectory(Directory[Model]):
    """Provides a collection of methods related to training models."""

    _data_model = Model

    def get(self, project_id: str) -> Model:
        """Get a model by project ID.

        Args:
            project_id: ID of the project.
        """

        return self._model_from(self._client._api.get_model(project_id))

    def build(
        self,
        configuration: BuildConfiguration,
        dismiss_data_with_fields_discrepancies: bool = False,
        dismiss_data_with_volume_overflow: bool = False,
    ):
        """Launches a build given a configuration."""
        build_conf = asdict(configuration)
        project_id = build_conf.pop("project_id")
        return self._model_from(
            self._client._api.launch_build(
                project_id,
                build_conf,
                dismiss_data_with_fields_discrepancies,
                dismiss_data_with_volume_overflow,
            )
        )
