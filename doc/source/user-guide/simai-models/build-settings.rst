:description: How a SimAI model build works: its four steps, debug mode and production mode, build duration and iterations, and how they map to the build preset parameter of ModelConfiguration.

.. _concepts_build_settings:

Model build, build settings, and build duration
===============================================

**Applies to:** SimAI models

A model build trains a SimAI model from the training data and the model configuration of a
project. This page explains the steps of a build, the build setting, and the build duration, and
how PySimAI sets them with the ``build_preset`` parameter of
:class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`.

Steps of a model build
----------------------

A model build runs in four steps:

#. Analyzing the configuration.
#. Preprocessing the data. This step takes longer when the build has more training data points.
#. Training the model. The build duration limits this step only.
#. Deploying the model. Deployment generates the Model Evaluation Report (MER) and creates a
   workspace. This step takes longer when the test subset has more data points, because
   generating the MER takes more time.

In PySimAI, :meth:`ModelDirectory.build() <ansys.simai.core.data.models.ModelDirectory.build>`
starts a build and returns a :class:`~ansys.simai.core.data.models.Model`. Call its ``wait()``
method to wait for the end of the build. See :doc:`/user-guide/simai-models/build-a-model`.

Build settings
--------------

The build setting is the type of build: debug mode or production mode.

Debug mode
   A debug build lasts less than 30 minutes and uses only four training data points. Use it to
   check that a model works before you start a longer production build. Don't use a model built
   in debug mode for production purposes.

Production mode
   A production build gives an accurate SimAI model for predictions. Its training step lasts up
   to the build duration that you choose.

Build duration and iterations
-----------------------------

The build duration is the maximum duration of the training step of a production build. It
doesn't include the other steps of the build.

During training, the model runs iterations. Each iteration processes one training data point,
and the build duration sets the number of iterations:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Build duration
     - Iterations
     - ``build_preset`` value
   * - Up to 24 hours
     - 100,000
     - ``1_day``
   * - Up to 48 hours
     - 200,000
     - ``2_days``
   * - Up to 7 days
     - 400,000
     - ``7_days``

A build shouldn't have more training data points than iterations. For example, with more than
100,000 training data points, choose a build duration of up to 48 hours or up to 7 days.

The ``build_preset`` parameter
------------------------------

PySimAI sets the build setting and the build duration with one parameter, ``build_preset``, of
:class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`:

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - ``build_preset``
     - Build setting
     - Build duration
   * - ``debug``
     - Debug mode
     - Less than 30 minutes, four training data points
   * - ``1_day``
     - Production mode
     - Up to 24 hours
   * - ``2_days``
     - Production mode
     - Up to 48 hours
   * - ``7_days``
     - Production mode
     - Up to 7 days

The ``ModelConfiguration`` constructor uses ``debug`` when you don't pass ``build_preset``.
Always pass ``build_preset`` explicitly. This example reuses the configuration of the last build
of a project, and changes it to a production build with a build duration of up to 48 hours:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")
    project = simai_client.projects.get(name="<your_project_name>")

    # last_model_configuration is None if the project has never been built
    model_configuration = project.last_model_configuration
    model_configuration.build_preset = "2_days"
    print(model_configuration.build_preset)

Any other value raises :class:`~ansys.simai.core.errors.InvalidArguments`.

More about the model build of a SimAI model
-------------------------------------------

- :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`
- :class:`~ansys.simai.core.data.models.ModelDirectory`
- :doc:`/user-guide/simai-models/configure-a-model`
- :doc:`/user-guide/simai-models/build-a-model`
- :doc:`/getting-started/overview/glossary`
