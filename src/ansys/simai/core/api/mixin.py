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
import os
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union
from urllib.parse import urljoin
from urllib.request import getproxies

import requests
from requests.adapters import HTTPAdapter, Retry
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from ansys.simai.core import __version__
from ansys.simai.core.data.types import APIResponse, File, MonitorCallback
from ansys.simai.core.errors import ConnectionError
from ansys.simai.core.utils.auth import Authenticator
from ansys.simai.core.utils.configuration import ClientConfig
from ansys.simai.core.utils.files import file_path_to_obj_file
from ansys.simai.core.utils.requests import handle_response

logger = logging.getLogger(__name__)


class ApiClientMixin:
    """The core on which all the mixins and the ApiClient are built."""

    def __init__(self, *args, config: ClientConfig):  # noqa: D107
        self._session = requests.Session()

        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self._session.mount("http", HTTPAdapter(max_retries=retries))

        system_proxies = getproxies()
        if config.https_proxy:
            https_proxy_str = str(config.https_proxy)
            logger.debug(f"Connecting using specified proxy: {https_proxy_str}")
            self._session.proxies = {"https": https_proxy_str}
        elif system_proxies:
            logger.debug(f"Using detected system proxies: {system_proxies}")
            self._session.proxies = system_proxies

        self._url_prefix = config.url
        self._set_user_agent()
        self._session.auth = Authenticator(config, self._session)

    def _set_user_agent(self) -> None:
        """Set the user-agent header for the session."""
        user_agent = f"PySimAI {__version__}"
        self._session.headers.update({"User-Agent": user_agent})

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

        By default this method expects a json response. If you call an endpoint that does
        not return a json, specify return_json=False

        Args:
            method: The HTTP verb of the request
            url: The url of the request
            *args: Additional args for the request
            return_json: Whether the expected response is a json. If yes returns
                directly the json, otherwise the Response is returned
            **kwargs: Additional kwargs for request

        Returns:
            The json dict of the response if :py:args:`return_json` is True. The raw
                :py:class:`requests.Response` otherwise.
        """
        logger.debug(f"Request {method} on {url}")
        full_url = self.build_full_url_for_endpoint(url)
        try:
            return handle_response(
                self._session.request(method, full_url, *args, **kwargs),
                return_json=return_json,
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(e) from None

    def download_file(
        self,
        download_url: str,
        file: Optional[File] = None,
        monitor_callback: Optional[MonitorCallback] = None,
        request_json_body: Optional[Dict[str, Any]] = None,
        request_method: str = "GET",
    ) -> Union[None, BinaryIO]:
        """Download a file from the given URL into the given file or a :class:`BytesIO`.

        Args:
            download_url: url to GET the file
            file: Optional binary file or path onto which to put the downloaded file
            monitor_callback: An optional callback to monitor the progress of the download.
                See :obj:`~ansys.simai.core.data.types.MonitorCallback` for details.
            request_json_body: Optional JSON to include in the request
            request_method: The HTTP verb

        Raises:
            ConnectionError: If an error occurred during the download

        Returns:
            None if a file is provided, a BytesIO with the file's content otherwise
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

        request_kwargs = {"stream": True, "return_json": False}
        if request_json_body is not None:
            request_kwargs.update({"json": request_json_body})
        response = self._request(request_method, download_url, **request_kwargs)
        if monitor_callback is not None:
            monitor_callback(int(response.headers.get("Content-Length", 0)))
        logger.info("Starting download.")
        try:
            for chunk in response.iter_content(chunk_size=1024):
                bytes_read_delta = output_file.write(chunk)
                if monitor_callback is not None:
                    monitor_callback(bytes_read_delta)
        except requests.exceptions.ConnectionError as e:
            logger.debug("Error {e} happened during download stream.")
            if close_file is True:
                output_file.close()
                os.remove(output_file)
            raise ConnectionError(e) from None

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
        monitor_callback: Optional[MonitorCallback] = None,
    ):
        upload_form = presigned_post["fields"]
        filename = getattr(file, "name", "")
        upload_form["file"] = (filename, file, "application/octet-stream")
        multipart = MultipartEncoder(upload_form)

        if monitor_callback is not None:
            # Wrap the monitor callback so that it receives only the bytes read
            # instead of the full MultipartEncoderMonitor object
            def wrap_monitor_callback(monitor_callback):
                # FIXME: This ain't gonna work chief
                def wrapped_monitor_callback(monitor):
                    update = monitor_callback(monitor)
                    return update.bytes_read

                return wrapped_monitor_callback

            multipart = MultipartEncoderMonitor(multipart, wrap_monitor_callback(monitor_callback))
        self._post(
            presigned_post["url"],
            data=multipart,
            headers={"Content-Type": multipart.content_type},
            return_json=False,
        )

    def upload_parts(
        self,
        url: str,
        file: BinaryIO,
        upload_id: str,
        part_size: int = int(100e6),
        monitor_callback: Optional[MonitorCallback] = None,
    ) -> List[Dict[str, Any]]:
        """Upload parts using the given endpoints to get presigned PUT urls

        Returns:
            The list of parts, with their id and their etag
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
