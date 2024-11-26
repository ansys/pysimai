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

import contextlib
import os
import ssl
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from unittest.mock import patch

import pytest
import responses

import ansys.simai.core.errors as err
from ansys.simai.core import SimAIClient


def test_client_creation_invalid_path():
    with pytest.raises(err.ConfigurationNotFoundError):
        SimAIClient.from_config(path="/")


def test_client_creation_invalid_config():
    with pytest.raises(err.InvalidConfigurationError):
        SimAIClient.from_config(path=Path(__file__).resolve())


@pytest.mark.parametrize(
    "local_ver,latest_ver,expected",
    [
        ("1.1.0", "1.1.1", "available."),
        ("1.0.9-rc8", "1.0.9", "available."),
        ("1.0.9", "1.9.0", "required."),
    ],
)
@responses.activate
def test_client_version_auto_warn(caplog, mocker, local_ver, latest_ver, expected):
    """WHEN the SDK version is slightly outdated compared to what the API responds
    THEN a warning is printed
    """
    mocker.patch(
        "ansys.simai.core.client.__version__",
        local_ver,
    )
    responses.add(
        responses.GET,
        "https://pypi.org/pypi/ansys-simai-core/json",
        json={"info": {"version": latest_ver}},
        status=200,
    )
    SimAIClient(
        url="https://test.test",
        organization="dummy",
        _disable_authentication=True,
        no_sse_connection=True,
        skip_version_check=False,
    )
    assert f"A new version of ansys-simai-core is {expected}" in caplog.text


def test_https_server_with_custom_ca(tmp_path, mocker):
    """Test HTTPS server with custom CA verification"""
    # Create CA key and certificate
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", tmp_path / "ca_key.pem", "-out", tmp_path / "test_ca.pem", "-days", "3650", "-subj", "/CN=Test CA"], check=False)  # fmt: skip # noqa: S607, S603
    # Create server key and certificate
    subprocess.run(["openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", tmp_path / "server_key.pem", "-out", tmp_path / "server_csr.pem", "-subj", "/CN=localhost"], check=False)  # fmt: skip # noqa: S607, S603
    with open(tmp_path / "openssl.cnf", "w") as f:
        # Create a config file for OpenSSL to include the SAN
        f.write("[SAN]\nsubjectAltName = DNS:localhost\n")
    subprocess.run(["openssl", "x509", "-req", "-in", tmp_path / "server_csr.pem", "-CA", tmp_path / "test_ca.pem", "-CAkey", tmp_path / "ca_key.pem", "-CAcreateserial", "-out", tmp_path / "server_cert.pem", "-days", "3650", "-extensions", "SAN", "-extfile", tmp_path / "openssl.cnf"], check=False)  # fmt: skip # noqa: S607, S603

    # Spawn an HTTPS server
    class SimpleHTTPSHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Hello, Secure World!")

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(
        certfile=tmp_path / "server_cert.pem", keyfile=tmp_path / "server_key.pem"
    )
    httpd = HTTPServer(("localhost", 48219), SimpleHTTPSHandler)
    httpd.socket = ssl_context.wrap_socket(
        httpd.socket,
        server_side=True,
    )
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    # Test requests
    clt_args = {
        "url": "https://test.example.com",
        "organization": "dummy",
        "_disable_authentication": True,
        "no_sse_connection": True,
        "skip_version_check": True,
    }

    ## Default config, using certifi's certificate store
    clt = SimAIClient(**clt_args)
    ### By default, the self-signed test CA is not accepted
    with pytest.raises(err.ConnectionError):
        clt._api._get("https://localhost:48219")
    ### One can use REQUESTS_CA_BUNDLE
    with patch.dict(os.environ, {"REQUESTS_CA_BUNDLE": str(tmp_path / "test_ca.pem")}):
        clt._api._get("https://localhost:48219", return_json=False)

    ## Using the system CA
    @contextlib.contextmanager
    def load_test_ca_as_truststore_system_ca(ctx: "ssl.SSLContext"):
        ctx.load_verify_locations(cafile=tmp_path / "test_ca.pem")
        yield

    clt = SimAIClient(**clt_args, tls_ca_bundle="system")
    ### The system CA rejects the test CA by default
    with pytest.raises(err.ConnectionError):
        clt._api._get("https://localhost:48219")
    ### If the host system trusts the test CA, pysimai trusts it !
    with patch(
        "truststore._api._configure_context", side_effect=load_test_ca_as_truststore_system_ca
    ):
        clt._api._get("https://localhost:48219", return_json=False)

    ## Disabling CA validation
    clt = SimAIClient(**clt_args, tls_ca_bundle="unsecure-none")
    clt._api._get("https://localhost:48219", return_json=False)

    ## Passing the path to the CA cert
    clt = SimAIClient(**clt_args, tls_ca_bundle=tmp_path / "test_ca.pem")
    clt._api._get("https://localhost:48219", return_json=False)
