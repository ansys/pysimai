:description: Run many SimAI model predictions and their postprocessings at once with a Selection of geometries and scalars, and build selections with Geometry.sweep and Range filters.

.. _data_exploration:

.. _simai_models_explore_predictions_with_selections:

Explore many predictions of a SimAI model with selections
=========================================================

**Applies to:** SimAI models

Run many predictions and their postprocessings at once with a
:class:`~ansys.simai.core.data.selections.Selection` object, which combines a list of geometries
with a list of scalars. Build the list of geometries with
:meth:`Geometry.sweep() <ansys.simai.core.data.geometries.Geometry.sweep>` or with
:class:`~ansys.simai.core.data.types.Range` filters.

Script to explore many predictions of a SimAI model with selections
-------------------------------------------------------------------

This script selects the geometries of a workspace whose ``length`` metadata is between 4 and 5,
runs a prediction for each of them at three inlet velocities, and exports all the global
coefficients to an Excel file.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.selections import Selection
   from ansys.simai.core.data.types import Range
   from ansys.simai.core.errors import SimAIError

   simai_client = asc.SimAIClient(organization="<your_organization>")
   simai_client.set_current_workspace("<your_workspace_name>")

   # Select geometries by metadata with filters
   geometries = simai_client.geometries.list(filters={"length": Range(min=4, max=5)})
   scalars = [{"Vx": vx} for vx in [12.2, 12.4, 12.6]]

   # Create a selection
   selection = Selection(geometries, scalars)
   print(f"{len(selection.points)} points in the selection")

   try:
       # Run the predictions of a selection
       selection.run_predictions()
       selection.wait()

       # Run postprocessings on a selection
       global_coefficients = selection.post.global_coefficients()
       global_coefficients.export(format="xlsx").download("selection_global_coefficients.xlsx")
       print("Global coefficients exported")
   except SimAIError as error:
       print(f"Processing failed: {error}")

Create a selection
------------------

A selection contains one :class:`~ansys.simai.core.data.selections.Point` object for each
combination of a geometry and a set of scalars. Three geometries and three sets of scalars give
nine points:

.. code-block:: python

   selection = Selection(geometries, [{"Vx": 12.2}, {"Vx": 12.4}, {"Vx": 12.6}])

The ``scalars`` parameter is required. It takes one dictionary or a list of dictionaries of
numbers. The optional ``tolerance`` parameter, ``10**-6`` by default, sets when two scalar values
count as equal.

When you create a selection, it finds the predictions that already exist for its points. Call
``selection.reload()`` to find predictions run since then, for example from another session.

Run the predictions of a selection
----------------------------------

``selection.run_predictions()`` runs a prediction for each point that has none yet. Then:

- ``selection.wait()`` blocks until all the predictions and postprocessings of the selection end.
  It raises :class:`~ansys.simai.core.errors.SimAIError` for one failure, or
  :class:`~ansys.simai.core.errors.MultipleErrors` for several.
- ``selection.predictions`` lists the existing predictions.
- ``selection.get_runnable_predictions()`` lists the points with no prediction yet.

Run postprocessings on a selection
----------------------------------

``selection.post`` runs the same postprocessing on every prediction of the selection. Its
methods are ``global_coefficients()``, ``surface_evolution(axis, delta)``,
``slice(axis, coordinate)``, ``volume_vtu()``, ``surface_vtp()``, and
``surface_vtp_td_location()``. For what each postprocessing returns, see
:doc:`/user-guide/simai-models/postprocess-predictions`.

Each method returns a list of postprocessings
(:class:`~ansys.simai.core.data.lists.PPList`) with two shortcuts:

- ``data`` returns the data of all the postprocessings, once they're all ready.
- ``wait()`` blocks until they're all ready.

``global_coefficients()`` and ``surface_evolution()`` return an
:class:`~ansys.simai.core.data.lists.ExportablePPList` object, which also exports all the results
in one file with ``export(format=...)``: ``"json"`` (default), ``"xlsx"``, or ``"csv.zip"``.

.. code-block:: python

   all_values = [gc.data for gc in selection.post.global_coefficients()]

.. _sweeping:

Select the neighbors of a geometry with a sweep
-----------------------------------------------

:meth:`Geometry.sweep() <ansys.simai.core.data.geometries.Geometry.sweep>` returns the geometries
whose numerical metadata are closest to a candidate geometry. It helps you explore the
surroundings of a design, for local optimization or gradient descent:

.. code-block:: python

   geometry = simai_client.geometries.get(name="<your_geometry_name>")
   neighbors = geometry.sweep(swept_metadata=["height", "length"])
   selection = Selection(neighbors, [{"Vx": 13.4}])

For each swept metadata, the method returns the geometries with the closest smaller and larger
values, and the same values for the other swept metadata. Its main optional parameters:

- ``fixed_metadata``: metadata whose value must equal the one of the candidate geometry.
- ``order``: the number of smaller and larger value groups to return. The default is ``1``.
- ``include_center``: also return the geometries with the same values as the candidate,
  including the candidate. The default is ``False``.
- ``include_diagonals``: also return the diagonal neighbors when you sweep more than one
  metadata. The default is ``False``.
- ``geometries``: the geometries to search. The default is all the geometries of the current
  workspace.

The method raises ``ValueError`` if a metadata doesn't exist on the candidate geometry or isn't
numerical.

.. _filtering_geometries:

Select geometries by metadata with filters
------------------------------------------

:meth:`GeometryDirectory.list() <ansys.simai.core.data.geometries.GeometryDirectory.list>` selects
large groups of geometries by metadata. Each filter is a string, a number, or a
:class:`~ansys.simai.core.data.types.Range` object for numerical metadata:

.. code-block:: python

   geometries = simai_client.geometries.list(
       filters={"variant": "A", "SINK": Range(-5.1, -4.8)}
   )

A ``Range`` includes its ``min`` and ``max`` boundaries. Both are optional: ``Range(min=4)``
matches all values greater than or equal to 4. The method raises ``TypeError`` if you apply a
``Range`` to non-numerical metadata.

Expected result when you explore many predictions of a SimAI model with selections
----------------------------------------------------------------------------------

The complete script prints the number of points, then ``Global coefficients exported``. The file
``selection_global_coefficients.xlsx`` holds the global coefficients of all the predictions.

Errors when you explore many predictions of a SimAI model with selections
-------------------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.MultipleErrors`
     - Several predictions or postprocessings of the selection failed.
     - Read the errors in the exception, fix the geometries or scalars, and run again.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - ``export()`` got a format other than ``json``, ``xlsx``, ``csv.zip``, or the selection has
       no prediction to export.
     - Use an accepted format, and run the predictions first.
   * - ``ValueError``
     - ``Selection`` got no scalars, or ``sweep()`` got an unknown or non-numerical metadata.
     - Pass scalars, and sweep numerical metadata only.
   * - ``TypeError``
     - ``Selection`` got geometries that aren't ``Geometry`` objects or scalars that aren't
       dictionaries of numbers, or a ``Range`` filter was applied to non-numerical metadata.
     - Pass ``Geometry`` objects and numerical scalars, and use ``Range`` on numerical metadata
       only.

More about how to explore many predictions of a SimAI model with selections
---------------------------------------------------------------------------

- :doc:`/user-guide/simai-models/run-predictions`
- :doc:`/user-guide/simai-models/postprocess-predictions`
- :doc:`/user-guide/common-tasks/work-asynchronously`
- :class:`~ansys.simai.core.data.selections.Selection`
- :class:`~ansys.simai.core.data.selection_post_processings.SelectionPostProcessingsMethods`
