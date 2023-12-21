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

from semver.version import Version

from ansys.simai.core import __version__
from ansys.simai.core.api.client import ApiClient
from ansys.simai.core.data.design_of_experiments import DesignOfExperimentsCollection
from ansys.simai.core.data.geometries import GeometryDirectory
from ansys.simai.core.data.optimizations import OptimizationDirectory, OptimizationTrialRunDirectory
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
from ansys.simai.core.utils.typing import steal_kwargs_type

logger = logging.getLogger(__name__)


class SimAIClient:
    """
    A client to communicate with SimAI API.

    Keyword Args: see :class:`~ansys.simai.core.utils.configuration.ClientConfig`

    Example:
        .. code-block:: python

            from ansys.simai.core import SimAIClient

            simai = SimAIClient(
                organization="company_name", https_proxy="http://company_proxy:3128"
            )
    """

    @steal_kwargs_type(ClientConfig)
    def __init__(self, **kwargs):
        config = ClientConfig(**kwargs)

        api_client_class = getattr(config, "_api_client_class_override", ApiClient)
        self._api = api_client_class(simai_client=self, config=config)
        self._doe_collection = DesignOfExperimentsCollection(client=self)
        self._geometry_directory = GeometryDirectory(client=self)
        self._optimization_directory = OptimizationDirectory(client=self)
        self._optimization_trial_run_directory = OptimizationTrialRunDirectory(client=self)
        self._post_processing_directory = PostProcessingDirectory(client=self)
        self._project_directory = ProjectDirectory(client=self)
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

        if not config.skip_version_check:
            self._check_for_new_version()

    @property
    def current_workspace(self) -> Workspace:
        """
        The workspace currently used in the SDK session.

        Note:
            It is recommended not set this directly. Instead use the :meth:`set_current_workspace`
                method which uses the workspace name and also ensures the workspace exists.
        """
        if self._current_workspace is None:
            raise InvalidClientStateError("Current workspace is not set.")
        return self._current_workspace

    @current_workspace.setter
    def current_workspace(self, workspace: Workspace):
        self._current_workspace = workspace

    def set_current_workspace(self, name: str):
        """
        Set the current workspace for the SimAIClient.

        Args:
            name: The name of the workspace the client should switch to.

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
            logger.info(f"Workspace set to {name}")
        except NotFoundError:
            raise InvalidConfigurationError(
                f"""Configured workspace {name} does not exist on the server.
{self.available_workspaces_string}"""
            ) from None
        self._current_workspace = workspace

    @property
    def available_workspaces_string(self):
        available_workspaces = [workspace.name for workspace in self.workspaces.list()]
        return f"Available workspaces are: {available_workspaces}."

    @property
    def current_project(self) -> Project:
        """
        The project currently used in the SDK session.

        Note:
            It is recommended not set this directly. Instead use the :meth:`set_current_project`
                method which uses the project name and also ensures the project exists.
        """
        if self._current_project is None:
            raise InvalidClientStateError("Current project is not set.")
        return self._current_project

    @current_project.setter
    def current_project(self, project: Project):
        self._current_project = project

    def set_current_project(self, name: str):
        """
        Sets the current project for the SimAIClient.

        Affects how some methods related to projects or associated data will behave.

        Args:
            name: The name of the project the client should switch to.
        """
        try:
            # Ensure the project exists
            project = self.projects.get(name=name)
            logger.info(f"Project set to {name}")
        except NotFoundError:
            raise InvalidConfigurationError(
                f"""Configured project {name} does not exist on the server.
{self.available_projects_string}"""
            ) from None
        self._current_project = project

    @property
    def is_current_project_set(self) -> bool:
        return self._current_project is not None

    @property
    def available_projects_string(self):
        available_projects = [project.name for project in self.projects.list()]
        return f"Available projects are: {available_projects}."

    @property
    def geometries(self):
        """
        Representation of all geometries on the server.
        More details in the :doc:`geometries documentation <geometries>`.
        """
        return self._geometry_directory

    @property
    def optimizations(self):
        """
        Representation of all optimizations on the server.
        More details in the :doc:`optimization documentation <optimizations>`.
        """
        return self._optimization_directory

    @property
    def training_data(self):
        """
        Representation of all training data on the server
        More details in the :doc:`training data documentation<training_data>`.
        """
        return self._training_data_directory

    @property
    def training_data_parts(self):
        """
        Representation of all training data parts on the server
        More details in the :doc:`training data parts documentation<training_data_parts>`.
        """
        return self._training_data_part_directory

    @property
    def predictions(self):
        """
        Representation of all predictions on the server.
        More details in the :doc:`predictions documentation <predictions>`.
        """
        return self._prediction_directory

    @property
    def post_processings(self):
        """
        Representation of all post-processings on the server.
        More details in the :doc:`post-processings documentation <post_processings>`
        """
        return self._post_processing_directory

    @property
    def projects(self):
        """
        Representation of all projects on the server.
        More details in the :doc:`projects documentations <projects>`
        """
        return self._project_directory

    @property
    def design_of_experiments(self):
        """
        Methods allowing to export design of experiments
        More details in the :doc:`design of experiments documentation <design_of_experiments>`
        """
        return self._doe_collection

    @property
    def workspaces(self):
        """
        Representation of all workspaces on the server.
        More details in the :doc:`workspaces documentation <workspaces>`.
        """
        return self._workspace_directory

    @classmethod
    def from_config(
        cls,
        profile: str = "default",
        path: Optional[Path] = None,
        **kwargs,
    ) -> "SimAIClient":
        """
        Initialize an `SimAIClient` by reading a configuration file.

        You can provide the path of the config to load. If no path is given it will look
        at default locations.

        For more information on the configuration, see :ref:`Configuration File<config_file>`.

        ``kwargs`` can be used to override part of the configuration.

        Args:
            profile: The profile to load from the configuration, the `default` profile
                will be loaded if not provided
            path: The path at which the configuration is located.

        Returns:
            A configured client.

        Raises:
            ConfigurationNotFoundError: No configuration file was found at the given location
                or defaults location if no path was given.
            InvalidConfigurationError: The configuration is invalid or incomplete.

        Example:
            After setting up your :ref:`configuration file.<config_file>`

            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core_from_config()

        .. note:: The default paths are only supported on Unix systems.
        """
        return cls(**get_config(path, profile, **kwargs))

    def wait(self) -> None:
        """
        Wait for all the ongoing operations
        on locally known predictions and post-processings
        to finish.


        Raises:
            :exception:`SimAIError`: if something went wrong on an operation.
            :exception:`MultipleErrors`: if things when wrong on multiple operations
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

    def _check_for_new_version(self, client_name="ansys.simai.core", current_version=__version__):
        try:
            latest_version = self._api._get(f"info/{client_name}/version")["version"]
            version_current = Version.parse(current_version)
            version_latest = Version.parse(latest_version)
        except (SimAIError, ValueError):
            pass
        else:
            if version_current < version_latest:
                warn_template = (
                    f"A new version of {client_name} is %s. "
                    "Please upgrade to get new features and ensure compatibility with the server."
                )
                if (
                    version_current.major < version_latest.major
                    or version_current.minor < version_latest.minor
                ):
                    raise SimAIError(warn_template % "required")
                else:
                    logger.warning(warn_template % "available")


from_config = SimAIClient.from_config
