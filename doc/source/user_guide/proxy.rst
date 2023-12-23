.. _proxy:

Working behind a proxy
======================

By default, the SDK will attempt to get your proxy configuration from your system if there is any.

SDK configuration
+++++++++++++++++

You can manually set a proxy for the SDK when creating an :ref:`SimAIClient<simai_client>`, like so :

.. code-block:: python

  import ansys.simai.core

  simai = ansys.simai.core.SimAIClient(https_proxy="http://company_proxy:3128")

Alternatively, you can store the proxy information in your :ref:`configuration file<config_file>`.

Note that setting this parameter will override the default configuration retrieved from your system.


Troubleshooting
~~~~~~~~~~~~~~~

In case you get an error or the type ``ProxyError([...], SSLCertVerificationError([...]``,
it is likely that your proxy setup looks like ``|computer|<-https->|proxy|<-https->|internet|``,
but the proxy is not trusted by your computer (your web browser uses a
`special configuration <https://en.wikipedia.org/wiki/Proxy_auto-config>`__).

To fix this:

1. Extract the certificates used by your company-configured browser on ``https://simai.ansys.com``
2. Set the ``REQUESTS_CA_BUNDLE`` environment variable:

  .. code:: python

    import os
    from pathlib import Path

    os.environ["REQUESTS_CA_BUNDLE"] = Path(
        "~/Downloads/ansys-simai-chain.pem"
    ).expanduser()
    client = ansys.simai.core.from_config()
