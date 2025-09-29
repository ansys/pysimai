# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import json
import logging
import queue
import time
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Event

import httpx
from httpx_sse import ServerSentEvent, connect_sse

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.errors import ApiClientError, ConnectionError
from ansys.simai.core.utils.configuration import ClientConfig

logger = logging.getLogger(__name__)


SSE_ENDPOINT = "sessions/events"


class SSEMixin(ApiClientMixin):
    """Provides the client for the server-sent-events ("/sessions/events")."""

    def __init__(self, config: ClientConfig, simai_client=None):
        super().__init__(config=config)

        if simai_client:
            self.simai_client = simai_client
        else:
            logger.warning("SSEMixin has no SimAI client.")

        # Disable sse thread in unit tests
        if config.no_sse_connection:
            logger.debug("Disabling SSE connection.")
            self._sse_listener = None
            return

        # Flag for stopping the threads when this object is destroyed.
        # A flag is used because Python's threading library does not provide
        # a "stop" command.
        # The _stop_sse_threads is to allow unit tests to kill the thread
        # immediately without needing another event.
        self._stop_sse_threads = getattr(config, "_stop_sse_threads", False)
        self._error_queue: queue.Queue[Exception] = queue.Queue()
        self._flag_sse_started = Event()
        logger.debug("Starting SSE listener thread.")
        self._executor = ThreadPoolExecutor(
            thread_name_prefix="SSEListener",
            max_workers=1,
        )
        self._sse_listener: Future = self._executor.submit(self._sse_thread_loop)
        logger.debug("Started listener thread.")
        self._flag_sse_started.wait(timeout=2)
        self.check_for_sse_error()

    def _sse_thread_loop(self):
        last_event_id = ""
        reconnection_delay = 0.0

        while True:
            try:
                time.sleep(reconnection_delay)
                headers = {"Accept": "text/event-stream"}
                if last_event_id:
                    headers["Last-Event-ID"] = last_event_id

                with connect_sse(
                    self._session, "GET", self._get_sse_url(), headers=headers, timeout=15
                ) as event_source:
                    _raise_for_status(event_source.response)
                    event_source._check_content_type()
                    self._flag_sse_started.set()

                    for sse in event_source.iter_sse():
                        last_event_id = sse.id
                        reconnection_delay = (sse.retry or 1000) / 1000
                        self._handle_sse_event(sse)
                        if self._stop_sse_threads:
                            return
            except httpx.ReadError as e:
                logger.info(f"SSE disconnection: {e}")
            except httpx.HTTPError as e:
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 403:
                    raise ConnectionError(e.response.text) from e
                self._flag_sse_started.set()
                raise ConnectionError("Impossible to connect to event's endpoint.") from e
            except Exception as e:
                self._flag_sse_started.set()
                raise ApiClientError("Unhandled exception in SSE thread") from e
            if self._stop_sse_threads:
                return

    def __del__(self):
        self._stop_sse_threads = True

    def check_for_sse_error(self) -> None:
        """Check if the SSE thread has raised an exception.
        Raises the exception if one occurred.
        """
        if not self._sse_listener:
            return
        if self._sse_listener.done():
            exc = self._sse_listener.exception()
            if exc:
                raise exc

    def _handle_sse_event(self, event: ServerSentEvent):
        try:
            if not event.data:
                # often a message has an empty data: ignore it
                return
            data = json.loads(event.data)
            logger.debug(f"received {data}")

            if "type" not in data:
                raise ValueError("No type is given for SSE event.")
            msg_type = data["type"]
            if msg_type == "session":
                self._handle_session_event(data)
            elif msg_type in ["job", "resource"]:
                self._handle_data_model_event(data)
        except Exception as e:
            msg = f"Error handling SSE event: {e}."
            logger.exception(msg)

    def _handle_data_model_event(self, data):
        target = data["target"]
        if target["type"] == "geometry":
            self.simai_client.geometries._handle_sse_event(data)
        elif target["type"] == "prediction":
            self.simai_client.predictions._handle_sse_event(data)
        elif target["type"] == "post_processing":
            self.simai_client.post_processings._handle_sse_event(data)
        elif target["type"] == "training_data":
            self.simai_client.training_data._handle_sse_event(data)
        elif target["type"] == "training_data_part":
            self.simai_client.training_data_parts._handle_sse_event(data)
        elif target["type"] == "optimization":
            self.simai_client.optimizations._handle_sse_event(data)
        elif target["type"] == "optimization_trial_run":
            self.simai_client._optimization_trial_run_directory._handle_sse_event(data)
        elif target["type"] == "model":
            self.simai_client._model_directory._handle_sse_event(data)
        elif target["type"] == "project":
            if "action" in target:
                if target["action"] in ["check", "compute"]:
                    self.simai_client._process_gc_formula_directory._handle_sse_event(data)
                else:
                    logger.debug(
                        f"Unknown action {target['action']} of type {target['type']} received for job or resource event. Ignoring."
                    )
        elif target["type"] == "geomai_model":
            self.simai_client.geomai.models._handle_sse_event(data)
        elif target["type"] == "geomai_prediction":
            self.simai_client.geomai.predictions._handle_sse_event(data)
        elif target["type"] == "geomai_training_data":
            self.simai_client.geomai.training_data._handle_sse_event(data)

        else:
            logger.debug(
                f"Unknown type {target['type']} received for job or resource event. Ignoring."
            )

    def _handle_session_event(self, data):
        # for now we don't handle session status
        service = data.get("service", "unknown")
        status = data.get("status", "unknown")
        logger.info(f"A session for {service} is now {status}")

    def _get_sse_url(self):
        return self.build_full_url_for_endpoint(SSE_ENDPOINT)


def _raise_for_status(resp: httpx.Response):
    """Wrapper for Response.raise_for_status().

    Reads the stream on error so err.response.text is loaded.
    """
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        resp.read()
        raise
