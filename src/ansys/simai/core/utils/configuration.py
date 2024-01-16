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

import hashlib
import logging
from typing import Optional
from urllib.parse import urlparse, urlunparse

from pydantic import AnyHttpUrl, BaseModel, Field, HttpUrl, root_validator, validator

from ansys.simai.core.utils.misc import prompt_for_input

logger = logging.getLogger(__name__)


def prompt_for_input_factory(*args, **kwargs):
    return lambda: prompt_for_input(*args, **kwargs)


class Credentials(BaseModel, extra="forbid"):
    username: str = ""  # dummy default, the root validator will call prompt_for_input
    "Username: Required if :code:`Credentials` is defined, automatically prompted."
    password: str = ""  # dummy default, like above
    "Password: Required if :code:`Credentials` is defined, automatically prompted."
    totp: Optional[str] = None
    "One-time password: required if :code:`totp_enabled=True`, automatically prompted."

    @root_validator(pre=True)
    def prompt(cls, values):
        if "username" not in values:
            values["username"] = prompt_for_input("username")
        if "password" not in values:
            values["password"] = prompt_for_input("password", hide_input=True)
        if values.pop("totp_enabled", False) and "totp" not in values:
            values["totp"] = prompt_for_input("totp")
        return values


class ClientConfig(BaseModel, extra="allow"):
    url: HttpUrl = Field(
        default=HttpUrl("https://api.simai.ansys.com/v2/"),
        description="URL to the SimAI API.",
    )
    "URL to the SimAI API."
    organization: str = Field(
        default_factory=prompt_for_input_factory("organization"),
        description="Name of the organization(/company) that the user belongs to.",
    )
    "Name of the organization(/company) that the user belongs to."
    credentials: Optional[Credentials] = Field(
        default=None,
        description="Authenticate via username/password instead of the device authorization code.",
    )
    "Authenticate via username/password instead of the device authorization code."
    workspace: Optional[str] = Field(
        default=None, description="Name of the workspace to use by default."
    )
    "Name of the workspace to use by default."
    project: Optional[str] = Field(
        default=None, description="Name of the project to use by default."
    )
    "Name of the project to use by default."
    https_proxy: Optional[AnyHttpUrl] = Field(
        default=None, description="URL of the HTTPS proxy to use."
    )
    "URL of the HTPPS proxy to use."
    skip_version_check: bool = Field(default=False, description="Skip checking for updates.")
    "Skip checking for updates."
    no_sse_connection: bool = Field(
        default=False, description="Don't receive live updates from the SimAI API."
    )
    "Don't receive live updates from the SimAI API."
    disable_cache: bool = Field(
        default=False, description="Don't use cached authentication tokens."
    )
    "Don't use cached authentication tokens."

    @validator("url", pre=True)
    def clean_url(cls, url):
        if isinstance(url, bytes):
            url = url.decode()
        url = urlunparse(urlparse(url))
        if not url.endswith("/"):
            url = url + "/"
        return url

    def _auth_hash(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(str(self.url).encode())
        if self.credentials:
            hasher.update(self.credentials.username.encode())
        config_file_profile = getattr(self, "_config_file_profile", None)
        if config_file_profile:
            hasher.update(config_file_profile.encode())
        return hasher.hexdigest()
