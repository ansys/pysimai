:description: Run postprocessings on a SimAI model prediction with prediction.post (global coefficients, predicted scalars, surface VTP, volume VTU, slice, surface evolution, point cloud) and download or export their results.

.. _simai_models_postprocess_predictions:

Run postprocessings on a SimAI model prediction
===============================================

**Applies to:** SimAI models

Get global coefficients, field files, slices, and other results from a prediction with the
methods of :attr:`Prediction.post <ansys.simai.core.data.predictions.Prediction.post>`, a
:class:`~ansys.simai.core.data.post_processings.PredictionPostProcessings` object. Each method
runs a postprocessing on Ansys SimAI and returns a
:class:`~ansys.simai.core.data.post_processings.PostProcessing` object.

Script to run postprocessings on a SimAI model prediction
---------------------------------------------------------

This script gets the first prediction of a workspace, prints its global coefficients, and
downloads its surface fields as a VTP file and its global coefficients as an Excel file.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.errors import ProcessingError

   simai_client = asc.SimAIClient(organization="<your_organization>")
   simai_client.set_current_workspace("<your_workspace_name>")

   prediction = simai_client.predictions.list()[0]

   try:
       # Get the global coefficients
       global_coefficients = prediction.post.global_coefficients()
       for name, value in global_coefficients.data.items():
           print(name, value["data"])

       # Download or export the results
       global_coefficients.export(format="xlsx").download("global_coefficients.xlsx")

       # Download the surface fields as a VTP file
       prediction.post.surface_vtp().data.download("prediction_surface.vtp")
       print("Files downloaded")
   except ProcessingError as error:
       print(f"Postprocessing failed: {error}")

How postprocessing methods work
-------------------------------

Each method of ``prediction.post`` is non-blocking. It starts the postprocessing on the first call
and returns the postprocessing object right away. Later calls with the same parameters return the
same postprocessing without running it again.

- ``wait()`` blocks until the postprocessing is ready, and raises
  :class:`~ansys.simai.core.errors.ProcessingError` if it fails.
- The ``data`` property also blocks until the result is ready.
- ``run=False`` gets an existing postprocessing without computing it, and returns ``None`` if it
  doesn't exist yet: ``prediction.post.surface_vtp(run=False)``.

To run postprocessings on many predictions, request them all before you read any data, or use a
selection. For more information, see :doc:`/user-guide/common-tasks/work-asynchronously` and
:doc:`/user-guide/simai-models/explore-predictions-with-selections`.

Get the global coefficients
---------------------------

:meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.global_coefficients`
computes the global coefficients defined in the model configuration. Its ``data`` property is a
dictionary with one entry per global coefficient. The value is in the ``"data"`` key:

.. code-block:: python

   values = prediction.post.global_coefficients().data
   print(values["<your_global_coefficient_name>"]["data"])

Get the predicted scalars
-------------------------

When the SimAI model has scalars as model outputs,
:meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.predict_scalars`
returns them. Its ``data`` property has the same structure as for global coefficients:

.. code-block:: python

   predicted = prediction.post.predict_scalars().data

Download the surface fields as a VTP file
-----------------------------------------

Two methods return the predicted surface fields in VTP format:

- :meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.surface_vtp` associates
  all the data with cells. Variables associated with points in the reference sample are
  associated with cells in the result.
- :meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.surface_vtp_td_location`
  keeps the original data association of the reference sample.

.. code-block:: python

   prediction.post.surface_vtp().data.download("prediction_surface.vtp")
   prediction.post.surface_vtp_td_location().data.download("prediction_surface_original.vtp")

Download the volume fields as a VTU file
----------------------------------------

When the SimAI model predicts volume fields,
:meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.volume_vtu` returns them
in VTU format:

.. code-block:: python

   prediction.post.volume_vtu().data.download("prediction_volume.vtu")

Get a slice of the prediction
-----------------------------

:meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.slice` cuts the
prediction with a plane normal to an axis:

- ``axis``: ``"x"``, ``"y"``, or ``"z"``.
- ``coordinate``: the position of the plane along the axis.
- ``format``: ``"png"`` (default) for an image, or ``"vtp"`` for a surface file.

.. code-block:: python

   prediction.post.slice(axis="x", coordinate=0.5, format="png").data.download("slice_x.png")

Get the surface evolution along an axis
---------------------------------------

:meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.surface_evolution`
computes the surface evolution of the prediction along an axis:

- ``axis``: ``"x"``, ``"y"``, or ``"z"``.
- ``delta``: the increment of the abscissa, in meters. It must be a positive number.

Its ``data`` property downloads JSON data, and ``as_dict()`` loads it as a Python dictionary:

.. code-block:: python

   surface_evolution = prediction.post.surface_evolution(axis="x", delta=0.01)
   evolution = surface_evolution.as_dict()

Predict the volume fields on a point cloud
------------------------------------------

To get the predicted volume on a point cloud of your own, attach a point cloud in VTP format to the
geometry with :meth:`Geometry.upload_point_cloud() <ansys.simai.core.data.geometries.Geometry.upload_point_cloud>`,
then call :meth:`~ansys.simai.core.data.post_processings.PredictionPostProcessings.custom_volume_point_cloud`:

.. code-block:: python

   prediction.geometry.upload_point_cloud("<path_to_your_point_cloud>.vtp")
   prediction.post.custom_volume_point_cloud().data.download("prediction_point_cloud.vtp")

The method raises :class:`~ansys.simai.core.errors.InvalidOperationError` if the geometry has no
point cloud.

Download or export the results
------------------------------

Binary results, such as VTP, VTU, PNG, and JSON files, come as a
:class:`~ansys.simai.core.data.downloads.DownloadableResult` object in the ``data`` property:

- ``download(file)`` writes the result to a path or a binary file object.
- ``in_memory()`` returns the result as an :class:`io.BytesIO` object.

The global coefficients, the predicted scalars, and the surface evolution can also be exported
as tables with ``export(format=...)``, which returns a ``DownloadableResult`` object. The formats
are ``"json"`` (default), ``"xlsx"``, and ``"csv.zip"``, a ZIP file of CSV sheets:

.. code-block:: python

   prediction.post.global_coefficients().export(format="csv.zip").download("global_coefficients.zip")

List and delete postprocessings
-------------------------------

``prediction.post.list()`` returns the postprocessings of the prediction. Pass a postprocessing
class, such as :class:`~ansys.simai.core.data.post_processings.SurfaceVTP`, to list one type only.
Call ``delete()`` on a postprocessing to delete it and its result data.

Expected result when you run postprocessings on a SimAI model prediction
------------------------------------------------------------------------

The complete script prints one line per global coefficient, with its name and value, then
``Files downloaded``. The folder now holds ``global_coefficients.xlsx`` and
``prediction_surface.vtp``.

Errors when you run postprocessings on a SimAI model prediction
---------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The postprocessing failed on Ansys SimAI.
     - Check that the SimAI model supports this postprocessing in
       ``workspace.model_manifest.post_processings``.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - ``slice()`` got an axis other than ``x``, ``y``, ``z``, or a format other than ``png``,
       ``vtp``.
     - Use an accepted value.
   * - ``TypeError``
     - ``surface_evolution()`` got an axis other than ``x``, ``y``, ``z``, or a ``delta`` that
       isn't a positive number.
     - Use an accepted value.
   * - :class:`~ansys.simai.core.errors.InvalidOperationError`
     - ``custom_volume_point_cloud()`` was called on a geometry with no point cloud.
     - Upload a point cloud with ``geometry.upload_point_cloud()``.

More about how to run postprocessings on a SimAI model prediction
-----------------------------------------------------------------

- :doc:`/user-guide/simai-models/run-predictions`
- :doc:`/user-guide/simai-models/explore-predictions-with-selections`
- :ref:`ref_basic_run_predictions`
- :class:`~ansys.simai.core.data.post_processings.PredictionPostProcessings`
- :class:`~ansys.simai.core.data.downloads.DownloadableResult`
