:description: Run one complete PySimAI script that creates a project, uploads training data, builds a SimAI model, uploads a geometry, and runs a prediction.

.. _getting_started_quickstart_simai_model:

Build a first SimAI model and run a prediction
==============================================

**Applies to:** SimAI models

This quickstart runs the whole workflow of a SimAI model in one script: it creates a
:class:`~ansys.simai.core.data.projects.Project`, uploads
:class:`~ansys.simai.core.data.training_data.TrainingData` from simulation folders, builds a
model with a :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`, and runs a
:class:`~ansys.simai.core.data.predictions.Prediction` on a new
:class:`~ansys.simai.core.data.geometries.Geometry`.

Prerequisites
-------------

- PySimAI is installed. See :doc:`/getting-started/install`.
- You have an account in an Ansys SimAI organization.
- A folder on your computer holds one simulation folder per simulation case. Each simulation
  folder holds a surface file (``.vtp``) and, when needed, a volume file (``.vtu``) and a scalar
  file (``.json``). For the requirements, see :doc:`/user-guide/simai-models/prepare-training-data`.
- You have a new geometry to predict on, in VTP format.
- You know the names of the variables in your data: the surface fields and the scalars.

Script to build a first SimAI model and run a prediction
--------------------------------------------------------

Replace the placeholders, then run the script. It uses the ``debug`` build preset, which builds a
model in less than 30 minutes from four training data points: use it to check your setup, not
for production.

.. code-block:: python

    import os

    import ansys.simai.core as asc
    from ansys.simai.core.data.model_configuration import (
        DomainOfAnalysis,
        ModelConfiguration,
        ModelInput,
        ModelOutput,
    )
    from ansys.simai.core.errors import ProcessingError

    TRAINING_DATA_PATH = "<path/to/your/simulation/folders>"
    GEOMETRY_PATH = "<path/to/your/new/geometry.vtp>"

    simai_client = asc.SimAIClient(organization="<your_organization>")

    # Step 1: Create a project
    project = simai_client.projects.create("<your_project_name>")

    # Step 2: Upload the training data
    # Upload one training data point for each simulation folder
    uploaded_training_data = []
    for folder_name in sorted(os.listdir(TRAINING_DATA_PATH)):
        folder_path = os.path.join(TRAINING_DATA_PATH, folder_name)
        if not os.path.isdir(folder_path):
            continue
        training_data = simai_client.training_data.create(folder_name, project=project)
        training_data.upload_folder(folder_path)
        uploaded_training_data.append(training_data)

    for training_data in uploaded_training_data:
        try:
            training_data.wait()
        except ProcessingError:
            print(f"{training_data.name} failed: {training_data.failure_reason}")

    # Step 3: Configure the model
    project.reload()
    print(project.get_variables())

    model_configuration = ModelConfiguration(
        project=project,
        build_preset="debug",
        input=ModelInput(
            surface=["<your_input_surface_variable>"],
            scalars=["<your_scalar_name>"],
        ),
        output=ModelOutput(surface=["<your_output_surface_variable>"]),
        domain_of_analysis=DomainOfAnalysis(
            length=("relative_to_min", 0.102, 1.219),
            width=("relative_to_min", 0.102, 1.219),
            height=("relative_to_min", 0.134, 1.61),
        ),
    )

    # Step 4: Build the model
    # Wait for the end of the build
    model = simai_client.models.build(model_configuration)
    try:
        while not model.wait(timeout=600):
            print("The model build is still running...")
    except ProcessingError:
        print(f"The model build failed: {model.failure_reason}")
        raise

    # Step 5: Upload a geometry
    # Upload the geometry to the workspace of the new model
    workspace = project.get_last_workspace()
    geometry = simai_client.geometries.upload(GEOMETRY_PATH, workspace=workspace)
    geometry.wait()

    # Step 6: Run a prediction
    # Run a prediction and download its surface results
    prediction = geometry.run_prediction(scalars={"<your_scalar_name>": 10.0})
    prediction.wait()
    print(f"Confidence score: {prediction.confidence_score}")
    prediction.post.surface_vtp().data.download("<path/to/prediction_result.vtp>")

The following sections explain each step of the script, with the matching part of the code.

Create a project
----------------

A project holds the training data and the model configuration of a SimAI model.
:meth:`ProjectDirectory.create() <ansys.simai.core.data.projects.ProjectDirectory.create>`
creates a project in your organization and returns a
:class:`~ansys.simai.core.data.projects.Project`. To reuse an existing project, call
``simai_client.projects.get(name="<your_project_name>")`` instead.

.. code-block:: python

    project = simai_client.projects.create("<your_project_name>")

Upload the training data
------------------------

Each simulation folder becomes one training data point.
:meth:`TrainingDataDirectory.create() <ansys.simai.core.data.training_data.TrainingDataDirectory.create>`
creates an empty :class:`~ansys.simai.core.data.training_data.TrainingData` in the project, and
:meth:`TrainingData.upload_folder() <ansys.simai.core.data.training_data.TrainingData.upload_folder>`
uploads every file of the folder. Ansys SimAI then extracts the data from the files.
:meth:`~ansys.simai.core.data.training_data.TrainingData.wait` waits for the extraction and
raises :class:`~ansys.simai.core.errors.ProcessingError` if it fails.

.. code-block:: python

    uploaded_training_data = []
    for folder_name in sorted(os.listdir(TRAINING_DATA_PATH)):
        folder_path = os.path.join(TRAINING_DATA_PATH, folder_name)
        if not os.path.isdir(folder_path):
            continue
        training_data = simai_client.training_data.create(folder_name, project=project)
        training_data.upload_folder(folder_path)
        uploaded_training_data.append(training_data)

    for training_data in uploaded_training_data:
        try:
            training_data.wait()
        except ProcessingError:
            print(f"{training_data.name} failed: {training_data.failure_reason}")

For details, see :doc:`/user-guide/simai-models/upload-training-data`.

Configure the model
-------------------

The first training data point added to the project becomes its reference sample, from which
Ansys SimAI extracts the variables. :meth:`Project.reload() <ansys.simai.core.data.projects.Project.reload>`
refreshes the local project object, and
:meth:`Project.get_variables() <ansys.simai.core.data.projects.Project.get_variables>` prints the
variables that you can use.

.. code-block:: python

    project.reload()
    print(project.get_variables())

The :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration` sets the model inputs,
the model outputs, the Domain of Analysis, and the build preset. The Domain of Analysis must
enclose all your designs: replace the example values with values that fit your geometries. For
details, see :doc:`/user-guide/simai-models/configure-a-model` and :doc:`/user-guide/simai-models/build-settings`.

