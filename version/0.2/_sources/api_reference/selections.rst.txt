.. _selections:

Selections
==========

Selection basics
----------------
.. py:module:: ansys.simai.core.data.selections

The :class:`Selection<ansys.simai.core.data.selections.Selection>` class allows you
to run a large number of operations in parallel by manipulating whole collections of SimAI models
(:class:`Geometries <ansys.simai.core.data.geometries.Geometry>`,
:class:`Predictions <ansys.simai.core.data.predictions.Prediction>`, and
:py:class:`Post-Processings <ansys.simai.core.data.post_processings.PostProcessing>` instances).

You create a selection by combining a list of :class:`Geometry <ansys.simai.core.data.geometries.Geometry>`
instances with a list of :class:`~ansys.simai.core.data.types.BoundaryConditions` instances:

.. code-block:: python

   from ansys.simai.core.data.selections import Selection

   geometries = simai.geometries.list()[:4]
   boundary_conditions = [dict(Vx=vx) for vx in [12.2, 12.4, 12.6]]
   selection = Selection(geometries, boundary_conditions)


The resulting selection contains all possible combinations between the geometries and
boundary conditions. Each of those combinations is a :class:`~ansys.simai.core.data.selections.Point`
instance, which can be viewed as a potential :class:`~ansys.simai.core.data.predictions.Prediction`
instance.

At first, all predictions may not exist. However, you can use the :meth:`~Selection.run_predictions`
method to run them:

.. code-block:: python

   # run all predictions
   selection.run_predictions()

   all_predictions = selection.predictions


Selection API reference
------------------------

In essence, a :class:`~ansys.simai.core.data.selections.Selection` instance is a
collection of :class:`points <ansys.simai.core.data.selections.Point>` instances.

.. autoclass:: Point()
    :members:
    :inherited-members:


.. autoclass:: Selection()
    :members:
    :inherited-members:


Postprocessing basics
----------------------

The :attr:`~Selection.post` namespace allows you to run and access all postprocessings
for existing predictions. For available postprocessings, see the
:py:class:`~ansys.simai.core.data.selection_post_processings.SelectionPostProcessingsMethods`
class.

.. code-block:: python

    coeffs = selection.post.global_coefficients()

    coeffs.data  # is a list of results of each post-processings.


You can use the :meth:`~ansys.simai.core.data.lists.ExportablePPList.export()`
method to export results in batch for exportable postprocessings
(:py:class:`~ansys.simai.core.data.post_processings.GlobalCoefficients`
and :py:class:`~ansys.simai.core.data.post_processings.SurfaceEvolution` instances):

.. code-block:: python

    selection.post.surface_evolution(axis="x", delta=13.5).export("xlsx").download(
        "/path/to/file.xlsx"
    )

Note that a CSV export generates a ZIP file containing multiple CSV files.
You can read them directly using Python's `zipfile<https://docs.python.org/3/library/zipfile.html>`
module:

.. code-block:: python

    import zipfile
    import csv
    from io import TextIOWrapper

    data = selection.post.global_coefficients().export("csv.zip").in_memory()

    with zipfile.ZipFile(data) as archive:
        csv_data = csv.reader(TextIOWrapper(archive.open("Global_Coeffs.csv")))

        # or with pandas:
        import pandas as pd

        df_geom = pd.read_csv(archive.open("Geometries.csv"))


You can download binary postprocessings results by looping on the list:

.. code-block:: python

    for vtu in selection.post.volume_vtu():
        vtu.data.download(f"/path/to/vtu_{vtu.id}")


Postprocessing API reference
-----------------------------

.. py:module:: ansys.simai.core.data.selection_post_processings

.. autoclass:: SelectionPostProcessingsMethods()
    :members:
    :inherited-members:


Collections
-----------

.. py:module:: ansys.simai.core.data.lists

.. autoclass:: PPList()
    :members:

.. autoclass:: ExportablePPList()
    :members:


Helpers
-------

.. py:module:: ansys.simai.core.data.downloads

.. autoclass:: DownloadableResult()
    :members:
