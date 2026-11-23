:description: Glossary of Ansys SimAI and PySimAI terms, split into concepts common to both types of AI model, SimAI models only, and GeomAI models only, with the matching PySimAI classes.

.. _concepts_glossary:

Glossary
========

**Applies to:** SimAI models and GeomAI models

This glossary defines the terms of Ansys SimAI as PySimAI uses them, with the matching PySimAI
class when there is one. Other pages link to these definitions.

The terms are in three parts, because the two types of AI model don't share their data or their
vocabulary. For why, see :doc:`/getting-started/overview/architecture`.

- :ref:`glossary_common_concepts`: terms that apply to SimAI models and GeomAI models. When the
  meaning differs between the two types, the definition says how.
- :ref:`glossary_simai_models`: terms that apply to SimAI models only.
- :ref:`glossary_geomai_models`: terms that apply to GeomAI models only.

.. _glossary_common_concepts:

Concepts common to both types of AI model
-----------------------------------------

.. glossary::
   :sorted:

   AI model
      A model that Ansys SimAI trains on the training data of a project. There are two types:
      :term:`SimAI model` and :term:`GeomAI model`. Each type has its own data, which the other
      type can't use.

   Ansys Help
      The Ansys documentation portal, https://ansyshelp.ansys.com. It hosts the Ansys SimAI
      User's Guide, which documents the web app.

   Ansys SimAI
      The platform for building and using AI models in industrial design. It offers two
      types of AI model: SimAI models and GeomAI models. You use it from the web app at
      https://simai.ansys.com or from Python with :term:`PySimAI`.

   Design of Experiments
   DOE
      The planned set of simulation cases that covers a :term:`design space`.

   design space
      The scope and limits of the study that the AI model must cover. It determines which
      training data to select.

   geometry
      The 3D surface mesh of a design. Its role depends on the type of AI model. For a SimAI
      model, it's the design you run a prediction on: see :term:`geometry of a SimAI model`.
      For a GeomAI model, geometries are both the training data and the result of a
      generation: see :term:`geometry of a GeomAI model`.

   model build
      The process that trains an AI model from the training data and the model configuration of
      a project. Each successful model build creates a :term:`workspace`. For a SimAI model, it
      runs in four steps: analyzing the configuration, preprocessing the data, training the
      model, and deploying the model. Deployment produces the :term:`Model Evaluation Report`
      and creates the workspace. PySimAI classes:
      :class:`~ansys.simai.core.data.models.Model` for SimAI models,
      :class:`~ansys.simai.core.data.geomai.models.GeomAIModel` for GeomAI models.

   model configuration
      The full set of settings used for the next model build in a project. For a SimAI model, it
      holds the reference sample, variables, global coefficients, Domain of Analysis, build
      setting, and build duration. For a GeomAI model, it holds the number of latent parameters
      and either a :term:`build preset of a GeomAI model` or a number of epochs. PySimAI
      classes: :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration` for SimAI
      models, :class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration` for GeomAI
      models.

   Model Evaluation Report
   MER
      The report produced with each trained AI model. It has plots and metrics to assess the
      accuracy of the model. Its content depends on the type of model. In PySimAI, download it
      with ``workspace.download_model_evaluation_report()``: as a PDF file for a SimAI model,
      and as a ZIP file for a GeomAI model.

   organization
      The account that groups the users of one company in Ansys SimAI. Users are added to an
      organization and receive an email invitation to sign in to Ansys SimAI. All the training data
      uploaded in an organization is shared between its users, and data can't be shared between
      organizations. SimAI models and GeomAI models belong to the same organization. Its name
      appears in the web app URL, for example ``https://simai.ansys.com/<organization-name>``, and is the
      ``organization`` parameter of :class:`~ansys.simai.core.client.SimAIClient`.

   prediction
      The result of running a trained AI model in a workspace. For a SimAI model, it's the
      physical fields predicted on one geometry with one set of scalars. For a GeomAI model,
      it's a new geometry generated from a set of :term:`latent parameters`. PySimAI classes:
      :class:`~ansys.simai.core.data.predictions.Prediction` for SimAI models,
      :class:`~ansys.simai.core.data.geomai.predictions.GeomAIPrediction` for GeomAI models.

   project
      The place where you gather training data and a model configuration to build AI models.
      Each successful model build in a project creates a workspace. A project is either a
      project of SimAI models or a project of GeomAI models, and each client lists only the
      projects of its type. PySimAI classes:
      :class:`~ansys.simai.core.data.projects.Project` for SimAI models,
      :class:`~ansys.simai.core.data.geomai.projects.GeomAIProject` for GeomAI models.

   PyAnsys
      The ecosystem of Ansys Python libraries, of which PySimAI is one. See
      https://docs.pyansys.com.

   PySimAI
      The Python SDK for Ansys SimAI. It gives access to almost all the features of the web app
      from Python apps and scripts. Its package is ``ansys-simai-core``. It has one client for
      each type of AI model: :class:`~ansys.simai.core.client.SimAIClient` for SimAI models, and
      :class:`~ansys.simai.core.data.geomai.client.GeomAIClient`, obtained with
      ``simai_client.geomai``, for GeomAI models.

   training data
      The data uploaded to Ansys SimAI to train AI models: simulation results for a SimAI model,
      geometries for a GeomAI model. Training data uploaded for one type of AI model can't train
      the other type. "Training data" is a mass noun: one training data point, several training
      data points.

   training data point
      One case uploaded as training data. For a SimAI model, it's one simulation case: it always
      has a surface file, and can also have a volume file and a scalar file. For a GeomAI model,
      it's one geometry file. PySimAI classes:
      :class:`~ansys.simai.core.data.training_data.TrainingData` for SimAI models and
      :class:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingData` for GeomAI models.
      Each file of a training data point is a
      :class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart` or a
      :class:`~ansys.simai.core.data.geomai.training_data_parts.GeomAITrainingDataPart`.

   workspace
      The place where you use a built AI model. Ansys SimAI creates one workspace when it
      deploys the model at the end of a successful model build. In the workspace of a SimAI
      model, you run predictions on geometries and generate postprocessings. In the workspace
      of a GeomAI model, you generate geometries and run projections. PySimAI classes:
      :class:`~ansys.simai.core.data.workspaces.Workspace` for SimAI models,
      :class:`~ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace` for GeomAI models.

