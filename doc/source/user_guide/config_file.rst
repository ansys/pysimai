.. _config_file:

Configuration File
==================

To create a client from a configuration file, you can use the
:py:meth:`~ansys.simai.core.client.SimAIClient.from_config` function :

.. code-block:: python

  simai = ansys.simai.core.from_config()

Location
--------

If no ``path`` is given, the ``SimAIClient`` will look at default locations.
These locations differ according to your operating system:

* Linux/MacOS:

  For UNIX systems the default locations are, in order :

  * ``$XDG_CONFIG_HOME/ansys_simai.conf``
  * ``$XDG_CONFIG_HOME/ansys/simai.conf``
  * ``~/.ansys_simai.conf``
  * ``~/.ansys/simai.conf``
  * ``/etc/ansys_simai.conf``
  * ``/etc/ansys/simai.conf``

  .. note ::

    Only the first one found will be used.

    ``$XDG_CONFIG_HOME`` defaults to ``~/.config``.

* For Windows XP :

  * ``C:\Documents and Settings\<user>\Local Settings\Application Data\Ansys\simai.conf``

* For Windows 7 to 11:

  * ``C:\Users\<user>\AppData\Roaming\Ansys\simai.conf``

Optionally you can specify the path yourself:

.. code-block:: python

  simai = ansys.simai.core.from_config(path="/path/to/my/config")

Content
-------

The configuration file is written in `TOML <https://toml.io/>`_.
Any parameter used to configure the :class:`~ansys.simai.core.client.SimAIClient` can
be be passed from the configuration file.


Example :
"""""""""

.. code-block:: TOML

   [default]
   organization = "company"

   [default.credentials]
   username = "user@company.com"
   password = "hunter12"
   totp_enabled = true


Proxy :
"""""""

If your network is situated behind a proxy, then you will need to add its address
in a `https_proxy` key in the `[default]` block:

.. code-block:: TOML

   [default]
   organization = "company"
   https_proxy = "http://company_proxy_host:3128" # replacing host and port by the real value

Profiles
--------

The SDK supports having multiple configurations in a single file through profiles.

Profiles can be loaded like so :

.. code-block:: TOML

   [default]
   organization = "company"
   workspace = "my-usual-workspace"

   [alternative]
   organization = "company"
   workspace = "some-other-workspace"
   project = "red herring"

.. code-block:: python

  simai = ansys.simai.core.from_config(profile="alternative")
