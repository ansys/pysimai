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

from ansys.simai.core.api.design_of_experiments import DesignOfExperimentsMixin
from ansys.simai.core.api.geometry import GeometryClientMixin
from ansys.simai.core.api.optimization import OptimizationClientMixin
from ansys.simai.core.api.post_processing import PostProcessingClientMixin
from ansys.simai.core.api.prediction import PredictionClientMixin
from ansys.simai.core.api.project import ProjectClientMixin
from ansys.simai.core.api.sse import SSEMixin
from ansys.simai.core.api.training_data import TrainingDataClientMixin
from ansys.simai.core.api.training_data_part import TrainingDataPartClientMixin
from ansys.simai.core.api.workspace import WorkspaceClientMixin


class ApiClient(
    DesignOfExperimentsMixin,
    GeometryClientMixin,
    OptimizationClientMixin,
    PostProcessingClientMixin,
    ProjectClientMixin,
    PredictionClientMixin,
    SSEMixin,
    TrainingDataClientMixin,
    TrainingDataPartClientMixin,
    WorkspaceClientMixin,
):
    """Provides the low-level client that handles direct communication with the server."""
