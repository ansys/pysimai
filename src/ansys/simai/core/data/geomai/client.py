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
import logging
from typing import TYPE_CHECKING

from ansys.simai.core.data.geomai.models import GeomAIModelDirectory
from ansys.simai.core.data.geomai.predictions import GeomAIPredictionDirectory
from ansys.simai.core.data.geomai.projects import GeomAIProject, GeomAIProjectDirectory
from ansys.simai.core.data.geomai.training_data import GeomAITrainingDataDirectory
from ansys.simai.core.data.geomai.training_data_parts import GeomAITrainingDataPartDirectory
from ansys.simai.core.data.geomai.workspaces import GeomAIWorkspace, GeomAIWorkspaceDirectory
from ansys.simai.core.errors import (
    InvalidClientStateError,
    InvalidConfigurationError,
    NotFoundError,
)
from ansys.simai.core.utils.configuration import ClientConfig

if TYPE_CHECKING:
    from ansys.simai.core.client import SimAIClient


logger = logging.getLogger(__name__)


class GeomAIClient:
    def __init__(self, simai_client: "SimAIClient", config: ClientConfig):
        self.client = simai_client
        self._model_directory = GeomAIModelDirectory(client=simai_client)
        self._prediction_directory = GeomAIPredictionDirectory(client=simai_client)
        self._project_directory = GeomAIProjectDirectory(client=simai_client)
        self._workspace_directory = GeomAIWorkspaceDirectory(client=simai_client)
        self._training_data_directory = GeomAITrainingDataDirectory(client=simai_client)
        self._training_data_part_directory = GeomAITrainingDataPartDirectory(client=simai_client)
        self._current_workspace = None
        self._current_project = None
        if config.geomai_workspace is not None:
            self.set_current_workspace(config.geomai_workspace)
        if config.geomai_project is not None:
            self.set_current_project(config.geomai_project)

    @property
    def current_workspace(self) -> GeomAIWorkspace:
        """Workspace currently used by the GeomAI client.

        Note:
            You should not set the workspace directly. Instead, use the :meth:`set_current_workspace`
            method, which uses the workspace name and ensures that the workspace exists.
        """
        if self._current_workspace is None:
            raise InvalidClientStateError("Current workspace is not set.")
        return self._current_workspace

    @current_workspace.setter
    def current_workspace(self, workspace: GeomAIWorkspace):
        self._current_workspace = workspace

    def set_current_workspace(self, name: str):
        """Set the current workspace for the GeomAI client.

        Args:
            name: Name of the workspace that the client should switch to.
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
    def current_project(self) -> GeomAIProject:
        """Project currently used by the GeomAI client.

        Note:
            You should not set the project directly. Instead, use the :meth:`set_current_project`
            method, which uses the project name and ensures that the project exists.
        """
        if self._current_project is None:
            raise InvalidClientStateError("Current project is not set.")
        return self._current_project

    @current_project.setter
    def current_project(self, project: GeomAIProject):
        self._current_project = project

    def set_current_project(self, name: str):
        """Set the current project for the GeomAI client.

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
    def training_data(self) -> GeomAITrainingDataDirectory:
        """Representation of all GeomAI training data on the server.
        For more information, see :ref:`geomai_training_data`.
        """
        return self._training_data_directory

    @property
    def training_data_parts(self) -> GeomAITrainingDataPartDirectory:
        """Representation of all GeomAI training data parts on the server.
        For more information, see :ref:`geomai_training_data_parts`.
        """
        return self._training_data_part_directory

    @property
    def projects(self) -> GeomAIProjectDirectory:
        """Representation of all GeomAI projects on the server.
        For more information, see :ref:`geomai_projects`.
        """
        return self._project_directory

    @property
    def models(self) -> GeomAIModelDirectory:
        """Representation of all GeomAI models on the server.
        For more information, see :ref:`geomai_models`.
        """
        return self._model_directory

    @property
    def workspaces(self) -> GeomAIWorkspaceDirectory:
        """Representation of all GeomAI workspaces on the server.
        For more information, see :ref:`geomai_workspaces`.
        """
        return self._workspace_directory

    @property
    def predictions(self) -> GeomAIPredictionDirectory:
        """Representation of all GeomAI predictions on the server.
        For more information, see :ref:`geomai_predictions`.
        """
        return self._prediction_directory
