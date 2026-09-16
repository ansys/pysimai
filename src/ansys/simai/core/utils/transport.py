# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""HTTP transports for the SimAI client."""

import logging
from typing import Iterable, Optional, Type

import httpx2
from tenacity import (
    RetryCallState,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_none,
)

logger = logging.getLogger(__name__)

RETRYABLE_METHODS = frozenset({"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"})
RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})
RETRYABLE_EXCEPTIONS = (
    httpx2.TimeoutException,
    httpx2.NetworkError,
    httpx2.RemoteProtocolError,
)


class Retry:
    """Configuration for :class:`RetryTransport`."""

    def __init__(
        self,
        total: int = 10,
        allowed_methods: Optional[Iterable[str]] = None,
        status_forcelist: Optional[Iterable[int]] = None,
        retry_on_exceptions: Optional[Iterable[Type[Exception]]] = None,
        backoff_factor: float = 0.0,
    ) -> None:
        self.total = total
        self.allowed_methods = frozenset(
            method.upper() for method in (allowed_methods or RETRYABLE_METHODS)
        )
        self.status_forcelist = frozenset(status_forcelist or RETRYABLE_STATUS_CODES)
        self.retry_on_exceptions = tuple(retry_on_exceptions or RETRYABLE_EXCEPTIONS)
        self.backoff_factor = backoff_factor

    def is_retryable_method(self, method: str) -> bool:
        """Whether the given HTTP method can be retried."""
        return method.upper() in self.allowed_methods

    def is_retryable_status_code(self, status_code: int) -> bool:
        """Whether the given status code can be retried."""
        return status_code in self.status_forcelist


class _RetryableStatus(Exception):
    """Internal exception used to trigger a retry on a retryable status code."""

    def __init__(self, response: httpx2.Response) -> None:
        super().__init__(f"Retryable status code: {response.status_code}")
        self.response = response


class RetryTransport(httpx2.BaseTransport):
    """A transport that retries requests on retryable status codes and errors."""

    def __init__(
        self,
        transport: Optional[httpx2.BaseTransport] = None,
        retry: Optional[Retry] = None,
    ) -> None:
        self._transport = transport if transport is not None else httpx2.HTTPTransport()
        self.retry = retry or Retry()

    def close(self) -> None:
        """Close the underlying transport."""
        self._transport.close()

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        """Send a request, retrying it when configured to do so."""
        retry = self.retry
        if retry.total <= 0 or not retry.is_retryable_method(request.method):
            return self._transport.handle_request(request)

        def send() -> httpx2.Response:
            response = self._transport.handle_request(request)
            if retry.is_retryable_status_code(response.status_code):
                raise _RetryableStatus(response)
            return response

        def close_failed_response(retry_state: RetryCallState) -> None:
            exception = retry_state.outcome.exception()
            if isinstance(exception, _RetryableStatus):
                exception.response.close()

        retryer = Retrying(
            stop=stop_after_attempt(retry.total + 1),
            wait=(
                wait_exponential(multiplier=retry.backoff_factor)
                if retry.backoff_factor
                else wait_none()
            ),
            retry=retry_if_exception_type((_RetryableStatus, *retry.retry_on_exceptions)),
            before_sleep=close_failed_response,
            reraise=True,
        )
        try:
            return retryer(send)
        except _RetryableStatus as exc:
            return exc.response
