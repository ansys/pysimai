:description: The PySimAI object model: organization, project, training data, model build, workspace, geometries, predictions and postprocessings, and the PySimAI class and client attribute of each object.

.. _concepts_object_model:

PySimAI object model
====================

**Applies to:** SimAI models and GeomAI models

Every PySimAI object represents an object of the Ansys SimAI platform. This page shows how the
objects relate to each other, and which class and client attribute give access to each one.

Hierarchy of the objects
------------------------

The objects follow the workflow of an AI model:

.. code-block:: text

   organization
   ├── training data (shared by all the projects)
   │   ├── training data points for SimAI models
   │   └── training data points for GeomAI models
   ├── SimAI project
   │   ├── training data points added to the project
   │   ├── model configuration
   │   └── model build ──> workspace
   │                       └── geometry
   │                           └── prediction
   │                               └── postprocessing
   └── GeomAI project
       ├── training data points added to the project
       ├── model configuration
       └── model build ──> workspace
                           ├── prediction (a generated geometry)
                           └── geometry ──> projection

Organization
   The account that groups the users of one company. All the training data uploaded in an
   organization is shared between its users. You choose it with the ``organization`` parameter
   of :class:`~ansys.simai.core.client.SimAIClient`.

Project
   The place where you gather training data and a model configuration to build AI models.

Training data
   The data that trains an AI model: simulation results for a SimAI model, geometries for a GeomAI
   model. "Training data" is a mass noun, so you count it in training data points.

Training data point
   One unit of training data, made of one or more training data parts. It belongs to the
   organization, and you add it to one or more projects. In PySimAI, it's a ``TrainingData``
   object, and each of its parts is a ``TrainingDataPart`` object.

Model build
   The process that trains an AI model from the training data and the model configuration of a
   project. Each successful model build creates a workspace.

Workspace
   The place where you use a built AI model.

Geometry
   The 3D surface mesh of a design. Its role depends on the type of AI model. For a SimAI model,
   you upload geometries to the workspace and run predictions on them. For a GeomAI model,
   geometries are the training data and the result of a generation, and you can also upload a
   geometry to the workspace to project it.

Prediction
   The result of running a trained AI model in a workspace. For a SimAI model, it's the
   predicted physical fields of one geometry with one set of scalars. For a GeomAI model, it's a
   new geometry generated with a configuration.

Postprocessing
   An analysis or export of the prediction of a SimAI model, such as global coefficients or the
   predicted surface fields in VTP format. GeomAI models have no postprocessings.

Structure of the training data
------------------------------

Training data is made of training data points, and each training data point is made of training
data parts, which are its files:

.. code-block:: text

   training data
   ├── training data points for SimAI models
   │   ├── training data point
   │   │   ├── training data part: surface file
   │   │   ├── training data part: volume file
   │   │   └── training data part: scalar file
   │   ├── training data point
   │   │   └── training data part: surface file
   │   └── ...
   └── training data points for GeomAI models
       ├── training data point
       │   └── training data part: geometry file
       └── ...

Classes and access for SimAI models
-----------------------------------

In the table, ``simai_client`` is a :class:`~ansys.simai.core.client.SimAIClient` instance.

.. list-table::
   :header-rows: 1
   :widths: 22 40 38

   * - Object
     - PySimAI class
     - Access
   * - Project
     - :class:`~ansys.simai.core.data.projects.Project`
     - ``simai_client.projects``
   * - Training data point
     - :class:`~ansys.simai.core.data.training_data.TrainingData`
     - ``simai_client.training_data``, ``project.list_training_data()``
   * - Training data part (file of a training data point)
     - :class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart`
     - ``simai_client.training_data_parts``, ``training_data.parts``
   * - Model configuration
     - :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`
     - ``project.last_model_configuration``, ``workspace.model_configuration``
   * - Model build
     - :class:`~ansys.simai.core.data.models.Model`
     - ``simai_client.models``, ``project.list_models()``, ``project.last_model``
   * - Workspace
     - :class:`~ansys.simai.core.data.workspaces.Workspace`
     - ``simai_client.workspaces``, ``project.list_workspaces()``,
       ``project.get_last_workspace()``
   * - Geometry
     - :class:`~ansys.simai.core.data.geometries.Geometry`
     - ``simai_client.geometries``, ``workspace.list_geometries()``
   * - Prediction
     - :class:`~ansys.simai.core.data.predictions.Prediction`
     - ``simai_client.predictions``, ``geometry.run_prediction()``,
       ``workspace.list_predictions()``
   * - Postprocessing
     - :class:`~ansys.simai.core.data.post_processings.PostProcessing` and its subclasses
     - ``simai_client.post_processings``, ``prediction.post``

Classes and access for GeomAI models
------------------------------------

In the table, ``geomai_client`` is ``simai_client.geomai``, a
:class:`~ansys.simai.core.data.geomai.client.GeomAIClient` instance. GeomAI models have no
postprocessings. In PySimAI, generating a geometry with a GeomAI model is a prediction, and
projecting an existing geometry onto the model of a workspace is a projection.

.. list-table::
   :header-rows: 1
   :widths: 22 40 38

   * - Object
     - PySimAI class
     - Access
   * - Project
     - :class:`~ansys.simai.core.data.geomai.projects.GeomAIProject`
     - ``geomai_client.projects``
   * - Training data point
     - :class:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingData`
     - ``geomai_client.training_data``, ``project.list_training_data()``
   * - Training data part (file of a training data point)
     - :class:`~ansys.simai.core.data.geomai.training_data_parts.GeomAITrainingDataPart`
     - ``geomai_client.training_data_parts``, ``training_data.parts``
   * - Model configuration
     - :class:`~ansys.simai.core.data.geomai.models.GeomAIModelConfiguration`
     - ``project.last_model_configuration``, ``workspace.model_configuration``
   * - Model build
     - :class:`~ansys.simai.core.data.geomai.models.GeomAIModel`
     - ``geomai_client.models``, ``project.list_models()``, ``project.last_model``
   * - Workspace
     - :class:`~ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace`
     - ``geomai_client.workspaces``, ``project.list_workspaces()``,
       ``project.get_last_workspace()``
   * - Geometry to project
     - :class:`~ansys.simai.core.data.geomai.geometries.GeomAIGeometry`
     - ``geomai_client.geometries``
   * - Generated geometry (prediction)
     - :class:`~ansys.simai.core.data.geomai.predictions.GeomAIPrediction`
     - ``geomai_client.predictions``, ``workspace.list_predictions()``
   * - Projection
     - :class:`~ansys.simai.core.data.geomai.projections.GeomAIProjection`
     - ``geomai_client.projections``, ``geometry.run_projection()``,
       ``workspace.list_projections()``

Directories and objects
-----------------------

Each client attribute, such as ``simai_client.projects``, is a directory: an object whose
methods find and create objects of one type on the server. Most directories have ``list()`` and
``get()`` methods, and many have ``create()``, ``upload()``, ``run()``, or ``delete()``. For
example, :class:`~ansys.simai.core.data.projects.ProjectDirectory` returns
:class:`~ansys.simai.core.data.projects.Project` objects.

Objects that the server computes, such as training data points, model builds, geometries, and
predictions, have a ``wait()`` method and the ``is_ready``, ``is_pending``, ``has_failed``, and
``failure_reason`` properties. For more information, see
:doc:`/user-guide/common-tasks/work-asynchronously`.

More about how to PySimAI object model
--------------------------------------

- :doc:`/getting-started/overview/key-concepts`
- :doc:`/getting-started/overview/glossary`
- :doc:`/user-guide/common-tasks/manage-resources`
- :doc:`/api_reference`
