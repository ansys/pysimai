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

import getpass
import logging
from typing import Any, Dict, Optional

from semver.version import Version

logger = logging.getLogger(__name__)


def prompt_for_input(name: str, hide_input: Optional[bool] = False):
    return input(f"{name}:") if not hide_input else getpass.getpass(f"{name}:")


def build_boundary_conditions(boundary_conditions: Optional[Dict[str, Any]] = None, **kwargs):
    bc = boundary_conditions if boundary_conditions else {}
    bc.update(**kwargs)
    if not bc:
        raise ValueError("No boundary condition was specified.")
    return bc


def dict_get(obj: dict, *keys: str, default=None):
    """Get the requested key of the dictionary or opt to the default."""
    for k in keys:
        obj = obj.get(k, {}) or {}
    return obj or default


def notify_if_package_outdated(package: str, current_version: str, latest_version: str):
    try:
        version_current = Version.parse(current_version)
        version_latest = Version.parse(latest_version)
    except ValueError as e:
        logger.debug(f"Could not parse package version: {e}")
    else:
        if version_current < version_latest:
            warn_template = (
                f"A new version of {package} is %s. "
                "Upgrade to get new features and ensure compatibility with the server."
            )
            if (
                version_current.major < version_latest.major
                or version_current.minor < version_latest.minor
            ):
                logger.critical(warn_template % "required")
            else:
                logger.warning(warn_template % "available")
