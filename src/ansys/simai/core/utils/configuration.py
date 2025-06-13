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
from os import PathLike
from typing import Literal, Optional, Union
from urllib.parse import urlparse, urlunparse

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    HttpUrl,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from ansys.simai.core.utils.misc import prompt_for_input

logger = logging.getLogger(__name__)


def prompt_if_interactive(interactive, **kwargs):
    """Raise an error or prompt for input according to _interactive_mode."""
    if not interactive:
        raise PydanticCustomError(
            "conf_param_missing", f"""Missing parameter "{kwargs["name"]}" from configuration"""
        )
    return prompt_for_input(**kwargs)


class Credentials(BaseModel, extra="forbid"):
    username: str  # the model validator will call prompt_for_interactive when interactive is on
    "Username: Required if :code:`Credentials` is defined, automatically prompted."
    password: str  # like above
    "Password: Required if :code:`Credentials` is defined, automatically prompted."
    totp: Optional[str] = None  # like the above
    "One-time password: required if :code:`totp_enabled=True`, automatically prompted."

    @model_validator(mode="before")
    @classmethod
    def prompt(cls, values, info):
        if "username" not in values:
            values["username"] = prompt_if_interactive(
                interactive=info.data["interactive"], name="username"
            )
        if "password" not in values:
            values["password"] = prompt_if_interactive(
                interactive=info.data["interactive"],
                name="password",
                hide_input=True,
            )
        if values.pop("totp_enabled", False) and "totp" not in values:
            values["totp"] = prompt_if_interactive(
                interactive=info.data["interactive"], name="totp"
            )
        return values


class ClientConfig(BaseModel, extra="allow"):
    interactive: Optional[bool] = True
    "If True, it enables interaction with the terminal."
    url: HttpUrl = HttpUrl("https://api.simai.ansys.com/v2/")
    "URL to the SimAI API."
    organization: str = Field(None, validate_default=True)
    "Name of the organization(/company) that the user belongs to."
    workspace: Optional[str] = None
    "Name of the workspace to use by default."
    project: Optional[str] = None
    "Name of the project to use by default."
    geomai_workspace: Optional[str] = None
    "Name of the GeomAI workspace to use by default."
    geomai_project: Optional[str] = None
    "Name of the GeomAI project to use by default."
    credentials: Optional[Credentials] = Field(
        default=None,
        validate_default=True,
    )
    "Authenticate via username/password instead of the device authorization code."
    skip_version_check: bool = False
    "Skip checking for updates."
    no_sse_connection: bool = False
    "Don't receive live updates from the SimAI API."
    https_proxy: Optional[AnyHttpUrl] = None
    "URL of the HTTPS proxy to use."
    tls_ca_bundle: Union[Literal["system", "unsecure-none"], PathLike, None] = None
    """
    Custom TLS CA certificate configuration. Possible values:

    * ``None``: use secure defaults
    * ``"system"``: uses system CA certificates (python >= 3.10)
    * A ``PathLike`` object: use a custom CA
    * ``"unsecure-none"``: no TLS certificate validation
    """

    @field_validator("url", mode="before")
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

    @field_validator("organization", mode="before")
    @classmethod
    def check_organization_exists(cls, val, info: ValidationInfo):
        """If organization is not set, either prompt the user or raise exception."""
        if not val:
            val = prompt_if_interactive(interactive=info.data["interactive"], name="organization")
        return val

    @field_validator("credentials", mode="before")
    @classmethod
    def creds_exist_when_non_interactive(cls, val, info: ValidationInfo):
        """If interactive mode is OFF and credentials are not set, raise exception."""
        if not info.data["interactive"] and not val:
            raise PydanticCustomError(
                "creds_missing_in_non_interactive",
                """Credentials should exist when interactive is false""",
            )
        return val
