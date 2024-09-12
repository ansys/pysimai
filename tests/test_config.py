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

import pytest
from pydantic_core import ValidationError

from ansys.simai.core.utils.configuration import ClientConfig


@pytest.mark.parametrize(
    "inputs,password,config,expected_output",
    [
        (
            [
                "12_monkeys",
                "timmy",
                "12345",
            ],  # list of simulated user inputs (other than password)
            "shakaponk",  # password for getpass if needed
            {
                "credentials": {"totp_enabled": True}
            },  # the configuration the method will be called with
            {
                "organization": "12_monkeys",
                "credentials": {
                    "username": "timmy",
                    "password": "shakaponk",
                    "totp": "12345",
                },
            },  # what the method should return
        ),
        (
            ["12345"],
            None,
            {
                "credentials": {
                    "totp_enabled": True,
                    "password": "shakaponk",
                    "username": "timmy",
                },
                "organization": "12_monkeys",
            },
            {
                "credentials": {
                    "username": "timmy",
                    "password": "shakaponk",
                    "totp": "12345",
                },
                "organization": "12_monkeys",
            },
        ),
        (
            [],
            None,
            {
                "credentials": {
                    "username": "timmy",
                    "password": "shakaponk",
                },
                "organization": "12_monkeys",
            },
            {
                "credentials": {"username": "timmy", "password": "shakaponk"},
                "organization": "12_monkeys",
            },
        ),
        (
            ["timmy"],
            "shakaponk",
            {"organization": "12_monkeys", "credentials": {}},
            {
                "credentials": {
                    "username": "timmy",
                    "password": "shakaponk",
                },
                "organization": "12_monkeys",
            },
        ),
        (
            [],
            None,
            {"organization": "12_monkeys"},
            {"organization": "12_monkeys"},
        ),
        (
            [],
            None,
            {  # interactive mode is OFF, and password is missing from credentials
                "organization": "12_monkeys",
                "interactive": False,
                "credentials": {
                    "username": "timmy",
                },
            },
            {"expect_error": True, "type": ValidationError, "error_count": 1},
        ),
        (
            [],
            None,
            {  # interactive mode is OFF, and organization is missing
                "interactive": False,
                "credentials": {"username": "timmy", "password": "teas"},
            },
            {"expect_error": True, "type": ValidationError, "error_count": 1},
        ),
        (
            [],
            None,
            {  # interactive mode is OFF, and organization and password are missing
                "interactive": False,
                "credentials": {"username": "timmy"},
            },
            {"expect_error": True, "type": ValidationError, "error_count": 2},
        ),
        (
            [],
            None,
            {  # interactive mode is OFF, and organization and password are missing, and url is not valid
                "url": "123",
                "interactive": False,
                "credentials": {"username": "timmy"},
            },
            {"expect_error": True, "type": ValidationError, "error_count": 3},
        ),
        (
            [],
            None,
            {  # interactive mode is ON, and credentials are missing
                "organization": "12_monkeys",
                "interactive": False,
            },
            {"expect_error": True, "type": ValidationError, "error_count": 1},
        ),
        (
            [],
            "pass",
            {  # sanity check; interactive is set explicitly to ON
                "interactive": True,
                "credentials": {"username": "timmy"},
                "organization": "12_monkeys",
            },
            {
                "credentials": {
                    "username": "timmy",
                    "password": "pass",
                },
                "organization": "12_monkeys",
            },
        ),
    ],
)
def test_get_authentication_configuration(inputs, password, config, expected_output, mocker):
    """GIVEN A list of prompt inputs, a configuration and an expected output
    WHEN getting authentication info for the config
    THEN the expected output is returned
    """
    mocker.patch("builtins.input", side_effect=inputs)
    mocker.patch("getpass.getpass", return_value=password)
    if expected_output.get("expect_error", None):
        # if an error is expected, catch the exception type and assert the error count
        with pytest.raises(expected_output.get("type")) as ex:
            client_config = ClientConfig(**config)
        assert ex.value.error_count() == expected_output.get("error_count")
    else:
        client_config = ClientConfig(**config).model_dump(exclude_none=True)
        # the config contains many fields, here we only test a subset
        tested_fields = ["organization", "credentials"]
        for f in list(client_config.keys()):
            if f not in tested_fields:
                client_config.pop(f)
        assert client_config == expected_output
