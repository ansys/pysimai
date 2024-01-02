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

from typing import Any, Callable, Iterable, List, TypeVar

import requests


class SimAIError(Exception):
    """Base exception for all errors of the SimAI SDK.

    To catch any expected error that it might throw, use this exception.
    """


class ApiClientError(SimAIError, requests.exceptions.HTTPError):
    """HTTP Error from the SimAi API."""

    def __init__(self, message: str, response=None):
        super(ApiClientError, self).__init__(message, response=response)

    @property
    def status_code(self):  # noqa: D102
        if self.response is not None:
            return self.response.status_code


class NotFoundError(ApiClientError):
    """The required resource was found on the server."""


class ConnectionError(SimAIError, requests.exceptions.ConnectionError):
    """Could not communicate with the server."""


class ConfigurationError(SimAIError):
    """The SDK could not be configured properly."""


class ConfigurationNotFoundError(ConfigurationError):
    """The configuration file does not exist."""


class InvalidConfigurationError(ConfigurationError, ValueError):
    """The given configuration is not valid."""


class ProcessingError(SimAIError):
    """The data could not be processed."""


class InvalidArguments(SimAIError, ValueError):
    """Invalid arguments were provided."""


class InvalidClientStateError(SimAIError):
    """The client's state is invalid."""


class InvalidServerStateError(SimAIError):
    """The server's state is invalid."""


class MultipleErrors(SimAIError):
    """Multiple errors occurred."""

    def __init__(self, exceptions: List[SimAIError]):
        self.exceptions = exceptions


T = TypeVar("T")


def _map_despite_errors(
    function: Callable[[T], Any],
    iterable: Iterable[T],
):
    """Like map(), applies the function for each item in iterable and return the result.
    On exception, it will continue with next items,
    and at the end raise either the exception or a MultipleError.
    """
    results: List[T] = []
    errors: List[SimAIError] = []
    for item in iterable:
        try:
            res = function(item)
            results.append(res)
        except SimAIError as e:
            errors.append(e)
    if errors:
        if len(errors) == 1:
            raise errors[0]
        raise MultipleErrors(errors)
    return results


def _foreach_despite_errors(
    procedure: Callable[[T], None],
    iterable: Iterable[T],
):
    """Applies the procedure for each item in iterable.
    On exception, it will continue with next items,
    and at the end raise either the exception or a MultipleError.
    """
    errors = []
    for item in iterable:
        try:
            procedure(item)
        except SimAIError as e:
            errors.append(e)
    if errors:
        if len(errors) == 1:
            raise errors[0]
        raise MultipleErrors(errors)
