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

import random

import pytest

from ansys.simai.core import SimAIClient
from ansys.simai.core.api.client import ApiClient
from ansys.simai.core.data.geometries import Geometry, GeometryDirectory
from ansys.simai.core.data.post_processings import PostProcessing, PostProcessingDirectory
from ansys.simai.core.data.predictions import Prediction
from ansys.simai.core.data.projects import Project
from ansys.simai.core.data.training_data import TrainingData
from ansys.simai.core.data.workspaces import Workspace
from ansys.simai.core.utils.configuration import ClientConfig


@pytest.fixture(scope="session")
def api_client():
    """A ApiClient object with bogus URL"""
    yield ApiClient(
        config=ClientConfig(
            url="https://test.test",
            _disable_authentication=True,
            no_sse_connection=True,
            organization="ExtraClaquette",
        )
    )


# warning: even with scope=function, the same SimAIClient is kept,
# thus previous test data exist in different methods
@pytest.fixture(scope="function")
def simai_client():
    client = SimAIClient(
        url="https://test.test",
        _disable_authentication=True,
        no_sse_connection=True,
        skip_version_check=True,
        organization="ExtraCorp",
    )
    client._current_workspace = Workspace(
        client,
        client._workspace_directory,
        {"id": "whatever", "name": "not-an-actual-workspace-please-set-it-if-needed"},
    )
    yield client


@pytest.fixture(scope="function")
def sse_mixin(simai_client):
    yield ApiClient(
        simai_client=simai_client,
        config=ClientConfig(
            url="https://test.test",
            _disable_authentication=True,
            no_sse_connection=True,
            organization="PhantomOrg",
        ),
    )


@pytest.fixture(scope="function")
def post_processing_factory(simai_client) -> PostProcessing:
    """Returns a function to create a :py:class:`PostProcessing`."""

    def _factory(prediction=None, **kwargs) -> PostProcessing:
        kwargs.setdefault("id", str(random.random()))
        if prediction and not "prediction_id" in kwargs:
            kwargs["prediction_id"] = prediction.id
        kwargs.setdefault("state", "successful")
        return simai_client._post_processing_directory._model_from(kwargs, prediction=prediction)

    return _factory


@pytest.fixture(scope="function")
def prediction_factory(simai_client) -> Prediction:
    """Returns a function to create a :py:class:`Prediction`."""

    def _factory(post_processings=None, geometry=None, **kwargs) -> Prediction:
        if not "id" in kwargs:
            if "boundary_conditions" in kwargs:
                kwargs["id"] = "pred-" + "-".join(
                    str(s) for s in kwargs["boundary_conditions"].values()
                )
            else:
                kwargs["id"] = str(random.random())
        if geometry and not "geometry_id" in kwargs:
            kwargs["geometry_id"] = geometry.id
        kwargs.setdefault("boundary_conditions", {"Vx": 10.01, "Vy": 0.0009})
        kwargs.setdefault("state", "successful")
        prediction = simai_client._prediction_directory._model_from(kwargs)
        if post_processings is not None:
            # If we passed post-processings as parameter,
            # link them with the prediction.
            # Evidently PP should not be passed directly if the aim
            # is to test creation requests.
            prediction.get_post_processings = lambda: post_processings
            for pp in post_processings:
                pp._prediction = prediction

                # add post processing to prediction
                pred_pp = prediction._post_processings
                params = pp.fields.get("location", {})
                params_frozen = frozenset(params.items())
                pp_type = PostProcessingDirectory._data_model_for_type_name(pp._api_name())
                if not pp_type in pred_pp._post_processings:
                    pred_pp._post_processings[pp_type] = {}
                pred_pp._post_processings[pp_type][params_frozen] = pp
        return prediction

    return _factory


@pytest.fixture()
def geometry_factory(simai_client) -> Geometry:
    """Returns a function to create a :py:class:`Geometry`."""

    def _factory(predictions=[], **kwargs) -> Geometry:
        kwargs.setdefault("id", str(random.random()))
        kwargs.setdefault("name", kwargs["id"])
        kwargs.setdefault("state", "successful")
        kwargs["predictions"] = [s.id for s in predictions]

        geometry = simai_client._geometry_directory._model_from(kwargs)
        geometry.get_predictions = lambda: predictions
        return geometry

    return _factory


@pytest.fixture()
def training_data_factory(simai_client) -> TrainingData:
    """Returns a function to create a :py:class:`TrainingData`."""

    def _factory(**kwargs) -> TrainingData:
        kwargs.setdefault("id", str(random.random()))
        kwargs.setdefault("name", kwargs["id"])
        kwargs.setdefault("state", "successful")

        training_data = simai_client._training_data_directory._model_from(kwargs)
        return training_data

    return _factory


@pytest.fixture()
def project_factory(simai_client) -> Project:
    """Returns a function to create a :py:class:`Project`."""

    def _factory(**kwargs) -> Project:
        kwargs.setdefault("id", str(random.random()))
        kwargs.setdefault("name", kwargs["id"])

        project = simai_client._project_directory._model_from(kwargs)
        return project

    return _factory


@pytest.fixture()
def geometry_directory():
    yield GeometryDirectory(client=None)


@pytest.fixture()
def create_mock_geometry():
    """Creates a lightweight geometry, not tracked by simai_client"""

    def _factory(id, predictions=[], **kwargs):
        geometry = Geometry(None, None, {"id": id, "name": str(id), "metadata": kwargs})
        geometry.get_predictions = lambda: predictions
        return geometry

    return _factory
