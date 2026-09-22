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

To fix the issue:

1. Extract the certificates used by your company-configured browser on ``https://simai.ansys.com``.
2. Set the ``REQUESTS_CA_BUNDLE`` environment variable:

   .. code:: python

     import os
     from pathlib import Path

     os.environ["REQUESTS_CA_BUNDLE"] = Path(
         "~/Downloads/ansys-simai-chain.pem"
     ).expanduser()
     client = ansys.simai.core.from_config()
