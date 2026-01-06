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

import logging
import os
import ssl
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from httpx_retries import RetryTransport

from ansys.simai.core import __version__
from ansys.simai.core.data.types import APIResponse, File, MonitorCallback
from ansys.simai.core.errors import ConfigurationError, ConnectionError
from ansys.simai.core.utils.auth import Authenticator
from ansys.simai.core.utils.configuration import ClientConfig
from ansys.simai.core.utils.files import file_path_to_obj_file
from ansys.simai.core.utils.requests import handle_response

logger = logging.getLogger(__name__)


class ApiClientMixin:
    """Provides the core that all mixins and the API client are built on."""

    def __init__(self, *args, config: ClientConfig):  # noqa: D107
        def new_transport(**kw):
            return RetryTransport(transport=httpx.HTTPTransport(**kw))

        transport_args = {"retries": 3}

        if config.tls_ca_bundle == "system":
            if sys.version_info < (3, 10):
                raise ConfigurationError("The system CA store can only be used with python >= 3.10")
            import truststore  # noqa: PLC0415

            transport_args["verify"] = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        elif config.tls_ca_bundle == "unsecure-none":
            transport_args["verify"] = False
        elif isinstance(config.tls_ca_bundle, os.PathLike):
            transport_args["verify"] = ssl.create_default_context(cafile=str(config.tls_ca_bundle))

        mounts = {"https://": new_transport(**transport_args)}
        if config.https_proxy:
            proxy_str = str(config.https_proxy)
            logger.debug(f"Connecting using specified proxy: {proxy_str}")
            mounts["https://"] = new_transport(**transport_args, proxy=proxy_str)
        else:
            proxies = httpx.Client._get_proxy_map(None, None, True)
            for k, v in proxies.items():
                mounts[k] = new_transport(**transport_args, proxy=v)

        # TODO: stop following redirects
        self._session = httpx.Client(
            mounts=mounts, headers=self._get_user_agent(), follow_redirects=True, timeout=15.0
        )
        self._url_prefix = config.url
        self._session.auth = Authenticator(config, self._session)

    def _get_user_agent(self) -> dict:
        """Get the user-agent header."""
        v = sys.version_info
        user_agent = f"PySimAI {__version__}/Python {v.major}.{v.minor}.{v.micro}"
        return {"User-Agent": user_agent}

    def _get(self, url, *args, **kwargs) -> APIResponse:
        """_request with method set to GET."""
        return self._request("GET", url, *args, **kwargs)

    def _put(self, url, *args, **kwargs) -> APIResponse:
        """_request with method set to PUT."""
        return self._request("PUT", url, *args, **kwargs)

    def _post(self, url, *args, **kwargs) -> APIResponse:
        """_request with method set to POST."""
        return self._request("POST", url, *args, **kwargs)

    def _delete(self, url, *args, **kwargs) -> APIResponse:
        """_request with method set to DELETE."""
        return self._request("DELETE", url, *args, **kwargs)

    def _patch(self, url, *args, **kwargs) -> APIResponse:
        """_request with method set to PATCH."""
        return self._request("PATCH", url, *args, **kwargs)

    def build_full_url_for_endpoint(self, url) -> str:  # noqa: D102
        return urljoin(str(self._url_prefix), url, allow_fragments=True)

    def _request(
        self,
        method: str,
        url,
        *args,
        return_json: bool = True,
        **kwargs,
    ) -> APIResponse:
        """Wrap around :py:meth:`requests.Session.request`.

        By default, this method expects a JSON response. If you call an endpoint that does
        not return a JSON response, specify ``return_json=False``.

        Args:
            method: HTTP verb of the request.
            url: URL of the request.
            *args: Additional arguments for the request.
            return_json: Whether the expected response is a json. If ``True``, the JSON
                is returned directly. Otherwise, the response is returned.
            **kwargs: Additional kwargs for request.

        Returns:
            JSON dictionary of the response if :py:args:`return_json` is True. The raw
                :py:class:`httpx.Response` otherwise.
        """
        logger.debug(f"Request {method} on {url}")
        full_url = self.build_full_url_for_endpoint(url)
        try:
            return handle_response(
                self._session.request(method, full_url, *args, **kwargs),
                return_json=return_json,
            )
        except httpx.RequestError as e:
            raise ConnectionError(str(e)) from None

    def download_file(
        self,
        download_url: str,
        file: Optional[File] = None,
        monitor_callback: Optional[MonitorCallback] = None,
        request_json_body: Optional[Dict[str, Any]] = None,
        request_method: str = "GET",
    ) -> Union[None, BinaryIO]:
        """Download a file from a URL into a file or a :class:`BytesIO` object.

        Args:
            download_url: URL for getting the file.
            file: Optional binary file or path for the downloaded file.
            monitor_callback: Optional callback to monitor the progress of the download.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.
            request_json_body: Optional JSON to include in the request.
            request_method: HTTP verb of the request.

        Raises:
            ConnectionError: If an error occurred during the download.

        Returns:
            None if a file is provided or a ``BytesIO`` object with the file's
            content otherwise.
        """
        if file is None:
            output_file = BytesIO()
            close_file = False
        elif isinstance(file, (Path, os.PathLike, str)):
            output_file = file_path_to_obj_file(file, "wb")
            close_file = True
        else:
            output_file = file
            close_file = False

        request_kwargs = {}
        if request_json_body is not None:
            request_kwargs.update({"json": request_json_body})
        logger.debug(f"Request stream {request_method} on {download_url}")
        full_url = self.build_full_url_for_endpoint(download_url)
        try:
            with self._session.stream(request_method, full_url, **request_kwargs) as response:
                handle_response(response, False)
                if monitor_callback is not None:
                    monitor_callback(int(response.headers.get("Content-Length", 0)))
                logger.info("Starting download.")
                for chunk in response.iter_bytes():
                    bytes_read_delta = output_file.write(chunk)
                    if monitor_callback is not None:
                        monitor_callback(bytes_read_delta)
        except httpx.RequestError as e:
            logger.debug("Error {e} happened during download stream.")
            if close_file is True:
                output_file.close()
                os.remove(str(output_file))
            raise ConnectionError(str(e)) from None
        logger.info("Download complete.")
        if close_file is True:
            output_file.close()
        elif output_file.seekable():
            output_file.seek(0)
        if file is None:
            return output_file

    def upload_file_with_presigned_post(
        self,
        file: BinaryIO,
        presigned_post: Dict[str, Any],
        monitor_callback: None = None,
    ):
        if monitor_callback:
            logger.warning(
                "monitor_callback is no longer supported in upload_file_with_presigned_post"
            )
        filename = getattr(file, "name", "")
        files = {"file": (filename, file, "application/octet-stream")}
        self._post(
            presigned_post["url"], files=files, data=presigned_post["fields"], return_json=False
        )

    def upload_parts(
        self,
        url: str,
        file: BinaryIO,
        upload_id: str,
        part_size: int = int(100e6),
        monitor_callback: Optional[MonitorCallback] = None,
    ) -> List[Dict[str, Any]]:
        """Upload parts using the given endpoints to get presigned ``PUT`` URLs.

        Returns:
            List of parts with their IDs and HTTP ETags.
        """
        part_number = 1
        parts = []
        while True:
            part_data = file.read(part_size)
            if len(part_data) == 0:
                break
            logger.debug(f"Uploading part {part_number}, sizeof {len(part_data)} bytes")
            create_part = self._put(url, json={"part_number": part_number, "upload_id": upload_id})
            uploaded_part = self._put(create_part["url"], data=part_data, return_json=False)
            parts.append({"PartNumber": part_number, "ETag": uploaded_part.headers["ETag"]})
            part_number += 1
            if monitor_callback is not None:
                monitor_callback(len(part_data))
        return parts
