:description: Upload a geometry to the workspace of a SimAI model, read the expected scalars from workspace.model_manifest, and run a prediction with geometry.run_prediction or simai_client.predictions.run.

.. _simai_models_run_predictions:

Run a prediction with a SimAI model
===================================

**Applies to:** SimAI models

Upload a geometry to the workspace of a SimAI model with
:meth:`GeometryDirectory.upload() <ansys.simai.core.data.geometries.GeometryDirectory.upload>`,
then run a prediction on it with
:meth:`Geometry.run_prediction() <ansys.simai.core.data.geometries.Geometry.run_prediction>`.
A prediction is the result of the SimAI model on one geometry with one set of scalars.

Script to run a prediction with a SimAI model
---------------------------------------------

This script reads the scalars that the SimAI model expects, uploads one geometry, runs a
prediction, and prints its confidence score.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.errors import ProcessingError

   simai_client = asc.SimAIClient(organization="<your_organization>")

   # Choose the workspace
   simai_client.set_current_workspace("<your_workspace_name>")
   workspace = simai_client.current_workspace

   # Read what the SimAI model expects
   # Scalars that the SimAI model expects as input
   print(workspace.model_manifest.scalars)

   # Upload a geometry
   geometry = simai_client.geometries.upload(
       "<path_to_your_geometry>.vtp", workspace=workspace
   )

   try:
       geometry.wait()

       # Run the prediction
       prediction = geometry.run_prediction(scalars={"<your_scalar_name>": 10.5})
       prediction.wait()
       print(f"Prediction {prediction.id} is ready")

       # Read the confidence score
       print(f"Confidence score: {prediction.confidence_score} ({prediction.raw_confidence_score})")
   except ProcessingError as error:
       print(f"Processing failed: {error}")

To get global coefficients and field files from the prediction, see
:doc:`/user-guide/simai-models/postprocess-predictions`.

Choose the workspace
--------------------

Each successful model build creates a workspace, where you upload geometries and run
predictions with its SimAI model. Set it as the current workspace of the client with
:meth:`SimAIClient.set_current_workspace() <ansys.simai.core.client.SimAIClient.set_current_workspace>`,
so that the geometry and prediction methods use it by default:

.. code-block:: python

   simai_client.set_current_workspace("<your_workspace_name>")

You can also pass ``workspace="<your_workspace_name>"`` when you create the client. The
``workspace`` parameter of methods such as ``simai_client.geometries.upload()`` takes a
:class:`~ansys.simai.core.data.workspaces.Workspace` object or a workspace ID, not a name. To find
the workspace of the last model build of a project, call ``project.get_last_workspace()``.

Read what the SimAI model expects
---------------------------------

The :attr:`Workspace.model_manifest <ansys.simai.core.data.workspaces.Workspace.model_manifest>`
property returns a :class:`~ansys.simai.core.data.workspaces.ModelManifest` object that
describes the SimAI model of the workspace:

- ``scalars``: the scalars expected as input of a prediction.
- ``geometry``: the geometry format expected by the SimAI model.
- ``physical_quantities``: the physical quantities that the prediction outputs.
- ``post_processings``: the available postprocessings and their parameters.

For the current workspace, ``simai_client.predictions.info`` returns the scalars and the
physical quantities in one dictionary.

Upload a geometry
-----------------

A geometry is the 3D surface mesh of a design. Upload it with ``simai_client.geometries.upload()``:

- VTP format (``.vtp``) is recommended.
- STL format (``.stl``) works only in the workspace of a SimAI model.
- To upload a geometry made of several STL files, put them in one ZIP archive (``.zip``).

The ``file`` parameter is a path or a ``(file, name)`` tuple. The ``metadata`` parameter adds
key-value pairs to the geometry, which you can filter on later. Lists and nested objects aren't
supported.

.. code-block:: python

   geometry = simai_client.geometries.upload(
       ("<path_to_your_geometry>.vtp", "<name_in_the_workspace>.vtp"),
       metadata={"length": 4.2, "variant": "A"},
   )

Ansys SimAI processes the geometry after upload. Call ``geometry.wait()`` before you run a
prediction on it. To use a geometry that's already in the workspace, get it with
``simai_client.geometries.get(name="<your_geometry_name>")``.

Run the prediction
------------------

Call ``geometry.run_prediction()`` with the scalars as a dictionary, or as keyword arguments:

.. code-block:: python

   prediction = geometry.run_prediction(scalars={"Vx": 10.5, "Vy": 2})
   # Equivalent:
   prediction = geometry.run_prediction(Vx=10.5, Vy=2)

:meth:`PredictionDirectory.run() <ansys.simai.core.data.predictions.PredictionDirectory.run>`
does the same from the geometry object or ID:

.. code-block:: python

   prediction = simai_client.predictions.run(geometry, {"Vx": 10.5, "Vy": 2})

Both methods return a :class:`~ansys.simai.core.data.predictions.Prediction` object right away.
If a prediction with the same scalars already exists on the geometry, ``run_prediction()``
returns it. Call ``prediction.wait()`` to block until the prediction is ready. ``wait()`` raises
:class:`~ansys.simai.core.errors.ProcessingError` if the prediction fails.

Read the confidence score
-------------------------

The confidence score shows how familiar a prediction is to the SimAI model compared with its
training data. It isn't a measure of accuracy:

- ``prediction.confidence_score`` is ``"high"`` or ``"low"``.
- ``prediction.raw_confidence_score`` is the value from 0 to 1.

Both properties block until the prediction is ready.

Expected result when you run a prediction with a SimAI model
------------------------------------------------------------

The complete script prints the expected scalars, then:

.. code-block:: text

   Prediction <prediction_id> is ready
   Confidence score: high (0.87)

Errors when you run a prediction with a SimAI model
---------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The processing of the geometry or the prediction failed.
     - Check the geometry format and that the scalars match ``workspace.model_manifest.scalars``.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The file extension isn't accepted.
     - Upload a ``.vtp``, ``.stl``, or ``.zip`` file.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - No current workspace is set and no ``workspace`` parameter is passed.
     - Call ``simai_client.set_current_workspace()`` or pass a ``workspace`` object or ID.
   * - :class:`~ansys.simai.core.errors.InvalidConfigurationError`
     - ``set_current_workspace()`` found no workspace with this name. The message lists the
       available workspaces.
     - Use one of the listed names.
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No geometry has this name or ID.
     - Check the name or the ID.

More about how to run a prediction with a SimAI model
-----------------------------------------------------

- :doc:`/user-guide/simai-models/postprocess-predictions`
- :doc:`/user-guide/simai-models/explore-predictions-with-selections`
- :ref:`ref_basic_run_predictions`
- :class:`~ansys.simai.core.data.geometries.GeometryDirectory`
- :class:`~ansys.simai.core.data.predictions.Prediction`
- :class:`~ansys.simai.core.data.workspaces.ModelManifest`
