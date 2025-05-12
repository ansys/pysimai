# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
def tls_root_certificate(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("tls_root_certificate")
    # Create OpenSSL config file for the CA with key usage extension
    with open(tmp_path / "ca_openssl.cnf", "w") as f:
        f.write("""
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_ca
x509_extensions = v3_ca

[req_distinguished_name]

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer:always
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign
""")
    # Create CA key and certificate with extensions
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", tmp_path / "ca_key.pem", "-out", tmp_path / "test_ca.pem", "-days", "3650", "-subj", "/CN=Test CA", "-config", tmp_path / "ca_openssl.cnf"], check=False)  # fmt: skip # noqa: S607, S603
    # Create server key and certificate
    subprocess.run(["openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", tmp_path / "server_key.pem", "-out", tmp_path / "server_csr.pem", "-subj", "/CN=localhost"], check=False)  # fmt: skip # noqa: S607, S603
    with open(tmp_path / "server_openssl.cnf", "w") as f:
        # Create a config file for OpenSSL to include the SAN and key usage extensions
        f.write("""
[req]
distinguished_name = req_distinguished_name

[req_distinguished_name]

[server_ext]
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = DNS:localhost
""")
    subprocess.run(["openssl", "x509", "-req", "-in", tmp_path / "server_csr.pem", "-CA", tmp_path / "test_ca.pem", "-CAkey", tmp_path / "ca_key.pem", "-CAcreateserial", "-out", tmp_path / "server_cert.pem", "-days", "3650", "-extensions", "server_ext", "-extfile", tmp_path / "server_openssl.cnf"], check=False)  # fmt: skip # noqa: S607, S603

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
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    yield "https://localhost:48219"
    httpd.shutdown()


BASE_CLT_ARGS = {
    "url": "https://test.example.com",
    "organization": "dummy",
    "_disable_authentication": True,
    "no_sse_connection": True,
    "skip_version_check": True,
}


def disable_http_retry(clt: SimAIClient, url: str):
    "Avoids slow tests due to retry backoff"
    adapter = clt._api._session.get_adapter(url)
    adapter.max_retries = 0


#
# TESTS
#
def test_client_without_config_tls_ca_bundle(tls_root_certificate, https_server):
    # Default config, using certifi's certificate store
    clt = SimAIClient(**BASE_CLT_ARGS)
    disable_http_retry(clt, https_server)
    # By default, the self-signed test CA is not accepted
    with pytest.raises(err.ConnectionError):
        clt._api._get(https_server)
    # One can use REQUESTS_CA_BUNDLE
    with patch.dict(os.environ, {"REQUESTS_CA_BUNDLE": str(tls_root_certificate["ca"])}):
        clt._api._get(https_server, return_json=False)


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason='"system" requires Python >= 3.10, "patch" is broken in python 3.10',
)
def test_client_config_tls_ca_bundle_system(tls_root_certificate, https_server):
    clt = SimAIClient(**BASE_CLT_ARGS, tls_ca_bundle="system")
    disable_http_retry(clt, https_server)
    # The system CA rejects the test CA by default
    with pytest.raises(err.ConnectionError):
        clt._api._get(https_server)

    # If the host system trusts the test CA, pysimai trusts it !
    @contextlib.contextmanager
    def load_test_ca_as_truststore_system_ca(ctx: "ssl.SSLContext"):
        ctx.load_verify_locations(cafile=tls_root_certificate["ca"])
        yield

    with patch(
        "truststore._api._configure_context", side_effect=load_test_ca_as_truststore_system_ca
    ):
        clt._api._get(https_server, return_json=False)


@pytest.mark.skipif(
    sys.version_info >= (3, 10), reason="The error is only raised for python < 3.10"
)
def test_client_config_tls_ca_bundle_system_on_usupported_python_version():
    with pytest.raises(err.ConfigurationError, match="python >= 3.10"):
        SimAIClient(**BASE_CLT_ARGS, tls_ca_bundle="system")


def test_client_config_tls_ca_bundle_unsecure_none(https_server):
    clt = SimAIClient(**BASE_CLT_ARGS, tls_ca_bundle="unsecure-none")
    clt._api._get(https_server, return_json=False)


def test_client_config_tls_ca_bundle_path(tls_root_certificate, https_server):
    clt = SimAIClient(**BASE_CLT_ARGS, tls_ca_bundle=tls_root_certificate["ca"])
    clt._api._get(https_server, return_json=False)
