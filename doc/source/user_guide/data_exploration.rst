.. _data_exploration:

Data Exploration
================

The SimAI SDK provides utilities to help you run a large amount of predictions and post-processings,
explore your data and gather insights from it.

Selections
----------

:class:`Selections<ansys.simai.core.data.selections.Selection>` enable you to manipulate a large number of
geometries and boundary conditions simultaneously.
It allows you to easily run many predictions or post-processings in parallel.

A Selection is created by combining a list of geometries with a list of boundary conditions.

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

You can dive deeper in the :ref:`selections page<selections>`

Sweeping
--------

To help building selections, the SimAIClient exposes two methods that are useful for different strategies:
The :meth:`geometry.sweep<ansys.simai.core.data.geometries.Geometry.sweep>` method aims to explore the surroundings
of a given geometry and can help with local optimization or gradient descent.
It finds geometries which have metadata closest to the candidate geometry
(only for numerical metadata).

.. code-block:: python

   geometry = simai.geometries.list()[0]
   neighbour_geometries = geometry.sweep(sweep_variables=["height", "length"])

   # with which a selection can be built:
   selection = Selection(neighbour_geometries, [dict(Vx=13.4)])

Filtering geometries
--------------------

The :meth:`GeometryDirectory.list<ansys.simai.core.data.geometries.GeometryDirectory.list>` method enables to take a
more brute-force approach, by allowing to select large swaths of geometries with range filters.

.. code-block:: python

   from ansys.simai.core.data.types import Range

   geometries = simai.geometries.list(filters={"SINK": Range(-5.1, -4.8)})

Geometry exploration methods are described in the :ref:`geometries page<geometries>`
