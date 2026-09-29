.. _config_file:

Configuration file
==================

To create a :class:`~ansys.simai.core.client.SimAIClient`
instance from a configuration file, you use the
:py:meth:`~ansys.simai.core.client.SimAIClient.from_config` method:

.. code-block:: python

  simai = ansys.simai.core.from_config()

Location
--------

If no path is given, the :class:`~ansys.simai.core.client.SimAIClient`
instance looks at default locations. These locations differ according to
your operating system.

**Linux/MacOS**

For UNIX systems, the default locations are, in order:

* ``$XDG_CONFIG_HOME/ansys_simai.conf``
* ``$XDG_CONFIG_HOME/ansys/simai.conf``
* ``~/.ansys_simai.conf``
* ``~/.ansys/simai.conf``
* ``/etc/ansys_simai.conf``
* ``/etc/ansys/simai.conf``

.. note ::

   The first location found is used. ``$XDG_CONFIG_HOME`` defaults to ``~/.config``.

**Windows XP**

* ``C:\Documents and Settings\<user>\Local Settings\Application Data\Ansys\simai.conf``

**Windows 7 to 11**

* ``C:\Users\<user>\AppData\Roaming\Ansys\simai.conf``

Optionally, you can specify the path yourself:

.. code-block:: python

  simai = ansys.simai.core.from_config(path="/path/to/my/config")

Content
-------

You write the configuration file in `TOML <https://toml.io/>`_.
From this file, you can pass parameters for configuring
the :class:`~ansys.simai.core.client.SimAIClient` instance (see :ref:`configuration`).


Example
"""""""

.. code-block:: TOML

   [default]
   organization = "company"

   [default.credentials]
   username = "user@company.com"
   password = "hunter12"
   totp_enabled = true


Profiles
--------

The :class:`~ansys.simai.core.client.SimAIClient` instance supports having multiple
configurations in a single file through profiles, which are loaded like this:

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
