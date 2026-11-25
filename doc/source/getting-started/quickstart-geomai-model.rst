:description: Run one complete PySimAI script that creates a project, uploads geometries as training data, builds a GeomAI model, and generates new geometries.

.. _getting_started_quickstart_geomai_model:

Build a first GeomAI model and generate geometries
==================================================

**Applies to:** GeomAI models

This quickstart runs the whole workflow of a GeomAI model in one script: it creates a
:class:`~ansys.simai.core.data.geomai.projects.GeomAIProject`, uploads geometry files as
:class:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingData`, builds a model with a
:class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration`, and generates new
geometries with :class:`~ansys.simai.core.data.geomai.predictions.GeomAIPrediction` objects.

Prerequisites
-------------

- PySimAI is installed. See :doc:`/getting-started/install`.
- You have an account in an :term:`organization` in Ansys SimAI.
- A folder on your computer holds your geometries, one file per geometry, in VTP (``.vtp``) or
  STL (``.stl``) format. For the requirements, see :doc:`/user-guide/geomai-models/prepare-training-data`.

Script to build a first GeomAI model and generate geometries
------------------------------------------------------------

Replace the placeholders, then run the script. It uses the ``debug`` build preset, which trains
on four training data points for one epoch: use it to check your setup, not for production.

.. code-block:: python

    import os
    import random

    import ansys.simai.core as asc
    from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration
    from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration
    from ansys.simai.core.errors import ProcessingError

    GEOMETRIES_PATH = "<path/to/your/geometries>"
    OUTPUT_DIR = "<path/to/output/folder>"
    NUM_GEOMETRIES = 5

    simai_client = asc.SimAIClient(organization="<your_organization>")
    geomai_client = simai_client.geomai

    # Step 1: Create a project
    project = geomai_client.projects.create("<your_project_name>")

    # Step 2: Upload the training data
    # Upload one training data point for each geometry file
    uploaded_training_data = []
    for file_name in sorted(os.listdir(GEOMETRIES_PATH)):
        if not file_name.lower().endswith((".vtp", ".stl")):
            continue
        training_data = geomai_client.training_data.create_from_file(
            file=os.path.join(GEOMETRIES_PATH, file_name), project=project
        )
        uploaded_training_data.append(training_data)

    for training_data in uploaded_training_data:
        try:
            training_data.wait()
        except ProcessingError:
            print(f"{training_data.name} failed: {training_data.failure_reason}")

    # Step 3: Build the model
    # Configure and build the model, then wait for the end of the build
    configuration = GeomAIModelConfiguration(build_preset="debug")
    model = geomai_client.models.build(project, configuration)
    try:
        while not model.wait(timeout=60):
            print("The model build is still running...")
    except ProcessingError:
        print(f"The model build failed: {model.failure_reason}")
        raise

    # Step 4: Get the workspace of the model
    workspace = project.get_last_workspace()
    nb_latent_params = workspace.model_manifest.nb_latent_parameters

    # Step 5: Generate geometries
    # Generate geometries from random latent parameters
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    predictions = []
    for _ in range(NUM_GEOMETRIES):
        prediction_configuration = GeomAIPredictionConfiguration(
            latent_params=[random.gauss(0, 1) for _ in range(nb_latent_params)]
        )
        predictions.append(geomai_client.predictions.run(prediction_configuration, workspace))

    # Step 6: Download the generated geometries
    for index, prediction in enumerate(predictions):
        try:
            prediction.download(os.path.join(OUTPUT_DIR, f"generated_{index + 1:02d}.vtp"))
        except ProcessingError:
            print(f"Generation {index + 1} failed: {prediction.failure_reason}")

The following sections explain each step of the script, with the matching part of the code.

Create a project
----------------

GeomAI models have their own projects, accessed through ``simai_client.geomai``.
:meth:`GeomAIProjectDirectory.create() <ansys.simai.core.data.geomai.projects.GeomAIProjectDirectory.create>`
creates a project and returns a
:class:`~ansys.simai.core.data.geomai.projects.GeomAIProject`. To reuse an existing project,
call ``geomai_client.projects.get(name="<your_project_name>")`` instead.

.. code-block:: python

    project = geomai_client.projects.create("<your_project_name>")

Upload the training data
------------------------

