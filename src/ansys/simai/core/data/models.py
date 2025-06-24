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


from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.model_configuration import ModelConfiguration
from ansys.simai.core.errors import InvalidArguments


class Model(ComputableDataModel):
    """Training model representation."""

    def __repr__(self) -> str:
        return f"<Model: {self.id}>"

    @property
    def project_id(self) -> str:
        """The ID of the project where the model exists."""
        return self.fields["project_id"]

    @property
    def configuration(self) -> ModelConfiguration:
        """Build configuration of a model."""
        return ModelConfiguration._from_payload(
            project=self._client.projects.get(self.fields["project_id"]),
            **self.fields["configuration"],
        )


class ModelDirectory(Directory[Model]):
    """Provides a collection of methods related to building models."""

    _data_model = Model

    def get(self, model_id: str) -> Model:
        """[Do not use] Get a model by ID.

        Args:
            model_id: ID of the model.
        """

        raise NotImplementedError("The method 'get' of the class Model is not implemented yet.")

    def build(
        self,
        configuration: ModelConfiguration,
        dismiss_data_with_fields_discrepancies: bool = False,
        dismiss_data_with_volume_overflow: bool = False,
        dismiss_data_input_with_nan: bool = False,
    ):
        """Launches a build given a configuration.

        Args:
            configuration: a ModelConfiguration object that contains the properties to be used in the build
            dismiss_data_with_fields_discrepancies: set to True for omitting data with missing properties
            dismiss_data_with_volume_overflow: set to True for omitting data outside the Domain of Analysis
            dismiss_data_input_with_nan: set to True for omitting data with inputs containing NaN values

        Example:
            Use a previous configuration for a new build in the same project

            .. code-block:: python

                a_project = simai.projects.get("project_A")

                build_conf = a_project.last_model_configuration

                new_model = simai.models.build(build_conf)

            Use a previous configuration for a new build in another project

            .. code-block:: python

                a_project = simai.projects.get("project_A")

                build_conf = a_project.last_model_configuration

                b_project = simai.projects.get("project_B")

                # set the id of b_project as the project_id of the configuration
                build_conf.project = b_project

                new_model = simai.models.build(build_conf)

        """
        if not configuration.project:
            raise InvalidArguments("The model configuration does not have a project set")

        is_trainable = configuration.project.is_trainable()
        if not is_trainable:
            raise InvalidArguments(f"Cannot train model because: {is_trainable.reason}")

        if configuration.build_on_top:
            response = self._client._api.launch_build_on_top(
                configuration.project.id,
                dismiss_data_with_fields_discrepancies,
                dismiss_data_with_volume_overflow,
                dismiss_data_input_with_nan,
            )
        else:
            response = self._client._api.launch_build(
                configuration.project.id,
                configuration._to_payload(),
                dismiss_data_with_fields_discrepancies,
                dismiss_data_with_volume_overflow,
                dismiss_data_input_with_nan,
            )
        return self._model_from(response)
