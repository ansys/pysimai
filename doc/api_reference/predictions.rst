Predictions
===========

.. py:module:: ansys.simai.core.data.predictions

The Prediction module is in charge of running the *SimAI-powered
predictions* on the :py:class:`Geometries<ansys.simai.core.data.geometries.Geometry>` you have uploaded.

It represents a numerical prediction with geometry and boundary conditions.
The arguments to :py:func:`predictions.run()<PredictionDirectory.run>` depend on your model.

.. code-block:: python

    # Run a prediction on a given geometry with the specified velocity.
    velocity = 10.0
    prediction = geometry.run_prediction(Vx=velocity)

.. warning::
    In order to better describe different physical constraints,
    the SimAI SDK has been updated to describe boundary conditions with a dict,
    replacing the previous tuple of 3 numbers.
    Please make sure to update your existing scripts, for instance from ``(3.4, 0, 0)`` to ``dict(Vx=3.4)``;
    there is no need to put ``Vy=0`` and ``Vz=0`` anymore if your project has not been trained on those velocities.
    In method calls, boundary conditions can be passed directly as arguments: ``run_prediction(Vx=3.4)``.

Directory
---------

.. autoclass:: PredictionDirectory()
    :members:

Model
-----

.. autoclass:: Prediction()
    :members:
    :inherited-members:
