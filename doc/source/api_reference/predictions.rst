.. _predictions:

Predictions
===========

.. py:module:: ansys.simai.core.data.predictions

The ``Prediction`` module is in charge of running the *SimAI-powered
predictions* on the :py:class:`geometries<ansys.simai.core.data.geometries.Geometry>`
that you have uploaded.

A prediction represents a numerical prediction with geometry and boundary conditions.
The arguments to the :py:meth:`predictions.run()<PredictionDirectory.run>` method
depend on your model.

.. code-block:: python

    # Run a prediction on a given geometry with the specified velocity.
    velocity = 10.0
    prediction = geometry.run_prediction(Vx=velocity)


Directory
---------

.. autoclass:: PredictionDirectory()
    :members:

Model
-----

.. autoclass:: Prediction()
    :members:
    :inherited-members:
