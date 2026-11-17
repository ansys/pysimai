:description: Create and configure the PySimAI client: SimAIClient for SimAI models, GeomAIClient for GeomAI models, the default project and workspace of each, and all the ClientConfig options.

.. _configuration:
.. py:module:: ansys.simai.core.utils.configuration

Configure the PySimAI client
============================

**Applies to:** SimAI models and GeomAI models

Every PySimAI script starts with a :class:`~ansys.simai.core.client.SimAIClient` instance,
which connects to your Ansys SimAI organization and gives access to all the other objects.
This page shows how to create the client, configure it for SimAI models and for GeomAI models,
and which configuration options it accepts. To sign in without a browser or run scripts without
prompts, see :doc:`/getting-started/authenticate`.

Create the client
-----------------

To create a :class:`~ansys.simai.core.client.SimAIClient` instance, pass the configuration
parameters to its constructor. The ``organization`` parameter is the name of your Ansys SimAI
organization, as it appears in the web app URL: ``https://simai.ansys.com/<organization-name>``.

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    for project in simai_client.projects.list():
        print(project.name)

By default, the client prompts you for any missing parameter and opens your web browser so
that you can sign in. For the other ways to authenticate, see :doc:`/getting-started/authenticate`.

To keep the parameters out of your scripts, store them in a configuration file. For more
information, see :doc:`/getting-started/use-a-configuration-file`.

Configure the client for SimAI models
-------------------------------------

The :class:`~ansys.simai.core.client.SimAIClient` instance is the client for SimAI models. Its
directories, such as ``simai_client.projects``, ``simai_client.training_data``, and
``simai_client.workspaces``, give access to the objects of SimAI models.

Set a default project and workspace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some methods, such as :meth:`GeometryDirectory.list() <ansys.simai.core.data.geometries.GeometryDirectory.list>`,
use the current workspace of the client when you don't pass a workspace. To set the current
project and workspace when you create the client, pass their names:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="<your_organization>",
        project="<your_project_name>",
        workspace="<your_workspace_name>",
    )

To change them later, call :meth:`~ansys.simai.core.client.SimAIClient.set_current_project`
and :meth:`~ansys.simai.core.client.SimAIClient.set_current_workspace`.

Configure the client for GeomAI models
--------------------------------------

GeomAI models have their own client, :class:`~ansys.simai.core.data.geomai.client.GeomAIClient`.
You don't create it yourself: you get it from the ``geomai`` property of the
:class:`~ansys.simai.core.client.SimAIClient` object, which passes it its configuration. The
GeomAI client has its own directories (``geomai_client.projects``, ``geomai_client.models``,
and so on) and its own current project and current workspace:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    # GeomAI models have their own client, created from the PySimAI client
    geomai_client = simai_client.geomai
    for project in geomai_client.projects.list():
        print(project.name)

The projects, training data, and workspaces of GeomAI models are separate from those of SimAI
models. For details, see :doc:`/getting-started/overview/architecture`.

Set a default GeomAI project and workspace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set the current project and workspace of the GeomAI client when you create the PySimAI
client, pass their names with the ``geomai_project`` and ``geomai_workspace`` parameters:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="<your_organization>",
        geomai_project="<your_geomai_project_name>",
        geomai_workspace="<your_geomai_workspace_name>",
    )
    geomai_client = simai_client.geomai

To change them later, call
:meth:`GeomAIClient.set_current_project() <ansys.simai.core.data.geomai.client.GeomAIClient.set_current_project>`
and
:meth:`GeomAIClient.set_current_workspace() <ansys.simai.core.data.geomai.client.GeomAIClient.set_current_workspace>`
on ``simai_client.geomai``.

Configuration options
---------------------

The :class:`~ansys.simai.core.client.SimAIClient` constructor accepts the options of
``ClientConfig``. These are the options you use most often:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``organization``
     - Name of your Ansys SimAI organization. Required.
   * - ``project``, ``workspace``
     - Names of the project and workspace of SimAI models to use by default.
   * - ``geomai_project``, ``geomai_workspace``
     - Names of the project and workspace of GeomAI models to use by default.
   * - ``credentials``, ``offline_token``, ``access_token``
     - Ways to authenticate without the web browser. See :doc:`/getting-started/authenticate`.
   * - ``interactive``
     - ``True`` by default. With ``False``, the client never prompts. See
       :ref:`Interactive mode`.
   * - ``https_proxy``, ``tls_ca_bundle``
     - Proxy URL and TLS certificate settings. See :doc:`/getting-started/work-behind-a-proxy`.

.. dropdown:: All the configuration options of ClientConfig

   .. autopydantic_model:: ClientConfig
     :model-show-config-summary: False
     :model-show-validator-summary: False
     :model-show-json: False
     :model-show-field-summary: False
     :model-show-validator-members: False
     :field-list-validators: False

Expected result when you configure the PySimAI client
-----------------------------------------------------

The code in "Create the client" prints the names of the projects of SimAI models in your
organization. The code in "Configure the client for GeomAI models" prints the names of the
projects of GeomAI models.

Errors when you configure the PySimAI client
--------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.InvalidConfigurationError`
     - A parameter is invalid or missing with ``interactive=False``.
     - Pass every required parameter.
   * - :class:`~ansys.simai.core.errors.InvalidConfigurationError`
     - The ``project``, ``workspace``, ``geomai_project``, or ``geomai_workspace`` you passed
       doesn't exist. The message lists the available names.
     - Use one of the names in the message.
   * - :class:`~ansys.simai.core.errors.ConfigurationError`
     - ``tls_ca_bundle="system"`` on Python earlier than 3.10.
     - Upgrade Python, or see :doc:`/getting-started/work-behind-a-proxy`.

For the authentication errors, see :doc:`/getting-started/authenticate`. For all the exceptions,
see :doc:`/user-guide/common-tasks/handle-errors`.

More about how to configure the PySimAI client
----------------------------------------------

- :class:`~ansys.simai.core.client.SimAIClient`
- :class:`~ansys.simai.core.data.geomai.client.GeomAIClient`
- :doc:`/getting-started/authenticate`
- :doc:`/getting-started/use-a-configuration-file`
- :doc:`/getting-started/work-behind-a-proxy`
- :doc:`/getting-started/overview/architecture`
