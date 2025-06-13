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
from typing import List, Optional

from pydantic import ValidationError

from ansys.simai.core import __version__
from ansys.simai.core.api.client import ApiClient
from ansys.simai.core.data.geomai.client import GeomAIClient
from ansys.simai.core.data.geometries import GeometryDirectory
from ansys.simai.core.data.global_coefficients_requests import ProcessGlobalCoefficientDirectory
from ansys.simai.core.data.models import ModelDirectory
from ansys.simai.core.data.optimizations import (
    OptimizationDirectory,
    _OptimizationTrialRunDirectory,
)
from ansys.simai.core.data.post_processings import PostProcessingDirectory
from ansys.simai.core.data.predictions import PredictionDirectory
from ansys.simai.core.data.projects import Project, ProjectDirectory
from ansys.simai.core.data.training_data import TrainingDataDirectory
from ansys.simai.core.data.training_data_parts import TrainingDataPartDirectory
from ansys.simai.core.data.types import Path
from ansys.simai.core.data.workspaces import Workspace, WorkspaceDirectory
from ansys.simai.core.errors import (
    InvalidClientStateError,
    InvalidConfigurationError,
    MultipleErrors,
    NotFoundError,
    SimAIError,
)
from ansys.simai.core.utils.config_file import get_config
from ansys.simai.core.utils.configuration import ClientConfig
from ansys.simai.core.utils.misc import notify_if_package_outdated
from ansys.simai.core.utils.typing import steal_kwargs_type_on_method

logger = logging.getLogger(__name__)


