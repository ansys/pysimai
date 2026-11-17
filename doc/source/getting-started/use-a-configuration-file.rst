:description: Store the PySimAI client parameters in a TOML configuration file, use profiles, and create the client from the file.

.. _config_file:

Use a configuration file
========================

**Applies to:** SimAI models and GeomAI models

A configuration file keeps the parameters of the PySimAI client out of your scripts. Create the
client from the file with :py:meth:`SimAIClient.from_config() <ansys.simai.core.client.SimAIClient.from_config>`,
also available as ``asc.from_config()``.

Write the configuration file
----------------------------

The configuration file uses the `TOML <https://toml.io/>`_ format. Each section is a profile,
and each key is a parameter of the :class:`~ansys.simai.core.client.SimAIClient` constructor.
For the list of parameters, see :ref:`configuration`.

Save this content in ``~/.ansys/simai.conf`` on Linux or macOS, or in
``C:\Users\<user>\AppData\Roaming\Ansys\simai.conf`` on Windows:

.. code-block:: toml

   [default]
   organization = "<your_organization>"
   workspace = "<your_workspace_name>"

Then create the client from it:

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.from_config()

   print(simai_client.current_workspace.name)

This example stores credentials and turns on two-factor authentication:

.. code-block:: toml

   [default]
   organization = "<your_organization>"

   [default.credentials]
   username = "<your_email>"
   password = "<your_password>"
   totp_enabled = true

A configuration file with a password gives access to your account: restrict its permissions,
and don't commit it.

Place the file in a default location
------------------------------------

When you don't pass a path, ``from_config()`` uses the first file it finds in the default
locations of your operating system.

On Linux and macOS, the default locations are, in order:

* ``$XDG_CONFIG_HOME/ansys_simai.conf``
* ``$XDG_CONFIG_HOME/ansys/simai.conf``
* ``~/.ansys_simai.conf``
* ``~/.ansys/simai.conf``
* ``/etc/ansys_simai.conf``
* ``/etc/ansys/simai.conf``

``$XDG_CONFIG_HOME`` defaults to ``~/.config``.

On Windows 7 to 11, the default location is
``C:\Users\<user>\AppData\Roaming\Ansys\simai.conf``.

On Windows XP, the default location is
``C:\Documents and Settings\<user>\Local Settings\Application Data\Ansys\simai.conf``.

To use a file in another location, pass its path:

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.from_config(path="<path/to/your/config/file>")

Use several profiles
--------------------

A configuration file can hold several profiles, one per section. ``from_config()`` loads the
``default`` profile unless you pass another one:

.. code-block:: toml

   [default]
   organization = "<your_organization>"
   workspace = "<your_workspace_name>"

   [alternative]
   organization = "<your_organization>"
   workspace = "<another_workspace_name>"
   project = "<another_project_name>"

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.from_config(profile="alternative")

Override a parameter of the file
--------------------------------

Keyword arguments of ``from_config()`` override the values of the file:

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.from_config(workspace="<another_workspace_name>")

Expected result when you use a configuration file
-------------------------------------------------

The code in "Write the configuration file" prints the name of the workspace set in the
configuration file.

Errors when you use a configuration file
----------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ConfigurationNotFoundError`
     - No configuration file exists at the path you passed or in the default locations.
     - Create the file in a default location, or pass its path.
   * - :class:`~ansys.simai.core.errors.InvalidConfigurationError`
     - The file isn't valid TOML, the profile you asked for has no section in the file, or a
       parameter is invalid.
     - Fix the syntax, add the ``[<profile>]`` section, or fix the parameter.

More about how to use a configuration file
------------------------------------------

- :py:meth:`~ansys.simai.core.client.SimAIClient.from_config`
- :doc:`/getting-started/configure-the-client`
- :doc:`/getting-started/work-behind-a-proxy`
