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
#
# ruff: noqa: S311

import random
import threading
import time
from collections.abc import Callable
from sys import modules

import niquests
import pytest
import requests
from niquests.packages import urllib3

from ansys.simai.core import SimAIClient
from ansys.simai.core.api.client import ApiClient
from ansys.simai.core.data.geometries import Geometry, GeometryDirectory
from ansys.simai.core.data.models import Model
from ansys.simai.core.data.post_processings import (
    PostProcessing,
    PostProcessingDirectory,
)
from ansys.simai.core.data.predictions import Prediction
from ansys.simai.core.data.projects import Project
from ansys.simai.core.data.training_data import TrainingData
from ansys.simai.core.data.workspaces import Workspace
from ansys.simai.core.utils.configuration import ClientConfig

# HACK: make responses work with niquests, coming from the niquests docs
# https://niquests.readthedocs.io/en/stable/dev/migrate.html
modules["requests"] = niquests
modules["requests.adapters"] = niquests.adapters
modules["requests.exceptions"] = niquests.exceptions
modules["requests.compat"] = requests.compat
modules["requests.packages.urllib3"] = urllib3
###


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
        if prediction and "prediction_id" not in kwargs:
            kwargs["prediction_id"] = prediction.id
        kwargs.setdefault("state", "successful")
        return simai_client._post_processing_directory._model_from(kwargs, prediction=prediction)

    return _factory


@pytest.fixture(scope="function")
def prediction_factory(simai_client) -> Prediction:
    """Returns a function to create a :py:class:`Prediction`."""

    def _factory(post_processings=None, geometry=None, **kwargs) -> Prediction:
        if "id" not in kwargs:
            if "boundary_conditions" in kwargs:
                kwargs["id"] = "pred-" + "-".join(
                    str(s) for s in kwargs["boundary_conditions"].values()
                )
            else:
                kwargs["id"] = str(random.random())
        if geometry and "geometry_id" not in kwargs:
            kwargs["geometry_id"] = geometry.id
        kwargs.setdefault("boundary_conditions", {"Vx": 10.01, "Vy": 0.0009})
        kwargs.setdefault("state", "successful")
        kwargs.setdefault("confidence_score", None)
        kwargs.setdefault("raw_confidence_score", None)
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
                if pp_type not in pred_pp._post_processings:
                    pred_pp._post_processings[pp_type] = {}
                pred_pp._post_processings[pp_type][params_frozen] = pp
        return prediction

    return _factory


@pytest.fixture()
def geometry_factory(simai_client) -> Geometry:
    """Returns a function to create a :py:class:`Geometry`."""

    def _factory(predictions=None, **kwargs) -> Geometry:
        kwargs.setdefault("id", str(random.random()))
        kwargs.setdefault("name", kwargs["id"])
        kwargs.setdefault("state", "successful")
        if not predictions:
            predictions = []
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
def geometry_directory(simai_client):
    yield GeometryDirectory(client=simai_client)


@pytest.fixture()
def create_mock_geometry():
    """Creates a lightweight geometry, not tracked by simai_client"""

    def _factory(id, predictions=None, **kwargs):
        geometry = Geometry(None, None, {"id": id, "name": str(id), "metadata": kwargs})
        geometry.get_predictions = lambda: predictions or []
        return geometry

    return _factory


@pytest.fixture(scope="function")
def global_coefficient_request_factory(simai_client):
    """Returns a function to create a global coefficient request object."""

    def _factory(**kwargs):
        return simai_client._process_gc_formula_directory._model_from(**kwargs)

    return _factory


@pytest.fixture()
def model_factory(simai_client) -> Model:
    """Returns a function to create a :py:class:`Model`."""

    def _factory(**kwargs) -> Model:
        kwargs.setdefault("id", str(random.random()))
        kwargs.setdefault("name", kwargs["id"])

        model = simai_client._model_directory._model_from(kwargs)
        return model

    return _factory


@pytest.fixture
def delayed_events():
    """
    Fixture to test Event.wait() with sequential events.

    This fixture provides a manager for scheduling events to happen at specific times,
    allowing for controlled testing of wait() behavior.

    Usage:
        def test_something(delayed_events):
            # Schedule events to occur
            delayed_events.add(lambda: model.update_state("processing"))
            delayed_events.add(lambda: model.complete())

            # Start the background thread that will trigger events
            delayed_events.start()

            # Call the wait method you're testing
            result = model.wait()

            # Make assertions
            assert result is True
    """

    class DelayedEventManager:
        def __init__(self) -> None:
            self.events = []
            self.thread = None

        def add(self, callback: Callable[[], None], delay: float = 0.1):
            """Add a callback to be executed after the specified delay (in seconds)"""
            self.events.append((delay, callback))

        def start(self):
            """Start the thread that will execute all scheduled events"""

            def run_events():
                start_time = time.time()

                for delay, callback in self.events:
                    time_to_wait = delay - (time.time() - start_time)
                    if time_to_wait > 0:
                        time.sleep(time_to_wait)
                    callback()

            self.thread = threading.Thread(target=run_events)
            self.thread.daemon = True
            self.thread.start()
            return self

        def join(self):
            """Wait for all events to complete"""
            if self.thread:
                self.thread.join()

    manager = DelayedEventManager()

    yield manager

    manager.join()
