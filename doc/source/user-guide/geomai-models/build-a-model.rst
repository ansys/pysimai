:description: Start the build of a GeomAI model with PySimAI, wait for it with a timeout, handle a failed build, and cancel a build in progress.

.. _geomai_models_build_a_model:

Build a GeomAI model
====================

**Applies to:** GeomAI models

To build a GeomAI model, pass a project and a
:class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration` object to
:meth:`geomai_client.models.build()<ansys.simai.core.data.geomai.models.GeomAIModelDirectory.build>`,
then wait for the returned :class:`~ansys.simai.core.data.geomai.models.GeomAIModel` object with
``wait()``.

Script to build a GeomAI model
------------------------------

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration
   from ansys.simai.core.errors import ProcessingError

   simai_client = asc.SimAIClient(organization="<your_organization>")
   geomai_client = simai_client.geomai

   project = geomai_client.projects.get(name="<your_project_name>")

   # Check the training data before the build of a GeomAI model
   # Check that all training data is ready before the build.
   project_data = project.list_training_data()
   ready_data = [data for data in project_data if data.is_ready]
   print(f"Project has {len(ready_data)}/{len(project_data)} ready training data")

   # Start the build of a GeomAI model
   configuration = GeomAIModelConfiguration(build_preset="default")
   model = geomai_client.models.build(project, configuration)
   print(f"Started build for model {model.id}")

   # Wait for the build of a GeomAI model
   # wait() returns False on timeout and raises ProcessingError if the build fails.
   try:
       while not model.wait(timeout=60):
           print(f"Model {model.id} is still training...")
       print(f"Model {model.id} trained successfully and is ready to use.")

       # Get the workspace of a trained GeomAI model
       workspace = project.get_last_workspace()
       if workspace is not None:
           print(f"Workspace: {workspace.name}")
   except ProcessingError:
       print(f"Model training failed: {model.failure_reason}")

Check the training data before the build of a GeomAI model
----------------------------------------------------------

A GeomAI model build uses the training data of the project. Training data that isn't processed
yet, or that failed processing, can make the build fail. Count the ready training data with
:meth:`project.list_training_data()<ansys.simai.core.data.geomai.projects.GeomAIProject.list_training_data>`
and the ``is_ready`` property:

.. code-block:: python

   project_data = project.list_training_data()
   ready_data = [data for data in project_data if data.is_ready]
   print(f"Project has {len(ready_data)}/{len(project_data)} ready training data")

For how to wait for processing and fix invalid geometries, see
:doc:`/user-guide/geomai-models/upload-training-data`.

Start the build of a GeomAI model
---------------------------------

The ``geomai_client.models.build()`` method takes the project, as an object or an ID, and the
configuration, as a ``GeomAIModelConfiguration`` object or a dictionary. It returns a
``GeomAIModel`` object right away, while the build runs on Ansys SimAI:

.. code-block:: python

   configuration = GeomAIModelConfiguration(build_preset="default")
   model = geomai_client.models.build(project, configuration)

The project method
:meth:`project.build_model()<ansys.simai.core.data.geomai.projects.GeomAIProject.build_model>`
does the same thing: ``model = project.build_model(configuration)``.

For how to choose the configuration, see :doc:`/user-guide/geomai-models/configure-a-model`.

Wait for the build of a GeomAI model
------------------------------------

The ``wait()`` method of ``GeomAIModel`` blocks until the build ends. With a ``timeout`` in
seconds, ``wait()`` returns ``False`` if the build is still running when the timeout expires, and
``True`` when the build has finished. If the build fails, ``wait()`` raises
:class:`~ansys.simai.core.errors.ProcessingError`, and the reason is in ``failure_reason``.

Call ``wait()`` in a loop to print progress, and handle the failure with ``try``/``except``:

.. code-block:: python

   try:
       while not model.wait(timeout=60):
           print(f"Model {model.id} is still training...")
       print(f"Model {model.id} trained successfully and is ready to use.")
   except ProcessingError:
       print(f"Model training failed: {model.failure_reason}")

Without a timeout, ``model.wait()`` waits until the build ends, which can take several hours
depending on the build preset.

Get the workspace of a trained GeomAI model
-------------------------------------------

When the build succeeds, Ansys SimAI creates a workspace for the trained GeomAI model. You run
predictions and projections in this workspace. Get the last workspace of the project with
:meth:`project.get_last_workspace()<ansys.simai.core.data.geomai.projects.GeomAIProject.get_last_workspace>`,
which returns ``None`` if the project has no workspace, or a workspace by name with
:meth:`geomai_client.workspaces.get()<ansys.simai.core.data.geomai.workspaces.GeomAIWorkspaceDirectory.get>`:

.. code-block:: python

   workspace = project.get_last_workspace()
   # Or by name. Workspace names typically follow the pattern "<your_project_name> #<number>".
   workspace = geomai_client.workspaces.get(name="<your_workspace_name>")

To list all workspaces of the project, use
:meth:`project.list_workspaces()<ansys.simai.core.data.geomai.projects.GeomAIProject.list_workspaces>`.

Cancel the build of a GeomAI model
----------------------------------

To stop a build in progress, call
:meth:`project.cancel_build()<ansys.simai.core.data.geomai.projects.GeomAIProject.cancel_build>`
on the project, or
:meth:`geomai_client.projects.cancel_build()<ansys.simai.core.data.geomai.projects.GeomAIProjectDirectory.cancel_build>`
with the project or its ID. Both raise :class:`~ansys.simai.core.errors.ProcessingError` if no build
is pending for the project:

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.errors import ProcessingError

   simai_client = asc.SimAIClient(organization="<your_organization>")
   geomai_client = simai_client.geomai

   project = geomai_client.projects.get(name="<your_project_name>")
   try:
       project.cancel_build()
       print("Build canceled.")
   except ProcessingError:
       print("No build pending for this project.")

Expected result when you build a GeomAI model
---------------------------------------------

The complete script prints the number of ready training data, the ID of the GeomAI model, a
progress line every 60 seconds, and then
``Model <model_id> trained successfully and is ready to use.`` followed by the name of the new
workspace. If the build fails, it prints ``Model training failed:`` and the reason.

Errors when you build a GeomAI model
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - Raised by ``wait()``: the build failed.
     - Read ``model.failure_reason``. Check that all training data is ready and valid, then start
       a new build.
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - Raised by ``cancel_build()``: no build is pending for the project.
     - No action needed. The project has no build to cancel.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The configuration isn't valid, for example both ``build_preset`` and ``nb_epochs`` are set.
     - Fix the configuration. See :doc:`/user-guide/geomai-models/configure-a-model`.
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No project or workspace has the requested name.
     - Check the name of the project or workspace.

More about how to build a GeomAI model
--------------------------------------

- :class:`~ansys.simai.core.data.geomai.models.GeomAIModelDirectory`
- :class:`~ansys.simai.core.data.geomai.models.GeomAIModel`
- :class:`~ansys.simai.core.data.geomai.projects.GeomAIProject`
- :doc:`/user-guide/geomai-models/configure-a-model`
- :doc:`/user-guide/geomai-models/evaluate-a-model`
- :ref:`ref_build_model`
