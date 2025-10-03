.. _data_exploration:

Data exploration
================

The SimAI client provides utilities to help you run a large number of predictions and
postprocessings, explore your data, and gather insights from it.

Selections
----------

:ref:`selections` enable you to manipulate a large number of geometries and boundary conditions
simultaneously. They also allow you to easily run many predictions or postprocessings in parallel.

You create a selection by combining a list of geometries with a list of boundary conditions:

.. code-block:: python

   import ansys.simai.core
   from ansys.simai.core.data.selections import Selection

   simai = ansys.simai.core.from_config()
   geometries = simai.geometries.list()[:4]
   boundary_conditions = [dict(Vx=vx) for vx in [12.2, 12.4, 12.6]]
   selection = Selection(geometries, boundary_conditions)

   # run all predictions
   selection.run_predictions()

   # compute all global coefficients
   selection.post.global_coefficients()

   # get all results
   all_selection_coefficients = [
       global_coefficients.data
       for global_coefficients in selection.post.global_coefficients()
   ]

To help build selections, the Sim AI client exposes two methods that are useful for
different strategies:

- The :meth:`geometry.sweep<ansys.simai.core.data.geometries.Geometry.sweep>` method, which
  is described in :ref:`sweeping`.
- The :meth:`GeometryDirectory.list<ansys.simai.core.data.geometries.GeometryDirectory.list>`
  method, which is described in :ref:`filtering_geometries`.

For more information on selections and geometry exploration methods, see :ref:`selections`
and :ref:`geometries`.

.. _sweeping:

Sweeping
--------

The :meth:`geometry.sweep<ansys.simai.core.data.geometries.Geometry.sweep>` method allows you
to explore the surroundings of a given geometry, which can help with local optimization or
gradient descent. This method, only for numerical metadata, finds geometries that have
metadata closest to the candidate geometry.

.. code-block:: python

   geometry = simai.geometries.list()[0]
   neighbour_geometries = geometry.sweep(swept_metadata=["height", "length"])

   # with which a selection can be built:
   selection = Selection(neighbour_geometries, [dict(Vx=13.4)])

.. _filtering_geometries:

Filtering geometries
--------------------

The :meth:`GeometryDirectory.list<ansys.simai.core.data.geometries.GeometryDirectory.list>` method
allows you to take a more brute-force approach. With this method, you can select large swaths of
geometries with range filters.

.. code-block:: python

   from ansys.simai.core.data.types import Range

   geometries = simai.geometries.list(filters={"SINK": Range(-5.1, -4.8)})

