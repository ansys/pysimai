:description: Ansys SimAI has two separate types of AI model. In PySimAI, SimAI models use SimAIClient and GeomAI models use GeomAIClient, each with its own projects, training data, workspaces, models and predictions, and the data isn't interoperable.

.. _home_architecture:

Architecture of Ansys SimAI and PySimAI
=======================================

**Applies to:** SimAI models and GeomAI models

The Ansys SimAI platform trains two separate types of :term:`AI model`: :term:`SimAI models
<SimAI model>` and :term:`GeomAI models <GeomAI model>`. Each type has its own data and its own
objects on the platform, and its own client in PySimAI. Data uploaded for one type isn't
available to the other.

Two types of AI model, two sets of data
---------------------------------------

On the Ansys SimAI platform, a SimAI model and a GeomAI model each have their own
:term:`projects <project>`, :term:`training data`, :term:`model builds <model build>`,
:term:`workspaces <workspace>`, :term:`geometries <geometry>`, and
:term:`predictions <prediction>`. The two types learn from different data and produce
different results:

- A SimAI model learns from simulation cases and predicts the physical fields of a new
  geometry. Each simulation case has a surface file, and can also have a volume file and a
  scalar file.
- A GeomAI model learns from geometry files only, and generates new geometries.

Both types belong to the same :term:`organization`, and you sign in to both with the same
account.

Two clients in PySimAI
----------------------

PySimAI has one client for each type of AI model:

- :class:`~ansys.simai.core.client.SimAIClient` is the client for SimAI models. You create it
  with ``asc.SimAIClient(organization="<your_organization>")``. Its directories, such as
  ``simai_client.projects`` and ``simai_client.training_data``, only handle the objects of SimAI
  models.
- :class:`~ansys.simai.core.data.geomai.client.GeomAIClient` is the client for GeomAI models.
  You don't create it yourself: you get it from the
  :attr:`~ansys.simai.core.client.SimAIClient.geomai` property of the SimAI client, with
  ``geomai_client = simai_client.geomai``. Its directories, such as ``geomai_client.projects``
  and ``geomai_client.training_data``, only handle the objects of GeomAI models.

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")
    geomai_client = simai_client.geomai

    # Projects of SimAI models
    for project in simai_client.projects.list():
        print(project.name)

    # Projects of GeomAI models: a different list
    for project in geomai_client.projects.list():
        print(project.name)

The SimAI client passes its configuration to the GeomAI client, so both use the same
organization, authentication, and connection settings. Each client keeps its own current project
and current workspace: ``project`` and ``workspace`` set them for the SimAI client, and
``geomai_project`` and ``geomai_workspace`` set them for the GeomAI client. For details, see
:doc:`/getting-started/configure-the-client`.

Data isn't interoperable between the two types of AI model
----------------------------------------------------------

The data of a SimAI model and the data of a GeomAI model are separate on the platform. In
PySimAI, each directory of the GeomAI client calls its own endpoints of the Ansys SimAI API,
under the ``geomai/`` path, so the two clients never see each other's objects. In practice:

- Training data uploaded for a SimAI model can't train a GeomAI model, and training data
  uploaded for a GeomAI model can't train a SimAI model.
- A project or a workspace of one type isn't visible to the client of the other type.
  ``simai_client.projects.list()`` doesn't return GeomAI projects, and
  ``geomai_client.projects.list()`` doesn't return SimAI projects.
- The objects of one type can't be passed to the methods of the other client. For example, a
  :class:`~ansys.simai.core.data.geomai.projects.GeomAIProject` can't be used to build a SimAI
  model.

To use the same designs with both types of AI model, upload them separately to each one: as
simulation folders for a SimAI model, and as geometry files for a GeomAI model.

More about the architecture of Ansys SimAI and PySimAI
------------------------------------------------------

- :doc:`/getting-started/overview/key-concepts`
- :doc:`/getting-started/overview/object-model`
- :doc:`/getting-started/overview/glossary`
- :class:`~ansys.simai.core.client.SimAIClient`
- :class:`~ansys.simai.core.data.geomai.client.GeomAIClient`
