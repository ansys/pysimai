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
import time
from typing import Callable, Optional

import requests
import sseclient

logger = logging.getLogger(__name__)


# take an optional last-event-id to be sent in request headers
EventSourceFactoryType = Callable[[Optional[str]], sseclient.SSEClient]


class ReconnectingSSERequestsClient:
    def __init__(
        self,
        event_source_factory: EventSourceFactoryType,
        char_enc: Optional[str] = None,
    ):
        self._sseclient = None
        self._event_source_factory = event_source_factory
        self._char_enc = char_enc
        self._last_event_id = None
        self._retry_timeout_sec = 3
        self._connect()

    def _connect(self):
        self._disconnect_client()
        logger.info(f"Will connect to SSE with last event id {self._last_event_id}.")
        event_source = self._event_source_factory(self._last_event_id)
        logger.info("Create SSEClient with event source.")
        self._sseclient = sseclient.SSEClient(event_source)

    def _disconnect_client(self):
        if self._sseclient is not None:
            try:
                self.close()
            except Exception:
                logger.error("Failed to close SSEClient ", exc_info=True)

    def close(self):
        self._sseclient.close()
        self._sseclient = None

    def events(self):
        while True:
            try:
                for event in self._sseclient.events():
                    yield event
                    self._last_event_id = event.id
            except (
                StopIteration,
                requests.exceptions.ChunkedEncodingError,
                requests.RequestException,
                EOFError,
            ):
                logger.info("SSEClient disconnected ", exc_info=True)
                logger.info(f"Will try to reconnect after {self._retry_timeout_sec}s")
                time.sleep(self._retry_timeout_sec)
                self._connect()