class SimAIClient:
    """Provides the client for communicating with the SimAI API.

    For keyword arguments, see the :class:`~ansys.simai.core.utils.configuration.ClientConfig` class.

    Example:
        .. code-block:: python

            from ansys.simai.core import SimAIClient

            simai = SimAIClient(
                organization="company_name", https_proxy="http://company_proxy:3128"
            )
    """

    @steal_kwargs_type_on_method(ClientConfig)
    def __init__(self, **kwargs):
        try:
            config = ClientConfig(**kwargs)
        except ValidationError as pydandic_exc:
            raise InvalidConfigurationError(pydandic_exc) from None

        api_client_class = getattr(config, "_api_client_class_override", ApiClient)
        self._api = api_client_class(simai_client=self, config=config)
        self._process_gc_formula_directory = ProcessGlobalCoefficientDirectory(client=self)
        self._geometry_directory = GeometryDirectory(client=self)
        self._optimization_directory = OptimizationDirectory(client=self)
        self._optimization_trial_run_directory = _OptimizationTrialRunDirectory(client=self)
        self._post_processing_directory = PostProcessingDirectory(client=self)
        self._project_directory = ProjectDirectory(client=self)
        self._model_directory = ModelDirectory(client=self)
        self._workspace_directory = WorkspaceDirectory(client=self)
        self._prediction_directory = PredictionDirectory(client=self)
        self._training_data_directory = TrainingDataDirectory(client=self)
        self._training_data_part_directory = TrainingDataPartDirectory(client=self)
        self._current_workspace = None
        self._current_project = None
        if config.workspace is not None:
            self.set_current_workspace(config.workspace)
        if config.project is not None:
            self.set_current_project(config.project)
        self._geomai_client = GeomAIClient(self, config)

        if not config.skip_version_check:
            self._check_for_new_version()

    @property
    def current_workspace(self) -> Workspace:
        """Workspace currently used by the SimAI client.

        Note:
            You should not set the workspace directly. Instead, use the :meth:`set_current_workspace`
            method, which uses the workspace name and ensures that the workspace exists.
        """
        if self._current_workspace is None:
            raise InvalidClientStateError("Current workspace is not set.")
        return self._current_workspace

    @current_workspace.setter
    def current_workspace(self, workspace: Workspace):
        self._current_workspace = workspace

    def set_current_workspace(self, name: str):
        """Set the current workspace for the SimAI client.

        Args:
            name: Name of the workspace that the client should switch to.

        Example:
            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config(workspace="old plane")
                simai.geometries.list()  # will list geometries belonging to the "old plane" workspace
                simai.set_current_workspace("new plane")
                simai.geometries.list()  # will list geometries belonging to the "new plane" workspace
        """
        try:
            # Ensure the workspace exists
            workspace = self.workspaces.get(name=name)
            logger.info(f"Workspace set to {name}.")
        except NotFoundError:
            raise InvalidConfigurationError(
                f"""Configured workspace {name} does not exist on the server.
{self._available_workspaces_string}"""
            ) from None
        self._current_workspace = workspace

    @property
    def _available_workspaces_string(self):
        available_workspaces = [workspace.name for workspace in self.workspaces.list()]
        return f"Available workspaces are: {available_workspaces}."

    @property
    def current_project(self) -> Project:
        """Project currently used by the SimAPI client.

        Note:
            You should not set the project directly. Instead, use the :meth:`set_current_project`
            method, which uses the project name and ensures that the project exists.
        """
        if self._current_project is None:
            raise InvalidClientStateError("Current project is not set.")
        return self._current_project

    @current_project.setter
    def current_project(self, project: Project):
        self._current_project = project

    def set_current_project(self, name: str):
        """Set the current project for the SimAI client.

        This method affects how some methods related to projects or associated
        data behave.

        Args:
            name: Name of the project that the client should switch to.
        """
        try:
            # Ensure the project exists
            project = self.projects.get(name=name)
            logger.info(f"Project set to {name}")
        except NotFoundError:
            raise InvalidConfigurationError(
                f"""Configured project {name} does not exist on the server.
{self._available_projects_string}"""
            ) from None
        self._current_project = project

    @property
    def _available_projects_string(self):
        available_projects = [project.name for project in self.projects.list()]
        return f"Available projects are: {available_projects}."

    @property
    def geometries(self):
        """Representation of all geometries on the server.
        For more information, see :ref:`geometries`.
        """
        return self._geometry_directory

    @property
    def optimizations(self):
        """Representation of all optimizations on the server.
        For more information, see :ref:`optimizations`.
        """
        return self._optimization_directory

    @property
    def training_data(self):
        """Representation of all training data on the server.
        For more information, see :ref:`training_data`.
        """
        return self._training_data_directory

    @property
    def training_data_parts(self):
        """Representation of all training data parts on the server.
        For more information, see :ref:`training_data_parts`.
        """
        return self._training_data_part_directory

    @property
    def predictions(self):
        """Representation of all predictions on the server.
        For more information, see :ref:`predictions`.
        """
        return self._prediction_directory

    @property
    def post_processings(self):
        """Representation of all postprocessings on the server.
        For more information, see :ref:`post_processings`.
        """
        return self._post_processing_directory

    @property
    def projects(self):
        """Representation of all projects on the server.
        For more information, see :ref:`projects`.
        """
        return self._project_directory

    @property
    def workspaces(self):
        """Representation of all workspaces on the server.
        For more information, see :ref:`workspaces`.
        """
        return self._workspace_directory

    @property
    def models(self):
        """Representation of all models on the server.
        For more information, see :ref:`models`.
        """
        return self._model_directory

    @property
    def geomai(self) -> GeomAIClient:
        """Access the GeomAI client."""
        return self._geomai_client

    @classmethod
    def from_config(
        cls,
        profile: str = "default",
        path: Optional[Path] = None,
        **kwargs,
    ) -> "SimAIClient":
        """Initializes a SimAI client by reading a configuration file.

        You can provide the path of the configuration file to load. If no path is
        given, this method looks at the default locations.

        For more information, see :ref:`Configuration file<config_file>`.

        You can use ``kwargs`` to override part of the configuration.

        Args:
            profile: Profile to load from the configuration file. The default profile
                is loaded if no profile is provided.
            path: Path for the configuration file.
            **kwargs: Additional arguments to pass to the SimAI client.

        Returns:
            Configured client.

        Raises:
            ConfigurationNotFoundError: No configuration file was found at the given location
                or in the default profile if no path was given.
            InvalidConfigurationError: Configuration is invalid or incomplete.

        Example:
            Create the client after setting up your :ref:`configuration file.<config_file>`.

            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config()

        Note:
            The default paths are only supported on Unix systems.
        """
        return cls(**get_config(path, profile, **kwargs))

    def wait(self) -> None:
        """Wait for all ongoing operations on locally known predictions and postprocessings
        to finish.


        Raises:
            :exception:`SimAIError`: If something went wrong on an operation.
            :exception:`MultipleErrors`: If things went wrong on multiple operations.
        """
        errors: List[Exception] = []
        for directory in [self.predictions, self.post_processings]:
            logger.debug(f"waiting on {directory}")
            for local_object in directory._all_objects():
                try:
                    logger.debug(f"Waiting on {local_object._classname} id {local_object.id}")
                    local_object.wait()
                except Exception as e:
                    errors.append(e)
        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleErrors(errors)

    def _check_for_new_version(self) -> None:
        try:
            latest_version = self._api._get("https://pypi.org/pypi/ansys-simai-core/json")["info"][
                "version"
            ]
        except (SimAIError, KeyError) as e:
            logger.debug(f"Could not query package version on pypi: {e}")
            return None
        notify_if_package_outdated("ansys-simai-core", __version__, latest_version)


from_config = SimAIClient.from_config
