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
import platform
from inspect import cleandoc
from pathlib import Path
from typing import Any, Dict, Optional

import tomli
from pydantic.v1.utils import deep_update

from ansys.simai.core.data.types import Path as PathType
from ansys.simai.core.errors import ConfigurationNotFoundError, InvalidConfigurationError

logger = logging.getLogger(__name__)


def _scan_defaults_config_paths() -> Optional[Path]:
    """Look for configuration files in the default locations.

    Returns:
        Path of the first configuration file from the list of existing configuration files.
    """
    system = platform.system()
    if system == "Windows":
        base_folder = Path(os.environ.get("APPDATA", "~")).expanduser()
        config_file = base_folder / "Ansys" / "simai.conf"
        if config_file.is_file():
            return config_file
    elif system == "Linux" or system == "Darwin":
        xdg_config = Path(os.getenv("XDG_CONFIG_HOME") or "~/.config")
        conf_paths = [
            xdg_config / "ansys_simai.conf",
            xdg_config / "ansys/simai.conf",
            "~/.ansys_simai.conf",
            "~/.ansys/simai.conf",
            "/etc/ansys_simai.conf",
            "/etc/ansys/simai.conf",
        ]
        for path in conf_paths:
            path = Path(path).expanduser()  # noqa: PLW2901
            if path.is_file():
                logger.debug(f"Found a configuration file at {path}.")
                return path
    else:
        raise ConfigurationNotFoundError("Could not determine OS.")
    # If no file was found
    return None


def get_config(
    path: Optional[PathType] = None,
    profile: str = "default",
    ignore_missing=False,
    **kwargs,
) -> Dict[Any, Any]:
    """Get configuration file, validate it, and return it as a flat dictionary.

    Args:
        path: Path of the configuration file. The default is ``None, in which
            case the method looks in default locations.
        profile: Profile to load. If no oath is specified, the method looks for ``[default]``.
        ignore_missing: Whether to raise an exception if no path to a configuration
            file is found. The default is ``False``.
        **kwargs: Overrides to apply to the configuration.
    """
    config_path = path or _scan_defaults_config_paths()
    if config_path is None:
        if ignore_missing:
            return kwargs
        raise ConfigurationNotFoundError
    config_path = Path(config_path).expanduser()
    if not os.path.isfile(config_path):
        raise ConfigurationNotFoundError
    with open(config_path, "rb") as f:
        try:
            all_config = tomli.load(f)
        except tomli.TOMLDecodeError as e:
            raise InvalidConfigurationError(f"Invalid configuration: {e}") from None
    config = all_config.get(profile, None)
    if config is None:
        raise InvalidConfigurationError(
            cleandoc(  # Takes care of the indentation
                f"""
                Did not find the [{profile}] profile section in the configuration file.
                Make sure that you have a '[default]' section or specify the name of the profile in your 'from_config' call.
                """
            )
        )
    config["_config_file_profile"] = profile
    # Apply overrides from kwargs if any
    config = deep_update(config, kwargs)
    return config
