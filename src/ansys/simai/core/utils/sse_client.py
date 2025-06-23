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

import logging
import time
from urllib.parse import urlparse

import niquests
import urllib3_future

logger = logging.getLogger(__name__)


class ReconnectingSSERequestsClient:
    def __init__(
        self,
        session: niquests.Session,
        url: str,
    ):
        self._session = session
        parsed_url = urlparse(url)
        if parsed_url.scheme == "https":
            self.url = parsed_url._replace(scheme="sse").geturl()
        elif parsed_url.scheme == "http":
            self.url = parsed_url._replace(scheme="psse").geturl()
        self._last_event_id = None
        self._retry_timeout_sec = 3
        self._sse = None
        self._connect()

    def _connect(self):
        self._disconnect_client()
        logger.info(f"Will connect to SSE with last event id {self._last_event_id}.")
        self._sse = self._session.get(self.url)
        self._sse.raise_for_status()
        logger.info("Created SSEClient with event source.")

    def _disconnect_client(self):
        if self._sse and self._sse.extension and not self._sse.extension.closed:
            try:
                self.close()
            except AssertionError:
                # Connection was already closed by peer
                pass
            except Exception:
                logger.error("Failed to close SSEClient ", exc_info=True)

    def close(self):
        self._sse.extension.close()
        self._sse = None

    def events(self):
        while True:
            try:
                while not self._sse.extension.closed:
                    event = self._sse.extension.next_payload()
                    logger.debug(f"SSE event received: {event}")
                    if event is None:
                        logger.warning("SSE connection closed by remote")
                        self._connect()
                        break
                    yield event
                    self._last_event_id = event.id
            except (
                StopIteration,
                niquests.exceptions.ChunkedEncodingError,
                niquests.RequestException,
                EOFError,
                urllib3_future.exceptions.MustRedialError,
                # In some cases, when the extension is closed the SSE extension
                # becomes None and trying to access .closed causes an AttributeError
                AttributeError,
            ) as e:
                logger.info(f"SSEClient disconnected: {e}")
                logger.info(f"Will try to reconnect after {self._retry_timeout_sec}s")
                time.sleep(self._retry_timeout_sec)
                self._connect()
