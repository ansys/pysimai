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
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from unittest.mock import patch

import pytest

import ansys.simai.core.errors as err
from ansys.simai.core import SimAIClient


#
# SETUP
#
@pytest.fixture(scope="module")
def tls_root_certificate(tmp_path):
    # Create CA key and certificate
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", tmp_path / "ca_key.pem", "-out", tmp_path / "test_ca.pem", "-days", "3650", "-subj", "/CN=Test CA"], check=False)  # fmt: skip # noqa: S607, S603
    # Create server key and certificate
    subprocess.run(["openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", tmp_path / "server_key.pem", "-out", tmp_path / "server_csr.pem", "-subj", "/CN=localhost"], check=False)  # fmt: skip # noqa: S607, S603
    with open(tmp_path / "openssl.cnf", "w") as f:
        # Create a config file for OpenSSL to include the SAN
        f.write("[SAN]\nsubjectAltName = DNS:localhost\n")
    subprocess.run(["openssl", "x509", "-req", "-in", tmp_path / "server_csr.pem", "-CA", tmp_path / "test_ca.pem", "-CAkey", tmp_path / "ca_key.pem", "-CAcreateserial", "-out", tmp_path / "server_cert.pem", "-days", "3650", "-extensions", "SAN", "-extfile", tmp_path / "openssl.cnf"], check=False)  # fmt: skip # noqa: S607, S603

    return {
        "ca": tmp_path / "test_ca.pem",
        "server_key": tmp_path / "server_key.pem",
        "server_cert": tmp_path / "server_cert.pem",
    }


@pytest.fixture(scope="module")
def https_server(tls_root_certificate):
    class SimpleHTTPSHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Hello, Secure World!")

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(
        certfile=tls_root_certificate["server_cert"], keyfile=tls_root_certificate["server_key"]
    )
    httpd = HTTPServer(("localhost", 48219), SimpleHTTPSHandler)
    httpd.socket = ssl_context.wrap_socket(
        httpd.socket,
        server_side=True,
    )
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

    return "https://localhost:48219"


BASE_CLT_ARGS = {
    "url": "https://test.example.com",
    "organization": "dummy",
    "_disable_authentication": True,
    "no_sse_connection": True,
    "skip_version_check": True,
}


#
# TESTS
#
def test_client_without_config_tls_ca_bundle(tls_root_certificate, https_server):
    # Default config, using certifi's certificate store
    clt = SimAIClient(**BASE_CLT_ARGS)
    # By default, the self-signed test CA is not accepted
    with pytest.raises(err.ConnectionError):
        clt._api._get("https://localhost:48219")
    # One can use REQUESTS_CA_BUNDLE
    with patch.dict(os.environ, {"REQUESTS_CA_BUNDLE": tls_root_certificate["ca"]}):
        clt._api._get("https://localhost:48219", return_json=False)


@pytest.mark.skipIf(sys.version_info < (3, 10), "Requires Python 3.10+")
def test_client_config_tls_ca_bundle_system(tls_root_certificate, https_server):
    clt = SimAIClient(**BASE_CLT_ARGS, tls_ca_bundle="system")
    # The system CA rejects the test CA by default
    with pytest.raises(err.ConnectionError):
        clt._api._get("https://localhost:48219")

    # If the host system trusts the test CA, pysimai trusts it !
    @contextlib.contextmanager
    def load_test_ca_as_truststore_system_ca(ctx: "ssl.SSLContext"):
        ctx.load_verify_locations(cafile=tls_root_certificate["ca"])
        yield

    with patch(
        "truststore._api._configure_context", side_effect=load_test_ca_as_truststore_system_ca
    ):
        clt._api._get("https://localhost:48219", return_json=False)


def test_client_config_tls_ca_bundle_unsecure_none(https_server):
    clt = SimAIClient(**BASE_CLT_ARGS, tls_ca_bundle="unsecure-none")
    clt._api._get("https://localhost:48219", return_json=False)


def test_client_config_tls_ca_bundle_path(tls_root_certificate, https_server):
    clt = SimAIClient(**BASE_CLT_ARGS, tls_ca_bundle=tls_root_certificate["ca"])
    clt._api._get("https://localhost:48219", return_json=False)