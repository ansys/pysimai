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
from json.decoder import JSONDecodeError

import requests

from ansys.simai.core.data.types import APIResponse
from ansys.simai.core.errors import ApiClientError, NotFoundError

logger = logging.getLogger(__name__)


def handle_http_errors(response: requests.Response) -> None:
    """Raise an error if the response status code is an error.

    Args:
        response: Response to check for errors.

    Raises:
        NotFoundError: If the response is a 404 error.
        ApiClientError: If the response is a 4xx or 5xx error other than the 404 error.
    """
    logger.debug("Checking for HTTP errors.")
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        try:
            json_response = response.json()
        except (ValueError, JSONDecodeError):
            # raise the errors from None
            # as we want to ignore the JSONDecodeError
            if response.status_code == 404:
                raise NotFoundError("Not Found", response) from e
            else:
                raise ApiClientError(
                    f"{response.status_code} {response.reason}", response
                ) from None
        if isinstance(json_response, dict):
            message = (
                json_response.get("errors")
                or json_response.get("message")
                or json_response.get("status")
                or json_response.get("error_description")
                or response.reason
            )

            if response.status_code == 404:
                raise NotFoundError(f"{message}", response) from e
            else:
                raise ApiClientError(
                    f"{response.status_code} {message}",
                    response,
                ) from e
        else:
            raise ApiClientError(f"{response.status_code}: {response.reason}", response) from e


def handle_response(response: requests.Response, return_json: bool = True) -> APIResponse:
    """Handle HTTP errors and return the relevant data from the response.

    Args:
        response: Response to handle
        return_json: Whether to return the JSON content or the whole response.

    Returns:
        JSON dict of the response if :py:args:`return_json` is ``True`` or the raw
            :py:class:`requests.Response` otherwise.
    """
    handle_http_errors(response)

    logger.debug("Returning response.")
    if return_json:
        try:
            return response.json()
        except (ValueError, JSONDecodeError):
            logger.debug("Failed to read JSON response.")
            raise ApiClientError(
                "Expected a JSON response but did not receive one.", response
            ) from None
    else:
        return response
