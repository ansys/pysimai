:description: Configure the PySimAI client to work behind a corporate proxy, and fix SSL certificate verification errors raised through the proxy.

.. _proxy:

Work behind a proxy
===================

**Applies to:** SimAI models and GeomAI models

By default, the :class:`~ansys.simai.core.client.SimAIClient` instance reads the proxy
configuration of your system, if any. This page shows how to set a proxy yourself, and how to
fix certificate errors when your proxy intercepts HTTPS traffic.

Set the proxy in the client
---------------------------

Pass the ``https_proxy`` parameter when you create the client.
This value overrides the proxy configuration of your system.

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.SimAIClient(
       organization="<your_organization>",
       https_proxy="<http://your_company_proxy:3128>",
   )

   print([project.name for project in simai_client.projects.list()])

Set the proxy in the configuration file
---------------------------------------

To keep the proxy out of your scripts, store it in your
:doc:`configuration file </getting-started/use-a-configuration-file>`:

.. code-block:: toml

   [default]
   organization = "<your_organization>"
   https_proxy = "<http://your_company_proxy:3128>"

Fix a certificate error raised through the proxy
------------------------------------------------

An error such as ``ProxyError([...], SSLCertVerificationError([...]`` usually means that your
proxy decrypts HTTPS traffic: ``|computer|<-https->|proxy|<-https->|internet|``. Your web browser
trusts the proxy through a
`proxy auto-configuration <https://en.wikipedia.org/wiki/Proxy_auto-config>`_ file, but Python
doesn't trust its certificate.

Try these fixes in order:

#. Use the CA certificates of your system. This option requires Python 3.10 or later:

   .. code-block:: toml

      [default]
      organization = "<your_organization>"
      tls_ca_bundle = "system"

#. If the first fix doesn't work, extract the CA certificate that your company-configured
   browser uses on ``https://simai.ansys.com``. Then set ``tls_ca_bundle``, or the
   ``REQUESTS_CA_BUNDLE`` environment variable, to the path of the certificate file:

   .. code-block:: toml

      [default]
      organization = "<your_organization>"
      tls_ca_bundle = "/home/username/Documents/my_company_proxy_ca_bundle.pem"

#. As a temporary last resort, and after you contact your IT department, turn off certificate
   validation with ``tls_ca_bundle = "unsecure-none"``.

Expected result when you work behind a proxy
--------------------------------------------

The code in "Set the proxy in the client" prints the names of the projects of your
organization.

Errors when you work behind a proxy
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ConnectionError`
     - The client can't reach the Ansys SimAI server, for example because the proxy address
       is wrong.
     - Check the value of ``https_proxy``.
   * - :class:`~ansys.simai.core.errors.ConfigurationError`
     - ``tls_ca_bundle = "system"`` on Python earlier than 3.10.
     - Upgrade Python, or use the path of a certificate file.

More about how to work behind a proxy
-------------------------------------

- :ref:`configuration`
- :doc:`/getting-started/use-a-configuration-file`
- :doc:`/user-guide/common-tasks/handle-errors`
