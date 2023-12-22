.. _selections:

Selections
===========

Selections Basics
-----------------
.. py:module:: ansys.simai.core.data.selections

The Selection class allows you to run a large number of operations in parallel,
by manipulating whole collections of SimAI models
(:class:`Geometries <ansys.simai.core.data.geometries.Geometry>`,
:class:`Predictions <ansys.simai.core.data.predictions.Prediction>`,
:py:class:`Post-Processings <ansys.simai.core.data.post_processings.PostProcessing>`).

A Selection is created by combining a list of
:class:`Geometries <ansys.simai.core.data.geometries.Geometry>` with a list of
:class:`~ansys.simai.core.data.types.BoundaryConditions`.

.. code-block:: python

   from ansys.simai.core.data.selections import Selection

   geometries = simai.geometries.list()[:4]
   boundary_conditions = [dict(Vx=vx) for vx in [12.2, 12.4, 12.6]]
   selection = Selection(geometries, boundary_conditions)


The resulting selection contains all possible combinations between
the geometries and boundary conditions. Each of those combinations is a
:class:`~ansys.simai.core.data.selections.Point`, which can be viewed as a potential
:class:`~ansys.simai.core.data.predictions.Prediction`.

At first all predictions may not all exist, they can be run with the :func:`~Selection.run_predictions` method:

.. code-block:: python

   # run all predictions
   selection.run_predictions()

   all_predictions = selection.predictions


Selections API Reference
------------------------

In essence a :class:`~ansys.simai.core.data.selections.Selection` is a collection of :class:`points <ansys.simai.core.data.selections.Point>`.

.. autoclass:: Point()
    :members:
    :inherited-members:


.. autoclass:: Selection()
    :members:
    :inherited-members:


Post-processing Basics
----------------------

The :attr:`~Selection.post` namespace allows you to run and access all post-processings for existing predictions.
Please see :py:class:`~ansys.simai.core.data.selection_post_processings.SelectionPostProcessingsMethods`
for available post-processings.

.. code-block:: python

    coeffs = selection.post.global_coefficients()

    coeffs.data  # is a list of results of each post-processings.


Results for exportable post-processings
(:py:class:`~ansys.simai.core.data.post_processings.GlobalCoefficients`
and :py:class:`~ansys.simai.core.data.post_processings.SurfaceEvol`)
can be exported in batch with the :func:`~ansys.simai.core.data.lists.ExportablePPList.export()` method:

.. code-block:: python

    selection.post.surface_evol(axis="x", delta=13.5).export("xlsx").download(
        "/path/to/file.xlsx"
    )

Please note that the ``csv`` export generates a zip archive containing multiple csv files.
They can be read directly with python by using zipfile:

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


Binary post-processings results can be downloaded by looping on the list, for instance:

.. code-block:: python

    for vtu in selection.post.volume_vtu():
        vtu.data.download(f"/path/to/vtu_{vtu.id}")


Post-processing API Reference
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
