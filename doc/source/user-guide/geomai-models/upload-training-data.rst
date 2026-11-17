:description: Create a project for a GeomAI model with PySimAI, upload geometry files as training data, and wait for their processing.

.. _geomai_models_upload_training_data:

Upload training data for a GeomAI model
=======================================

**Applies to:** GeomAI models

To upload training data for a GeomAI model, create a project with
:meth:`geomai_client.projects.create()<ansys.simai.core.data.geomai.projects.GeomAIProjectDirectory.create>`,
then upload each geometry file with
:meth:`geomai_client.training_data.create_from_file()<ansys.simai.core.data.geomai.training_data.GeomAITrainingDataDirectory.create_from_file>`.

Script to upload training data for a GeomAI model
-------------------------------------------------

.. code-block:: python

   import os

   import ansys.simai.core as asc
   from ansys.simai.core.errors import NotFoundError, ProcessingError

   DATASET_PATH = "<path_to_your_geometry_folder>"  # Folder with .vtp or .stl files
   PROJECT_NAME = "<your_project_name>"

   simai_client = asc.SimAIClient(organization="<your_organization>")
   geomai_client = simai_client.geomai

   # Create or get a project for a GeomAI model
   # Get the project, or create it if it doesn't exist.
   try:
       project = geomai_client.projects.get(name=PROJECT_NAME)
   except NotFoundError:
       project = geomai_client.projects.create(PROJECT_NAME)

   # Upload a geometry file as GeomAI model training data
   # Upload each geometry file, or add it to the project if it's already uploaded.
   for fname in os.listdir(DATASET_PATH):
       if not fname.lower().endswith((".vtp", ".stl")):
           continue
       td_name = os.path.splitext(fname)[0]
       try:
           # Add existing training data to the project of a GeomAI model
           existing_td = geomai_client.training_data.get(name=td_name)
           existing_td.add_to_project(project)
       except NotFoundError:
           geomai_client.training_data.create_from_file(
               file=os.path.join(DATASET_PATH, fname), project=project
           )

   # Wait for the processing of GeomAI model training data
   project_data = project.list_training_data()
   for data in project_data:
       try:
           data.wait()
       except ProcessingError:
           print(f"'{data.name}' failed: {data.failure_reason}")

   ready_count = sum(1 for d in project_data if d.is_ready)
   print(f"Project '{project.name}': {ready_count}/{len(project_data)} training data ready.")

Create or get a project for a GeomAI model
------------------------------------------

A project for a GeomAI model, :class:`~ansys.simai.core.data.geomai.projects.GeomAIProject`, holds the
training data of a GeomAI model. Get an existing project by name with
:meth:`geomai_client.projects.get()<ansys.simai.core.data.geomai.projects.GeomAIProjectDirectory.get>`.
The method raises :class:`~ansys.simai.core.errors.NotFoundError` if no project has this name.
Create the project in that case:

.. code-block:: python

   try:
       project = geomai_client.projects.get(name="<your_project_name>")
   except NotFoundError:
       project = geomai_client.projects.create("<your_project_name>")

``geomai_client.projects.create()`` also accepts an optional ``description`` argument.

Upload a geometry file as GeomAI model training data
----------------------------------------------------

The
:meth:`create_from_file()<ansys.simai.core.data.geomai.training_data.GeomAITrainingDataDirectory.create_from_file>`
method creates a :class:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingData` object,
uploads the file, and starts its processing. The file must be a ``.vtp`` or ``.stl`` geometry that
meets the requirements in :ref:`geometry_requirements`. The name of the training data is the filename
name without its extension.

.. code-block:: python

   training_data = geomai_client.training_data.create_from_file(
       file="<path_to_your_geometry>.vtp", project=project
   )

If you don't pass ``project``, the training data is attached to the current project of the client,
if one is set.

Add existing training data to the project of a GeomAI model
-----------------------------------------------------------

Training data that you already uploaded doesn't need a new upload. Get it by name with
:meth:`geomai_client.training_data.get()<ansys.simai.core.data.geomai.training_data.GeomAITrainingDataDirectory.get>`
and add it to the project with
:meth:`add_to_project()<ansys.simai.core.data.geomai.training_data.GeomAITrainingData.add_to_project>`:

.. code-block:: python

   existing_td = geomai_client.training_data.get(name="<your_training_data_name>")
   existing_td.add_to_project(project)

To remove training data from a project, use
:meth:`remove_from_project()<ansys.simai.core.data.geomai.training_data.GeomAITrainingData.remove_from_project>`.

Wait for the processing of GeomAI model training data
-----------------------------------------------------

After upload, Ansys SimAI processes each geometry. List the training data of the project with
:meth:`project.list_training_data()<ansys.simai.core.data.geomai.projects.GeomAIProject.list_training_data>`
and call ``wait()`` on each item. ``wait()`` raises :class:`~ansys.simai.core.errors.ProcessingError`
if the processing fails. The reason is in ``failure_reason``.

.. code-block:: python

   for data in project.list_training_data():
       try:
           data.wait()
       except ProcessingError:
           print(f"'{data.name}' failed: {data.failure_reason}")

An "invalid geometry" failure means that the geometry isn't watertight, isn't manifold, or
self-penetrates. For how to fix it, see :doc:`/user-guide/geomai-models/prepare-training-data`.

Expected result when you upload training data for a GeomAI model
----------------------------------------------------------------

The script prints a line for each training data point that failed processing, then a summary
such as ``Project '<your_project_name>': 24/24 training data ready.``. When all training data is
ready, you can build a GeomAI model.

Errors when you upload training data for a GeomAI model
-------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No project or training data has the requested name.
     - Create the project, or upload the file with ``create_from_file()``.
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The processing of a geometry failed, for example because the geometry is invalid.
     - Read ``failure_reason``, fix the geometry, and upload it again.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The ``file`` argument isn't a valid path or named file.
     - Pass the path of a ``.vtp`` or ``.stl`` file.

More about how to upload training data for a GeomAI model
---------------------------------------------------------

- :class:`~ansys.simai.core.data.geomai.projects.GeomAIProjectDirectory`
- :class:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingDataDirectory`
- :class:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingData`
- :doc:`/user-guide/geomai-models/prepare-training-data`
- :doc:`/user-guide/geomai-models/configure-a-model`
- :ref:`ref_create_project_upload_data`