.. _glossary_simai_models:

SimAI models
------------

.. glossary::
   :sorted:

   build duration
      The maximum duration of the training step of a :term:`model build` in
      :term:`production mode`: up to 24 hours (100,000 iterations), up to 48 hours (200,000
      iterations), or up to 7 days (400,000 iterations). It doesn't include the other steps of
      the build. A build shouldn't have more training data points than iterations. In PySimAI,
      the ``build_preset`` parameter of
      :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration` sets it. See
      :doc:`/user-guide/simai-models/build-settings`.

   build setting
      The type of build of a SimAI model: :term:`debug mode` or :term:`production mode`. PySimAI
      sets the build setting and the :term:`build duration` with one parameter,
      ``build_preset``: ``debug``, ``1_day``, ``2_days``, or ``7_days``. For GeomAI models, see
      :term:`build preset of a GeomAI model`.

   confidence score
      A value from 0 to 1 that shows how familiar a :term:`prediction` is to the SimAI model,
      compared with its training data. It's labeled high (0.66 or more) or low. It isn't a
      measure of accuracy or error. In PySimAI, read it with
      :attr:`Prediction.confidence_score <ansys.simai.core.data.predictions.Prediction.confidence_score>`
      (``high`` or ``low``) and
      :attr:`Prediction.raw_confidence_score <ansys.simai.core.data.predictions.Prediction.raw_confidence_score>`
      (the value).

   debug mode
      A :term:`build setting` of SimAI models. A debug build lasts less than 30 minutes and uses
      only four training data points. It checks that a model works before you start a longer
      production build. Don't use a model built in debug mode for production purposes. In
      PySimAI, pass ``build_preset="debug"``.

   Domain of Analysis
   DoA
      The box-shaped volume, defined once per SimAI model, that must enclose all designs: the
      training data and the geometries you predict on. A smaller domain gives better accuracy.
      PySimAI class:
      :class:`~ansys.simai.core.data.model_configuration.DomainOfAnalysis`.

   geometry of a SimAI model
      The 3D surface mesh of a design on which you run a :term:`prediction`. You upload it to
      the workspace of a SimAI model, in VTP format (recommended), STL format, or CGNS format.
      To upload a geometry made of several STL files, put them in one ZIP archive. In PySimAI,
      upload it with
      :meth:`GeometryDirectory.upload() <ansys.simai.core.data.geometries.GeometryDirectory.upload>`,
      which accepts the ``vtp``, ``stl``, ``zip``, and ``cgns`` file extensions. PySimAI class:
      :class:`~ansys.simai.core.data.geometries.Geometry`.

   global coefficient
      A single value computed for a whole design after a SimAI model prediction, such as drag
      or lift, from a formula that you define in the :term:`model configuration`. PySimAI
      class:
      :class:`~ansys.simai.core.data.model_configuration.GlobalCoefficientDefinition`.

   iteration
      One step of the training of a SimAI model, in which the model processes one training data
      point. A production build runs 100,000, 200,000, or 400,000 iterations, depending on its
      :term:`build duration`. SimAI models use iterations, not epochs.

   model input
      A :term:`variable` that a SimAI model uses to predict its outputs. It must exist in every
      training data point of the project and in every geometry you predict on. PySimAI class:
      :class:`~ansys.simai.core.data.model_configuration.ModelInput`.

   model output
      A :term:`variable` that a SimAI model learns to predict. It must exist in every training
      data point of the project. PySimAI class:
      :class:`~ansys.simai.core.data.model_configuration.ModelOutput`.

   postprocessing
      Analyzing or exporting results after they're computed. In Ansys SimAI, postprocessings
      are also the analysis tools available for a :term:`prediction` of a SimAI model, such as
      global coefficients or the export of the predicted fields. In PySimAI, run them through
      ``prediction.post``. PySimAI class:
      :class:`~ansys.simai.core.data.post_processings.PostProcessing` and its subclasses.

   postprocessing input
      A :term:`variable` that a SimAI model doesn't learn from or predict, but that you need for
      global coefficients or other postprocessings. PySimAI class:
      :class:`~ansys.simai.core.data.model_configuration.PostProcessInput`.

   production mode
      A :term:`build setting` of SimAI models. A production build lasts the build duration you
      choose (24 hours, 48 hours, or 7 days) and gives an accurate SimAI model for predictions.
      In PySimAI, pass ``build_preset="1_day"``, ``"2_days"``, or ``"7_days"``.

   reference sample
      The training data point of a project from which Ansys SimAI extracts the variables
      available to a SimAI model, and on which it tests global coefficient formulas. By default,
      it's the first data point added to the project. It has no effect on model performance. In
      PySimAI, it's the ``sample`` property of
      :class:`~ansys.simai.core.data.projects.Project`.

   scalar
      A single value with no unit that describes the operating conditions of a case, such as an
      inlet velocity or a fluid temperature. Scalars come from the :term:`scalar file` during
      training. You set them for each prediction, for example with
      ``geometry.run_prediction(scalars={"Vx": 10.5})``. A SimAI model can also output scalars.

   scalar file
      The optional JSON file (``.json``) of a training data point for a SimAI model. It lists the
      scalars of the case as name and value pairs, without units.

   SimAI model
      The type of AI model that trains on simulation data and predicts physical fields for new
      geometries in a workspace. PySimAI class:
      :class:`~ansys.simai.core.data.models.Model`.

   simulation folder
      The folder on your computer that holds the files of one simulation case before upload.
      Each file type appears at most once per folder. After upload, the folder becomes a
      :term:`training data point`. In PySimAI, upload it with
      :meth:`TrainingData.upload_folder() <ansys.simai.core.data.training_data.TrainingData.upload_folder>`.

   surface file
      The required file of a training data point for a SimAI model, in VTP format (``.vtp``). It
      describes the geometry and the surface fields. If one geometry has several surface files,
      merge them before upload.

   test subset
      The group of training data points that a model build doesn't learn from, and on which the
      :term:`Model Evaluation Report` reports errors. See :term:`training subset`.

   training subset
      The group of training data points that a model build learns from. By default, a build
      uses 90% of the training data for training and 10% for testing, chosen at random. In
      PySimAI, assign a training data point to a subset by hand with
      :meth:`TrainingData.assign_subset() <ansys.simai.core.data.training_data.TrainingData.assign_subset>`
      and :class:`~ansys.simai.core.data.types.SubsetEnum`.

   variable
      A named quantity extracted from the :term:`reference sample`, such as a surface field, a
      volume field, or a scalar. You choose variables as model inputs, model outputs, or
      postprocessing inputs of a SimAI model. In PySimAI, list them with
      :meth:`Project.get_variables() <ansys.simai.core.data.projects.Project.get_variables>`.

   volume file
      The optional file of a training data point for a SimAI model, in VTU format (``.vtu``). It
      holds the volume (3D) fields and is needed only to predict volume fields.

.. _glossary_geomai_models:

GeomAI models
-------------

.. glossary::
   :sorted:

   build preset of a GeomAI model
      The preset that sets the training duration of a GeomAI model: the ``build_preset``
      parameter of :class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration`.
      According to the PySimAI code, its values are:

      - ``debug``: 4 minutes plus 15 seconds per geometry. The code describes it as a mode for
        pipeline testing and debugging, limited to a subset of four training data points and
        one :term:`epoch`.
      - ``short``: 45 minutes plus 15 seconds per geometry.
      - ``default``: 3 hours plus 15 seconds per geometry.
      - ``long``: 15 hours plus 15 seconds per geometry.

      Instead of a build preset, you can set the number of epochs with ``nb_epochs``. A model
      configuration takes exactly one of ``build_preset`` and ``nb_epochs``. The build presets
      of GeomAI models differ from the ``build_preset`` values of SimAI models: see
      :term:`build setting`.

      .. TODO: confirm what the debug build preset does for GeomAI models with the product team.

   epoch
      One pass of a GeomAI model over the whole training data during a model build. Set the
      number of epochs with the ``nb_epochs`` parameter of
      :class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration`, at least 1. To
      keep the training within its maximum runtime of 72 hours, Ansys SimAI can use fewer
      epochs than requested: compare ``requested_nb_epochs`` and ``nb_epochs`` in the
      :class:`~ansys.simai.core.data.geomai.workspaces.GeomAIModelManifest` of the workspace.
      SimAI models use :term:`iterations <iteration>`, not epochs.

   GeomAI model
      The type of AI model that trains on geometries only, with no simulation data, and
      generates new geometries in the same design language as its training data. It doesn't
      predict physical fields. In PySimAI, access GeomAI models through
      ``simai_client.geomai``, which returns a
      :class:`~ansys.simai.core.data.geomai.client.GeomAIClient`. PySimAI class:
      :class:`~ansys.simai.core.data.geomai.models.GeomAIModel`.

   geometry of a GeomAI model
      A 3D surface mesh used by a GeomAI model. Geometries play two roles: they're the training
      data of the model, one geometry file for each training data point, and they're the result
      of a generation, which you download from a :term:`prediction`. You can also upload a
      geometry to a GeomAI workspace to compute its :term:`projection`. In PySimAI, upload
      training data with
      :meth:`GeomAITrainingDataDirectory.create_from_file() <ansys.simai.core.data.geomai.training_data.GeomAITrainingDataDirectory.create_from_file>`,
      and upload a geometry with
      :meth:`GeomAIGeometryDirectory.upload() <ansys.simai.core.data.geomai.geometries.GeomAIGeometryDirectory.upload>`,
      which supports the VTP and STL formats. PySimAI class:
      :class:`~ansys.simai.core.data.geomai.geometries.GeomAIGeometry`.

   latent parameters
      The coordinates of a geometry in the :term:`latent space` of a GeomAI model: a list of
      floats that describes the shape in a compressed form. The first latent parameters capture
      the largest variations of the geometry, and the later ones capture finer details. To
      generate a geometry, pass latent parameters as ``latent_params`` to
      :class:`~ansys.simai.core.data.geomai.predictions.GeomAIPredictionConfiguration`. Their
      number can be less than or equal to the number of latent parameters of the model, which
      ``workspace.model_manifest.nb_latent_parameters`` returns.

   latent space
      The compressed representation of the geometries that a GeomAI model learns during its
      model build. Each geometry is a point of the latent space, described by its
      :term:`latent parameters`. Its dimension is the ``nb_latent_param`` parameter of
      :class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration`, from 2 to 1024,
      512 by default. Keep the default value unless you can assess the performance of your
      models for other values.

   projection
      The computation of the :term:`latent parameters` of an existing geometry in the latent
      space of a GeomAI model. In PySimAI, run it with
      :meth:`GeomAIProjectionDirectory.run() <ansys.simai.core.data.geomai.projections.GeomAIProjectionDirectory.run>`,
      then read the result with
      :meth:`GeomAIProjection.get_latent_parameters() <ansys.simai.core.data.geomai.projections.GeomAIProjection.get_latent_parameters>`.
      PySimAI class: :class:`~ansys.simai.core.data.geomai.projections.GeomAIProjection`.

More about the glossary
-----------------------

- :doc:`/getting-started/overview/architecture`
- :doc:`/getting-started/overview/object-model`
- :doc:`/user-guide/simai-models/build-settings`
- :doc:`/getting-started/overview/key-concepts`
