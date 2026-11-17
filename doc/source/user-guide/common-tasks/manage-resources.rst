:description: List, rename, and delete projects, workspaces, geometries, predictions, and training data with PySimAI, for both types of AI model.

.. _common_tasks_manage_resources:

List, rename, and delete resources
==================================

**Applies to:** SimAI models and GeomAI models

PySimAI lists, renames, and deletes the objects of your organization through the ``list()``,
``rename()``, and ``delete()`` methods of each object and of each client directory. This page
covers projects, workspaces, geometries, predictions, and training data, for both types of AI
model.

.. warning::

   Deletion is permanent. PySimAI doesn't ask for confirmation, and you can't restore a deleted
   object. Training data is shared by all the users and projects of your organization, so
   deleting a training data point removes it for everyone.

Script to list, rename, and delete resources
--------------------------------------------

This script lists the projects and workspaces of your organization, renames a workspace, and
deletes one geometry with its predictions:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    # List resources: the projects and their workspaces
    for project in simai_client.projects.list():
        workspace_names = [workspace.name for workspace in project.list_workspaces()]
        print(f"{project.name}: {workspace_names}")

    # Rename resources: a workspace
    workspace = simai_client.workspaces.get(name="<your_workspace_name>")
    workspace.rename("<new_workspace_name>")

    # List resources: the geometries of the workspace with the number of predictions of each
    for geometry in workspace.list_geometries():
        print(f"{geometry.name}: {len(geometry.list_predictions())} predictions")

    # Delete resources: a geometry, with its predictions and postprocessings
    geometry = simai_client.geometries.get(name="<your_geometry_name>", workspace=workspace)
    geometry.delete()

Available methods
-----------------

``rename()`` and ``delete()`` are methods of the objects. Each directory of the client also has a
``delete()`` method that takes an object or its ID, for example
``simai_client.projects.delete(project)``.

.. list-table:: SimAI models
   :header-rows: 1
   :widths: 16 42 18 24

   * - Object
     - List
     - Rename
     - Delete
   * - Project
     - ``simai_client.projects.list()``
     - ``project.rename(new_name)``
     - ``project.delete()``
   * - Workspace
     - ``simai_client.workspaces.list()``, ``project.list_workspaces()``
     - ``workspace.rename(new_name)``
     - ``workspace.delete()``
   * - Geometry
     - ``simai_client.geometries.list(workspace=...)``, ``workspace.list_geometries()``
     - ``geometry.rename(new_name)``
     - ``geometry.delete()``
   * - Prediction
     - ``simai_client.predictions.list(workspace=...)``, ``workspace.list_predictions()``,
       ``geometry.list_predictions()``
     - Not available
     - ``prediction.delete()``
   * - Training data point
     - ``simai_client.training_data.list()``, ``project.list_training_data()``
     - ``training_data.rename(new_name)``
     - ``training_data.delete()``

.. list-table:: GeomAI models (``geomai_client = simai_client.geomai``)
   :header-rows: 1
   :widths: 16 42 18 24

   * - Object
     - List
     - Rename
     - Delete
   * - Project
     - ``geomai_client.projects.list()``
     - ``project.rename(new_name)``
     - ``project.delete()``
   * - Workspace
     - ``geomai_client.workspaces.list()``, ``project.list_workspaces()``
     - ``workspace.rename(new_name)``
     - ``workspace.delete()``
   * - Geometry
     - ``geomai_client.geometries.list()``
     - ``geometry.rename(new_name)``
     - ``geometry.delete()``
   * - Prediction
     - ``geomai_client.predictions.list(workspace=...)``, ``workspace.list_predictions()``
     - Not available
     - ``prediction.delete()``
   * - Training data point
     - ``geomai_client.training_data.list()``, ``project.list_training_data()``
     - Not available
     - ``training_data.delete()``

List resources
--------------

The ``list()`` methods of ``simai_client.projects``, ``simai_client.workspaces``, and
``simai_client.training_data`` take two optional parameters: ``filters``, and
``created_by_me=True`` to list only the objects that you created. The same methods exist on
``simai_client.geomai``.

``simai_client.geometries.list()`` and ``simai_client.predictions.list()`` list the objects of one
workspace: pass ``workspace``, or set the current workspace of the client first.
``simai_client.geomai.geometries.list()`` takes no parameter and lists all the GeomAI geometries.

Listing all the training data of an organization can take a long time. To list the training data
of one project, use ``project.list_training_data()``. To go through all of it, iterate with
``simai_client.training_data.iter()`` instead of building the full list:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    for training_data in simai_client.training_data.iter():
        print(training_data.name)

Rename resources
----------------

``rename()`` takes the new name and updates the object on the server:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    project = simai_client.projects.get(name="<your_project_name>")
    project.rename("<new_project_name>")
    print(project.name)

For a SimAI model geometry,
:meth:`Geometry.rename() <ansys.simai.core.data.geometries.Geometry.rename>` changes only the
stem of the filename: the extension can't change. If you pass an extension, it must be the same
as the original one. If the new name contains dots other than the one of the extension, pass the
extension too.

Predictions and GeomAI training data points have no ``rename()`` method.

Delete resources
----------------

``delete()`` removes the object from the server immediately and for good. Get the object first,
check that it's the right one, then delete it:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    workspace = simai_client.workspaces.get(name="<your_workspace_name>")
    print(f"Deleting workspace {workspace.name} ({workspace.id})")
    workspace.delete()

Deleting a SimAI model geometry also deletes its predictions and postprocessings.

Remove training data from a project without deleting it
-------------------------------------------------------

A training data point belongs to the organization and can be part of several projects. To take it
out of one project only, remove it from the project instead of deleting it:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    project = simai_client.projects.get(name="<your_project_name>")
    training_data = simai_client.training_data.get(name="<your_training_data_name>")
    training_data.remove_from_project(project)

:meth:`TrainingData.remove_from_project() <ansys.simai.core.data.training_data.TrainingData.remove_from_project>`
raises :class:`~ansys.simai.core.errors.ApiClientError` if the training data point is the
reference sample of the project, or if the project is being trained. For GeomAI models, use
:meth:`GeomAITrainingData.remove_from_project() <ansys.simai.core.data.geomai.training_data.GeomAITrainingData.remove_from_project>`.

Expected result when you list, rename, and delete resources
-----------------------------------------------------------

The complete script prints each project with the names of its workspaces, then each geometry of
the renamed workspace with its number of predictions. The geometry you named no longer exists on
the server.

Errors when you list, rename, and delete resources
--------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No object has the name or ID you passed to ``get()`` or ``delete()``.
     - Check the name or ID with ``list()``.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - You passed both a name and an ID to ``get()``, or neither.
     - Pass one of them.
   * - :class:`~ansys.simai.core.errors.ApiClientError`
     - The server refused the operation, for example removing the reference sample from its
       project.
     - Read the message, which contains the reason returned by the server.

For all the exceptions, see :doc:`/user-guide/common-tasks/handle-errors`.

More about how to list, rename, and delete resources
----------------------------------------------------

- :class:`~ansys.simai.core.data.projects.ProjectDirectory`
- :class:`~ansys.simai.core.data.workspaces.WorkspaceDirectory`
- :class:`~ansys.simai.core.data.geometries.GeometryDirectory`
- :class:`~ansys.simai.core.data.predictions.PredictionDirectory`
- :class:`~ansys.simai.core.data.training_data.TrainingDataDirectory`
- :class:`~ansys.simai.core.data.geomai.client.GeomAIClient`
- :doc:`/getting-started/overview/object-model`
