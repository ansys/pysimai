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

import json
import logging
import os
import threading
from typing import Optional

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.errors import ConnectionError
from ansys.simai.core.utils.configuration import ClientConfig
from ansys.simai.core.utils.sse_client import ReconnectingSSERequestsClient

logger = logging.getLogger(__name__)


SSE_ENDPOINT = "sessions/events"


class SSEMixin(ApiClientMixin):
    """Provides the client for the server-sent-events ("/sessions/events")."""

    def __init__(self, config: ClientConfig, simai_client=None):
        super().__init__(config=config)

        if simai_client:
            self.simai_client = simai_client
        else:
            logger.warning("SSEMixin has no SIM AI client.")

        # Disable sse thread in unit tests
        if config.no_sse_connection:
            logger.debug("Disabling SSE connection.")
            return

        # Flag for stopping the threads when this object is destroyed.
        # A flag is used because Python's threading library does not provide
        # a "stop" command.
        # The _stop_sse_threads is to allow unit tests to kill the thread
        # immediately without needing another event.
        self._stop_sse_threads = getattr(config, "_stop_sse_threads", False)
        logger.debug("Connecting to SSE.")

        def sse_connection_factory(last_event_id: Optional[str]):
            headers = {"Accept": "text/event-stream"}
            if last_event_id is not None:
                headers["Last-Event-ID"] = last_event_id
            return self._get(
                self._get_sse_url(),
                stream=True,
                headers=headers,
                return_json=False,
            )

        try:
            self.sse_client = ReconnectingSSERequestsClient(sse_connection_factory)
        except Exception as e:
            raise ConnectionError("Impossible to connect to event's endpoint.") from e
        logger.debug("SSEMixin is connected to SSE endpoint.")
        logger.debug("Starting listener thread.")
        self.listener_thread = threading.Thread(target=self._sse_thread_loop, daemon=True)
        self.listener_thread.start()
        logger.debug("Started listener thread.")

    def __del__(self):
        self._stop_sse_threads = True

    def _sse_thread_loop(self):
        try:
            for event in self.sse_client.events():
                if self._stop_sse_threads:
                    break
                self._handle_sse_event(event)
        except Exception:
            logger.critical("Unhandled exception in SSE thread: ", exc_info=True)
            # if object has been garbage collected, ignore exceptions
            if not self._stop_sse_threads:
                os._exit(1)

    def _handle_sse_event(self, event):
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
            logger.error(msg)

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
