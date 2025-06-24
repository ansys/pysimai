# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

from typing import TYPE_CHECKING, Literal, Optional, Union

from pydantic import BaseModel, Field, ValidationError, model_validator

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.types import Identifiable, get_id_from_identifiable
from ansys.simai.core.errors import InvalidArguments

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.projects import GeomAIProject


class GeomAIModelConfiguration(BaseModel):
    nb_latent_param: int = Field(ge=2, le=256)
    """
    This number defines the number of floats that will be listed in the `latent_params` parameter for prediction.
    It has to be defined according to the complexity and the diversity of the geometries you used as training data.

    You need to find the smallest number of latent parameters enabling the model to rebuild
    a training data with a similar level of detail as the original geometry.

    - If the number is too low, the generated geometries will be too coarse.
    - If the number is too high, the model will not be able to generate consistent geometries.

    In most cases, the optimal number of latent parameters is lower than `20`.
    """
    build_preset: Optional[Literal["debug", "short", "default", "long"]] = None
    """
    The preset to use for the model training duration. One of `debug`, `short`, `default`, `long`.

    - `short` duration should last approximately 10 minutes.
    - `long` duration should last a few hours at most.

    Mutually exclusive with `nb_epochs`.
    """
    nb_epochs: Optional[int] = Field(default=None, ge=1, le=1000)
    """
    The number of times each training data is seen by the model during the training, between 1 and 1000.

    Mutually exclusive with `build_preset`.
    """

    def __init__(self, *args, **kwargs):
        """Raises :exc:`~ansys.simai.core.errors.InvalidArguments` if the input data cannot be validated to from a valid model."""
        try:
            super().__init__(*args, **kwargs)
        except ValidationError as e:
            raise InvalidArguments(e.errors(include_url=False)) from None

    @model_validator(mode="after")
    def _build_preset_or_nb_epochs(self) -> "GeomAIModelConfiguration":
        if (self.nb_epochs is None and self.build_preset is None) or (
            self.nb_epochs is not None and self.build_preset is not None
        ):
            raise ValueError("Exactly one of nb_epochs or build_preset must have a value")
        return self


class GeomAIModel(ComputableDataModel):
    """GeomAI model representation."""

    def __repr__(self) -> str:
        return f"<Model: {self.id}>"

    @property
    def project_id(self) -> str:
        """The ID of the GeomAI project where the model exists."""
        return self.fields["project_id"]

    @property
    def configuration(self) -> GeomAIModelConfiguration:
        """Build configuration of a model."""
        return GeomAIModelConfiguration.model_construct(
            **self.fields["configuration"],
        )


class GeomAIModelDirectory(Directory[GeomAIModel]):
    """Provides a collection of methods related to building models."""

    _data_model = GeomAIModel

    def get(self, id: str) -> GeomAIModel:
        """[Do not use] Get a GeomAI model by ID.

        Args:
            id: ID of the model.
        """

        raise NotImplementedError(
            "The method 'get' of the class GeomAIModel is not implemented yet."
        )

    def build(
        self,
        project: Identifiable["GeomAIProject"],
        configuration: Union[dict, GeomAIModelConfiguration],
    ) -> GeomAIModel:
        """Launches a GeomAI build with the given configuration.

        Args:
            project: The GeomAI project in which to run the training.
            configuration: a :class:`GeomAIModelConfiguration` object that contains the properties to be used in the build.

        Examples:
            .. code-block:: python

                import ansys.simai.core
                from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration

                simai = ansys.simai.core.from_config()
                project = simai.geomai.projects.get("new_secret_project")
                configuration = GeomAIModelConfiguration(build_preset="default", nb_latent_param=10)
                model = simai.geomai.models.build(project, configuration)


            Use a previous configuration for a new build in the same project:

            .. code-block:: python

                a_project = simai.geomai.projects.get("project_A")
                build_conf = a_project.last_model_configuration
                new_model = simai.geomai.models.build(build_conf)

            Use a previous configuration for a new build in another project:

            .. code-block:: python

                a_project = simai.geomai.projects.get("project_A")
                build_conf = a_project.last_model_configuration
                b_project = simai.geomai.projects.get("project_B")
                new_model = simai.geomai.models.build(build_conf)

        """
        project_id = get_id_from_identifiable(project)
        configuration = (
            configuration
            if isinstance(configuration, GeomAIModelConfiguration)
            else GeomAIModelConfiguration(configuration)
        )
        response = self._client._api.launch_geomai_build(
            project_id,
            configuration.model_dump(),
        )
        return self._model_from(response)
