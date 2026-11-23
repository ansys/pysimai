:description: Create a project, upload simulation folders as training data for a SimAI model, folder by folder or file by file, and add the training data to the project.

.. _simai_models_upload_training_data:

Upload the training data of a SimAI model
=========================================

**Applies to:** SimAI models

Upload your simulation folders to Ansys SimAI with
:meth:`TrainingData.upload_folder() <ansys.simai.core.data.training_data.TrainingData.upload_folder>`,
then add the training data to a :class:`~ansys.simai.core.data.projects.Project` object with
:meth:`TrainingData.add_to_project() <ansys.simai.core.data.training_data.TrainingData.add_to_project>`.
Training data belongs to your organization, so you can add the same training data point to
several projects.

Script to upload the training data of a SimAI model
---------------------------------------------------

This script creates a project, uploads each folder inside a dataset folder as one training data
point, adds it to the project, and waits for Ansys SimAI to process it.

.. code-block:: python

   import os

   import ansys.simai.core as asc
   from ansys.simai.core.errors import ProcessingError

   DATASET_PATH = "<path_to_your_dataset_folder>"

   simai_client = asc.SimAIClient(organization="<your_organization>")

   # Create a project
   project = simai_client.projects.create("<your_project_name>")

   uploaded = []
   for folder_name in os.listdir(DATASET_PATH):
       folder_path = os.path.join(DATASET_PATH, folder_name)
       if not os.path.isdir(folder_path):
           continue
       # Upload a simulation folder
       training_data = simai_client.training_data.create(folder_name)
       training_data.upload_folder(folder_path)

       # Add the training data to a project
       training_data.add_to_project(project)
       uploaded.append(training_data)
       print(f"Uploaded {folder_name}")

   for training_data in uploaded:
       try:
           training_data.wait()
           print(f"{training_data.name} is ready")
       except ProcessingError:
           print(f"{training_data.name} failed: {training_data.failure_reason}")

Create a project
----------------

A project gathers training data and a model configuration to build SimAI models. Create one with
:meth:`ProjectDirectory.create() <ansys.simai.core.data.projects.ProjectDirectory.create>`.
The ``description`` parameter is optional:

.. code-block:: python

   project = simai_client.projects.create("<your_project_name>", description="<your_description>")

To use a project that already exists, get it by name. The method raises
:class:`~ansys.simai.core.errors.NotFoundError` if no project has this name:

.. code-block:: python

   project = simai_client.projects.get(name="<your_project_name>")

Upload a simulation folder
--------------------------

To upload one simulation folder, create an empty
:class:`~ansys.simai.core.data.training_data.TrainingData` object, then upload the folder into it:

.. code-block:: python

   training_data = simai_client.training_data.create("<your_training_data_name>")
   training_data.upload_folder("<path_to_your_simulation_folder>")

The :meth:`~ansys.simai.core.data.training_data.TrainingData.upload_folder` method uploads every
file at the top level of the folder, except hidden files, and returns the list of
:class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart` objects it created. It then
requests the extraction of the data, so you don't need to call
:meth:`~ansys.simai.core.data.training_data.TrainingData.extract_data`. The method raises
:class:`~ansys.simai.core.errors.InvalidArguments` if the path isn't a folder.

The directory method
:meth:`TrainingDataDirectory.upload_folder() <ansys.simai.core.data.training_data.TrainingDataDirectory.upload_folder>`
does the same from the ID or object of the training data point:

.. code-block:: python

   simai_client.training_data.upload_folder(training_data, folder_path="<path_to_your_simulation_folder>")

Add the training data to a project
----------------------------------

A training data point is used in a model build only if it belongs to the project. Add it with
:meth:`~ansys.simai.core.data.training_data.TrainingData.add_to_project`, which accepts a
project object or a project ID:

.. code-block:: python

   training_data.add_to_project(project)

You can also add the training data point when you create it, with the ``project`` parameter of
:meth:`TrainingDataDirectory.create() <ansys.simai.core.data.training_data.TrainingDataDirectory.create>`:

.. code-block:: python

   training_data = simai_client.training_data.create("<your_training_data_name>", project=project)

To remove a training data point from a project, call
:meth:`~ansys.simai.core.data.training_data.TrainingData.remove_from_project`. This call fails if
the data point is the reference sample of the project or if the project is in a model build.

Upload a training data point file by file
-----------------------------------------

To control which files you upload, or to follow the progress of each upload, upload the files
one by one with
:meth:`TrainingData.upload_part() <ansys.simai.core.data.training_data.TrainingData.upload_part>`.
After the last file, call
:meth:`~ansys.simai.core.data.training_data.TrainingData.extract_data` so that Ansys SimAI
extracts the data from the uploaded parts:

.. code-block:: python

   training_data = simai_client.training_data.create("<your_training_data_name>", project=project)
   training_data.upload_part("<path_to_your_folder>/surface.vtp")
   training_data.upload_part("<path_to_your_folder>/scalars.json")
   training_data.extract_data()

Each file is a :obj:`~ansys.simai.core.data.types.NamedFile`: a path, from which PySimAI takes the
filename, or a ``(file, name)`` tuple. The name must contain the file extension. The optional
``monitor_callback`` parameter takes a :obj:`~ansys.simai.core.data.types.MonitorCallback`
function to follow the progress of the upload.

The directory method
:meth:`TrainingDataDirectory.upload_part() <ansys.simai.core.data.training_data.TrainingDataDirectory.upload_part>`
takes the training data point as first parameter. Its ``monitor_callback`` parameter has no
default value, so pass it explicitly:

.. code-block:: python

   simai_client.training_data.upload_part(
       training_data, "<path_to_your_folder>/volume.vtu", monitor_callback=None
   )

Upload many simulation folders in parallel
------------------------------------------

To upload a large dataset faster, run several uploads in parallel processes, with one
``SimAIClient`` per process. The gallery example :ref:`ref_multiprocess_upload` shows a complete
script that also skips the training data points already in the project.

Expected result when you upload the training data of a SimAI model
------------------------------------------------------------------

The complete script prints one line per uploaded folder, then one line per training data point
when its processing ends:

.. code-block:: text

   Uploaded case_001
   Uploaded case_002
   case_001 is ready
   case_002 is ready

Errors when you upload the training data of a SimAI model
---------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The data extraction of a training data point failed. The reason is in
       ``training_data.failure_reason``.
     - Check the files of the simulation folder against :doc:`/user-guide/simai-models/prepare-training-data`,
       then upload them again.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The path passed to ``upload_folder`` isn't a folder.
     - Pass the path of a simulation folder.
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - ``projects.get`` or ``training_data.get`` found no object with this name or ID.
     - Check the name, or create the object.
   * - :class:`~ansys.simai.core.errors.ApiClientError`
     - ``remove_from_project`` was called on the reference sample, or on a project in a model build.
     - Change the reference sample, or wait for the end of the model build.

More about how to upload the training data of a SimAI model
-----------------------------------------------------------

- :doc:`/user-guide/simai-models/prepare-training-data`
- :doc:`/user-guide/simai-models/assign-subsets`
- :doc:`/user-guide/simai-models/configure-a-model`
- :ref:`ref_basic_create_project_upload_data`
- :ref:`ref_multiprocess_upload`
- :class:`~ansys.simai.core.data.training_data.TrainingData`
- :class:`~ansys.simai.core.data.training_data.TrainingDataDirectory`
- :class:`~ansys.simai.core.data.projects.ProjectDirectory`