Each geometry file becomes one training data point.
:meth:`GeomAITrainingDataDirectory.create_from_file() <ansys.simai.core.data.geomai.training_data.GeomAITrainingDataDirectory.create_from_file>`
creates the training data point in the project, uploads the file, and starts the data
extraction. :meth:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingData.wait` waits for
the extraction and raises :class:`~ansys.simai.core.errors.ProcessingError` if it fails.

.. code-block:: python

    uploaded_training_data = []
    for file_name in sorted(os.listdir(GEOMETRIES_PATH)):
        if not file_name.lower().endswith((".vtp", ".stl")):
            continue
        training_data = geomai_client.training_data.create_from_file(
            file=os.path.join(GEOMETRIES_PATH, file_name), project=project
        )
        uploaded_training_data.append(training_data)

    for training_data in uploaded_training_data:
        try:
            training_data.wait()
        except ProcessingError:
            print(f"{training_data.name} failed: {training_data.failure_reason}")

For details, see :doc:`/user-guide/geomai-models/upload-training-data`.

Build the model
---------------

:class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration` takes either a
``build_preset`` (``debug``, ``short``, ``default``, or ``long``) or a number of epochs
(``nb_epochs``), not both.
:meth:`GeomAIModelDirectory.build() <ansys.simai.core.data.geomai.models.GeomAIModelDirectory.build>`
starts the model build and returns a :class:`~ansys.simai.core.data.geomai.models.GeomAIModel`.
:meth:`GeomAIModel.wait(timeout=60) <ansys.simai.core.data.geomai.models.GeomAIModel.wait>`
returns ``False`` every minute while the build runs, and raises
:class:`~ansys.simai.core.errors.ProcessingError` if the build fails.

.. code-block:: python

    configuration = GeomAIModelConfiguration(build_preset="debug")
    model = geomai_client.models.build(project, configuration)
    try:
        while not model.wait(timeout=60):
            print("The model build is still running...")
    except ProcessingError:
        print(f"The model build failed: {model.failure_reason}")
        raise

For details, see :doc:`/user-guide/geomai-models/configure-a-model` and :doc:`/user-guide/geomai-models/build-a-model`.

Get the workspace of the model
------------------------------

At the end of a successful build, Ansys SimAI creates a workspace for the new GeomAI model.
:meth:`GeomAIProject.get_last_workspace() <ansys.simai.core.data.geomai.projects.GeomAIProject.get_last_workspace>`
returns it. The ``nb_latent_parameters`` property of its
:attr:`~ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace.model_manifest` gives the number
of :term:`latent parameters <latent parameter>` of the model.

.. code-block:: python

    workspace = project.get_last_workspace()
    nb_latent_params = workspace.model_manifest.nb_latent_parameters

Generate geometries
-------------------

A GeomAI model generates a geometry from a vector of latent parameters.
:meth:`GeomAIPredictionDirectory.run() <ansys.simai.core.data.geomai.predictions.GeomAIPredictionDirectory.run>`
starts one generation for each
:class:`~ansys.simai.core.data.geomai.predictions.GeomAIPredictionConfiguration` and returns a
:class:`~ansys.simai.core.data.geomai.predictions.GeomAIPrediction` immediately. This script
draws the latent parameters at random from a standard normal distribution.

.. code-block:: python

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    predictions = []
    for _ in range(NUM_GEOMETRIES):
        prediction_configuration = GeomAIPredictionConfiguration(
            latent_params=[random.gauss(0, 1) for _ in range(nb_latent_params)]
        )
        predictions.append(geomai_client.predictions.run(prediction_configuration, workspace))

For other ways to choose latent parameters, see :doc:`/user-guide/geomai-models/generate-geometries` and
:doc:`/user-guide/geomai-models/interpolate-and-project`.

Download the generated geometries
---------------------------------

:meth:`GeomAIPrediction.download() <ansys.simai.core.data.geomai.predictions.GeomAIPrediction.download>`
waits for the generation to finish, then saves the geometry in VTP format. It raises
:class:`~ansys.simai.core.errors.ProcessingError` if the generation failed.

.. code-block:: python

    for index, prediction in enumerate(predictions):
        try:
            prediction.download(os.path.join(OUTPUT_DIR, f"generated_{index + 1:02d}.vtp"))
        except ProcessingError:
            print(f"Generation {index + 1} failed: {prediction.failure_reason}")

Expected result when you build a first GeomAI model and generate geometries
---------------------------------------------------------------------------

The script prints a progress message every minute during the build, then saves five generated
geometries, ``generated_01.vtp`` to ``generated_05.vtp``, in the output folder.

Errors when you build a first GeomAI model and generate geometries
------------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The extraction of a training data point, the model build, or a generation failed.
     - Read ``failure_reason`` on the object.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The model configuration or the prediction configuration is invalid, for example with
       both ``build_preset`` and ``nb_epochs``.
     - Fix the configuration as the message describes.

For all the exceptions, see :doc:`/user-guide/common-tasks/handle-errors`.

More about how to build a first GeomAI model and generate geometries
--------------------------------------------------------------------

- :ref:`ref_create_project_upload_data`
- :ref:`ref_build_model`
- :ref:`ref_generate_random_geometries`
- :doc:`/getting-started/overview/object-model`
- :doc:`/user-guide/common-tasks/work-asynchronously`
