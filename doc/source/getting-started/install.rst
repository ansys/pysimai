:description: Install or upgrade PySimAI, the Python SDK for Ansys SimAI, with pip, and check the installed version.

.. _getting_started_install:

Install PySimAI
===============

**Applies to:** SimAI models and GeomAI models

Install the ``ansys-simai-core`` package with pip to use PySimAI.

Prerequisites
-------------

- Python 3.9 or later.
- An account in your :term:`organization`, to use PySimAI after installation.

Install the package
-------------------

Run this command:

.. code-block:: bash

   pip install ansys-simai-core --upgrade

Run the same command every time you want to upgrade PySimAI to the latest version.

Check the installed version
---------------------------

Print the version of the installed package:

.. code-block:: bash

   python -c "import ansys.simai.core as asc; print(asc.__version__)"

Expected result when you install PySimAI
----------------------------------------

The command prints the version number of ``ansys-simai-core``, for example ``0.4.9``.
When a newer version exists, the :class:`~ansys.simai.core.client.SimAIClient` constructor
logs a message about it, unless you set ``skip_version_check=True``.

More about how to install PySimAI
---------------------------------

- :doc:`/getting-started/configure-the-client`
- :doc:`/getting-started/quickstart-simai-model`
- :doc:`/getting-started/quickstart-geomai-model`
- :ref:`changelog`
