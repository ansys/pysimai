:description: Configure a GeomAI model build with GeomAIModelConfiguration: choose a build preset or a number of epochs, and the number of latent parameters.

.. _model_setup_geomai:

Configure a GeomAI model
========================

**Applies to:** GeomAI models

To configure a GeomAI model, create a
:class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration` object. Set exactly one of
``build_preset`` or ``nb_epochs`` to control the training duration, and optionally set
``nb_latent_param`` to change the :term:`latent dimension`.

Choose a configuration for your use case
----------------------------------------

Decide what you want to achieve before you configure a GeomAI model:

- Design exploration: you want to generate many diverse geometries. Provide diverse training data
  and favor interpolation quality with a moderate build preset.
- Optimization: you want to use a GeomAI model inside an optimization loop, for example with
  Ansys optiSLang. Provide training data that covers the region of interest and favor smooth
  interpolations. For more information, see :ref:`reduced_latent_space_geomai`.
- Complex geometric features: your geometries have fine details or intricate shapes that the
  GeomAI model must reproduce faithfully. Provide enough training data to represent those
  features and use a longer build preset to favor reconstruction quality.

.. tip::
   A GeomAI model captures implicit constraints from your training data. For more information,
   see :ref:`data_preparation_geomai`.

Balance reconstruction and interpolation in a GeomAI model
----------------------------------------------------------

The training of a GeomAI model balances two objectives:

- Reconstruction: how well the GeomAI model reproduces the training geometries.
- Interpolation: how well the GeomAI model generates meaningful new geometries between known
  ones.

A GeomAI model that reconstructs the training data perfectly may overfit and produce poor
interpolations. A GeomAI model tuned for smooth interpolation may not reproduce every detail of
the original geometries. The build preset that you choose sets where the GeomAI model falls
between these two objectives.

.. _geomai_models_build_preset:

Set the build preset of a GeomAI model
--------------------------------------

The ``build_preset`` parameter sets the training duration of the GeomAI model. The training
duration grows with the number of geometries in the training data:

- ``debug``: 4 minutes + 15 seconds per geometry.
- ``short``: 45 minutes + 15 seconds per geometry.
- ``default``: 3 hours + 15 seconds per geometry.
- ``long``: 15 hours + 15 seconds per geometry.

These values apply to GeomAI models only. SimAI models use other ``build_preset`` values:
``debug``, ``1_day``, ``2_days``, and ``7_days``. For more information, see
:doc:`/user-guide/simai-models/build-settings`.

Use ``debug`` to test and debug your pipeline. According to the API reference, a ``debug`` build
uses a subset of four training data points and one epoch, which reduces the runtime while you
check the processing workflow. Don't use a ``debug`` build for production.

.. TODO: confirm what the debug build preset does for GeomAI models with the product team.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration

   simai_client = asc.SimAIClient(organization="<your_organization>")
   geomai_client = simai_client.geomai

   project = geomai_client.projects.get(name="<your_project_name>")

   # Use a build preset. To set the number of epochs instead, use nb_epochs=100.
   configuration = GeomAIModelConfiguration(build_preset="default")
   print(configuration)

   model = geomai_client.models.build(project, configuration)
   print(f"Started build for model {model.id}")

To follow the build after it starts, see :doc:`/user-guide/geomai-models/build-a-model`.

Choose the build preset of a GeomAI model
-----------------------------------------

The right build preset depends on your training data and your goal:

- Small sets (2 to 10 geometries) focused on interpolation: use a lower build preset
  (``short``). Longer training on few geometries tends to overfit, which degrades interpolation
  quality.
- Moderate sets of simple geometries: use ``short`` or ``default``. Simple geometries, with a low
  polygon count, are easier to learn, and longer training may bring no benefit.
- Large sets or complex geometries: use ``default`` or ``long``. Complex geometries, with a high
  polygon count, need more training so that the GeomAI model learns the geometric structure
  instead of approximating it.

.. note::
   Some training data is easy to reconstruct, and even a ``short`` build preset gives good
   reconstruction. Training data of similar size but higher geometric complexity may need a longer
   build preset so that the GeomAI model captures the full geometry.

.. tip::
   If generated geometries are too smooth or lack detail, try a longer build preset. If you see
   void volumes or garbled shapes during interpolation, try a shorter one.

Set the number of epochs of a GeomAI model
------------------------------------------

The ``nb_epochs`` parameter sets the number of epochs, that is, the number of times the GeomAI
model processes the whole training data during training. The minimum is 1.

.. code-block:: python

   configuration = GeomAIModelConfiguration(nb_epochs=100)

``nb_epochs`` and ``build_preset`` are mutually exclusive: set exactly one of them. If you set
both or neither, ``GeomAIModelConfiguration`` raises
:class:`~ansys.simai.core.errors.InvalidArguments`.

``nb_epochs`` is for experienced users. It allows finer tuning but requires prior knowledge of how
the GeomAI model behaves on your training data. Start with ``build_preset`` and switch to
``nb_epochs`` only when you need more tuning:

- Poor reconstruction quality: increase the number of epochs to give the GeomAI model more
  training.
- Void or garbled geometries during interpolation: decrease the number of epochs. The GeomAI model
  may overfit the training data, which degrades interpolation quality.

.. note::
   Training has a maximum runtime of 72 hours. If the requested number of epochs leads to a longer
   training, the system may reduce the number of epochs, so the GeomAI model can complete fewer
   epochs than requested. To compare the two values, read ``requested_nb_epochs`` and ``nb_epochs``
   in the :class:`~ansys.simai.core.data.geomai.workspaces.GeomAIModelManifest` of the workspace.
   For more information, see :doc:`/user-guide/geomai-models/evaluate-a-model`.

Set the number of latent parameters of a GeomAI model
-----------------------------------------------------

The ``nb_latent_param`` parameter defines the :term:`latent dimension`, that is, the length of
the :term:`latent vector` that represents each geometry in the :term:`latent space`. Valid values
are between 2 and 1024. The default value is 512.

Keep the default value of 512 unless your use case has specific constraints. A higher value lets
the GeomAI model encode more complex variations and fine geometric details, but raises the risk of
overfitting, and the GeomAI model may fail to generate new geometries correctly. A value that is
too low can make geometries too coarse and degrade reconstruction.

.. code-block:: python

   configuration = GeomAIModelConfiguration(build_preset="default", nb_latent_param=256)

Reuse the last GeomAI model configuration of a project
------------------------------------------------------

The
:attr:`last_model_configuration<ansys.simai.core.data.geomai.projects.GeomAIProject.last_model_configuration>`
property of a project returns the last configuration used to build a GeomAI model in that project,
or ``None`` if the project has no model build yet. Pass it to ``geomai_client.models.build()`` to
build again with the same configuration, in the same project or in another one:

.. code-block:: python

   project_a = geomai_client.projects.get(name="<your_project_name>")
   project_b = geomai_client.projects.get(name="<your_other_project_name>")

   configuration = project_a.last_model_configuration
   new_model = geomai_client.models.build(project_b, configuration)

Expected result when you configure a GeomAI model
-------------------------------------------------

The code in "Set the build preset of a GeomAI model" prints the configuration, for example
``nb_latent_param=512 build_preset='default' nb_epochs=None``, then the ID of the GeomAI model
that starts to build.

Errors when you configure a GeomAI model
----------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - Both ``build_preset`` and ``nb_epochs`` are set, or neither is set. Or a value is out of
       range: ``nb_latent_param`` outside 2 to 1024, ``nb_epochs`` lower than 1, or an unknown
       build preset.
     - Set exactly one of ``build_preset`` and ``nb_epochs``, with a valid value.
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No project has the requested name.
     - Check the project name, or create the project. See
       :doc:`/user-guide/geomai-models/upload-training-data`.

More about how to configure a GeomAI model
------------------------------------------

- :class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration`
- :class:`~ansys.simai.core.data.geomai.models.GeomAIModelDirectory`
- :doc:`/user-guide/geomai-models/build-a-model`
- :doc:`/user-guide/geomai-models/evaluate-a-model`
- :ref:`ref_build_model`
