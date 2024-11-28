.. _proxy:

Working behind a proxy
======================

By default, the SimAI client attempts to get your proxy configuration, if any, from your system.

SimAI client configuration
++++++++++++++++++++++++++

You can manually set a proxy when creating the :ref:`SimAIClient<simai_client>`
instance:

.. code-block:: python

  import ansys.simai.core

  simai = ansys.simai.core.SimAIClient(https_proxy="http://company_proxy:3128")

Alternatively, you can store the proxy information in your :ref:`configuration file<config_file>`.

.. note::
   Setting this parameter overrides the default configuration retrieved from your system.


Troubleshooting
~~~~~~~~~~~~~~~

If you get an error of the type ``ProxyError([...], SSLCertVerificationError([...]``,
it is likely that your proxy setup looks like ``|computer|<-https->|proxy|<-https->|internet|``.
Because your web browser uses a special
`proxy auto-configuration <https://en.wikipedia.org/wiki/Proxy_auto-config>`_ file, the
proxy is not trusted by your computer.

There are multiple ways to fix this issue:

1. Try ``tls_ca_bundle="system"`` (requires ``python>=3.10``, see :ref:`configuration`).
2. Extract the required CA certificate:

    a. Extract the certificates used by your company-configured browser on ``https://simai.ansys.com``.
    b. Set ``tls_ca_bundle`` (or the ``REQUESTS_CA_BUNDLE`` environment variable):

       .. code-block:: TOML

         [default]
         organization = "company"
         tls_ca_bundle = "/home/username/Documents/my_company_proxy_ca_bundle.pem"
3. As a temporary last resort, one can use ``tls_ca_bundle="unsecure-none"`` (contact your IT department).
