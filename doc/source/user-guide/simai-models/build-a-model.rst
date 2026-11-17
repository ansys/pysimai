:description: Start the model build of a SimAI model with PySimAI, follow it with a timeout, cancel it, and choose between debug mode and production mode.

.. _building_a_model:

.. _simai_models_build_a_model:

Build a SimAI model
===================

**Applies to:** SimAI models

Start a model build from a
:class:`~ansys.simai.core.data.model_configuration.ModelConfiguration` object with
:meth:`ModelDirectory.build() <ansys.simai.core.data.models.ModelDirectory.build>`, follow it
with :meth:`Model.wait() <ansys.simai.core.data.models.Model.wait>`, and cancel it with
:meth:`Project.cancel_build() <ansys.simai.core.data.projects.Project.cancel_build>`.

.. note::

   Building a model with PySimAI is still experimental and subject to API changes.

Script to build a SimAI model
-----------------------------

This script checks that the project can be trained, starts a debug build, and waits up to one
hour for the end of the build. Replace the variable names and the Domain of Analysis values with
the ones of your training data.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.model_configuration import (
       DomainOfAnalysis,
       ModelConfiguration,
       ModelInput,
       ModelOutput,
   )
   from ansys.simai.core.errors import ProcessingError

   simai_client = asc.SimAIClient(organization="<your_organization>")
   project = simai_client.projects.get(name="<your_project_name>")

   model_configuration = ModelConfiguration(
       project=project,
       # Choose debug mode or production mode
       build_preset="debug",
       input=ModelInput(surface=["<your_surface_input_variable>"], scalars=["<your_scalar_name>"]),
       output=ModelOutput(surface=["<your_surface_output_variable>"]),
       global_coefficients=[("max(<your_surface_output_variable>)", "<your_global_coefficient_name>")],
       domain_of_analysis=DomainOfAnalysis(
           length=("relative_to_min", 0.102, 1.219),
           width=("relative_to_min", 0.102, 1.219),
           height=("relative_to_min", 0.134, 1.61),
       ),
   )

   # Check that the project can be trained
   trainable = project.is_trainable()
   if not trainable:
       raise SystemExit(f"The project can't be trained: {trainable.reason}")

   # Start the model build
   model = simai_client.models.build(model_configuration)
   print(f"Model build started: {model.id}")

   # Follow the model build
   try:
       finished = model.wait(timeout=3600)
       if finished:
           print("Model build finished")
       else:
           print("Model build still running after one hour")
   except ProcessingError:
       print(f"Model build failed: {model.failure_reason}")

For each part of the model configuration, see :doc:`/user-guide/simai-models/configure-a-model`.

Check that the project can be trained
-------------------------------------

Before a model build, call
:meth:`Project.is_trainable() <ansys.simai.core.data.projects.Project.is_trainable>`. It returns
an :class:`~ansys.simai.core.data.projects.IsTrainableInfo` object that you can use as a Boolean.
When the project can't be trained, its ``reason`` attribute explains why:

.. code-block:: python

   trainable = project.is_trainable()
   print(trainable)

.. code-block:: text

   <is_trainable: False, reason(s): Not enough data to train a model: we need at least 3 data points to train a model.>

``simai_client.models.build()`` makes the same check and raises
:class:`~ansys.simai.core.errors.InvalidArguments` with this reason when the project can't be
trained.

Start the model build
---------------------

Pass the model configuration to ``simai_client.models.build()``. The method returns a
:class:`~ansys.simai.core.data.models.Model` object right away, while the build runs on Ansys
SimAI:

.. code-block:: python

   model = simai_client.models.build(model_configuration)

Three optional parameters leave problem training data points out of the build instead of
failing it. They're all ``False`` by default:

- ``dismiss_data_with_fields_discrepancies``: leaves out data points with missing variables.
- ``dismiss_data_with_volume_overflow``: leaves out data points outside the Domain of Analysis.
- ``dismiss_data_input_with_nan``: leaves out data points whose model inputs contain NaN values.

To build again with the configuration of the last build, pass
``project.last_model_configuration``. For an example, see :ref:`ref_model_recomputation`.

Follow the model build
----------------------

A model build runs in four steps: analyzing the configuration, preprocessing the data, training
the model, and deploying the model. Deployment generates the Model Evaluation Report and creates
the workspace of the SimAI model.

Call ``model.wait()`` to block until the build ends. Use the ``timeout`` parameter, in seconds,
because a production build can last days:

- ``wait()`` returns ``True`` when the build has finished.
- ``wait()`` returns ``False`` when the timeout is reached and the build is still running.
- ``wait()`` raises :class:`~ansys.simai.core.errors.ProcessingError` when the build fails. The
  reason is in ``model.failure_reason``.

You can also check ``model.is_pending``, ``model.is_ready``, and ``model.has_failed`` without
blocking. For more ways to wait, see :doc:`/user-guide/common-tasks/work-asynchronously`.

Choose debug mode or production mode
------------------------------------

The ``build_preset`` parameter of the model configuration sets the build setting:

- Debug mode (``"debug"``) lasts less than 30 minutes and uses only four training data points. It
  checks that the model configuration works before a longer production build. Don't use a SimAI
  model built in debug mode for production purposes.
- Production mode gives an accurate SimAI model for predictions. Its build duration is the maximum
  duration of the training step: ``"1_day"`` (up to 24 hours, 100,000 iterations), ``"2_days"``
  (up to 48 hours, 200,000 iterations, the default build duration), or ``"7_days"`` (up to 7 days,
  400,000 iterations).

The build duration doesn't include the other steps. Preprocessing takes longer with more training
data points, and deployment takes longer with more data points in the test subset, because the
Model Evaluation Report takes more time to generate.

Cancel a model build
--------------------

To stop a model build in progress, call ``cancel_build()`` on the project, or on the projects
directory with the project object or ID:

.. code-block:: python

   project.cancel_build()
   # Equivalent:
   simai_client.projects.cancel_build(project)

Both methods raise :class:`~ansys.simai.core.errors.ProcessingError` with the message
``No build pending for this project.`` when the project has no build in progress.

Expected result when you build a SimAI model
--------------------------------------------

The complete script prints the ID of the model, then the end of the build:

.. code-block:: text

   Model build started: <model_id>
   Model build finished

When the build finishes, the workspace of the SimAI model is ready for predictions. Get it with
:meth:`Project.get_last_workspace() <ansys.simai.core.data.projects.Project.get_last_workspace>`.

Errors when you build a SimAI model
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The project can't be trained, the model configuration has no project, or a Domain of
       Analysis axis is missing.
     - Read ``project.is_trainable().reason`` and fix the project or the configuration.
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - ``wait()``: the model build failed. ``cancel_build()``: no build is in progress.
     - Read ``model.failure_reason``, fix the configuration or the training data, and build again.

More about how to build a SimAI model
-------------------------------------

- :doc:`/user-guide/simai-models/configure-a-model`
- :doc:`/user-guide/simai-models/assign-subsets`
- :doc:`/user-guide/simai-models/evaluate-a-model`
- :ref:`ref_basic_build_model`
- :ref:`ref_model_recomputation`
- :class:`~ansys.simai.core.data.models.ModelDirectory`
- :class:`~ansys.simai.core.data.models.Model`