.. code-block:: python

    model_configuration = ModelConfiguration(
        project=project,
        build_preset="debug",
        input=ModelInput(
            surface=["<your_input_surface_variable>"],
            scalars=["<your_scalar_name>"],
        ),
        output=ModelOutput(surface=["<your_output_surface_variable>"]),
        domain_of_analysis=DomainOfAnalysis(
            length=("relative_to_min", 0.102, 1.219),
            width=("relative_to_min", 0.102, 1.219),
            height=("relative_to_min", 0.134, 1.61),
        ),
    )

Build the model
---------------

:meth:`ModelDirectory.build() <ansys.simai.core.data.models.ModelDirectory.build>` starts the
model build and returns a :class:`~ansys.simai.core.data.models.Model`. A debug build lasts less
than 30 minutes; a production build can last several days.
:meth:`Model.wait(timeout=600) <ansys.simai.core.data.models.Model.wait>` returns ``False`` every
10 minutes while the build runs, and raises
:class:`~ansys.simai.core.errors.ProcessingError` if the build fails.

.. code-block:: python

    model = simai_client.models.build(model_configuration)
    try:
        while not model.wait(timeout=600):
            print("The model build is still running...")
    except ProcessingError:
        print(f"The model build failed: {model.failure_reason}")
        raise

For details, see :doc:`/user-guide/simai-models/build-a-model`.

Upload a geometry
-----------------

At the end of a successful build, Ansys SimAI creates a workspace for the new model.
:meth:`Project.get_last_workspace() <ansys.simai.core.data.projects.Project.get_last_workspace>`
returns it, and
:meth:`GeometryDirectory.upload() <ansys.simai.core.data.geometries.GeometryDirectory.upload>`
uploads the geometry to this workspace.

.. code-block:: python

    workspace = project.get_last_workspace()
    geometry = simai_client.geometries.upload(GEOMETRY_PATH, workspace=workspace)
    geometry.wait()

Run a prediction
----------------

:meth:`Geometry.run_prediction() <ansys.simai.core.data.geometries.Geometry.run_prediction>` runs
the SimAI model on the geometry with the scalars you pass, and returns a
:class:`~ansys.simai.core.data.predictions.Prediction` immediately. Use the names of the scalars
of your model as keys. The ``surface_vtp()`` postprocessing exports the predicted surface fields
in VTP format.

.. code-block:: python

    prediction = geometry.run_prediction(scalars={"<your_scalar_name>": 10.0})
    prediction.wait()
    print(f"Confidence score: {prediction.confidence_score}")
    prediction.post.surface_vtp().data.download("<path/to/prediction_result.vtp>")

For details, see :doc:`/user-guide/simai-models/run-predictions` and
:doc:`/user-guide/simai-models/postprocess-predictions`.

Expected result when you build a first SimAI model and run a prediction
-----------------------------------------------------------------------

The script prints the variables of the reference sample, a progress message every 10 minutes
during the build, and the confidence score of the prediction (``high`` or ``low``). It saves the
predicted surface fields in a VTP file at the path you set.

Errors when you build a first SimAI model and run a prediction
--------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The extraction of a training data point, the model build, or the prediction failed.
     - Read ``failure_reason`` on the object.
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - A variable of the model configuration doesn't exist in the reference sample.
     - Use the names printed by ``project.get_variables()``.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The project isn't ready for a build, for example because it has too few training data
       points. The message gives the reason.
     - Fix the reason, then build again.

For all the exceptions, see :doc:`/user-guide/common-tasks/handle-errors`.

More about how to build a first SimAI model and run a prediction
----------------------------------------------------------------

- :ref:`ref_basic_create_project_upload_data`
- :ref:`ref_basic_build_model`
- :ref:`ref_basic_run_predictions`
- :doc:`/getting-started/overview/object-model`
- :doc:`/user-guide/common-tasks/work-asynchronously`
