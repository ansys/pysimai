.. _predictions:

Predictions
===========

.. py:module:: ansys.simai.core.data.predictions

The Prediction module is in charge of running the *SimAI-powered
predictions* on the :py:class:`Geometries<ansys.simai.core.data.geometries.Geometry>`
instances you have uploaded.

A prediction represents a numerical prediction with geometry and boundary conditions.
The arguments to the :py:meth:`predictions.run()<PredictionDirectory.run>` depend on your model.

.. code-block:: python

    # Run a prediction on a given geometry with the specified velocity.
    velocity = 10.0
    prediction = geometry.run_prediction(Vx=velocity)

.. warning::
    To better describe different physical constraints, the SimAI client has been
    updated to describe boundary conditions with a dictionary, replacing the previous
    tuple of three numbers. Make sure that you update your existing scripts, for example
    from ``(3.4, 0, 0)`` to ``dict(Vx=3.4)``. You no longer need to put ``Vy=0`` and ``Vz=0``
    if your project has not been trained on those velocities. In method calls, you can
    directly pass boundary conditions as arguments: ``run_prediction(Vx=3.4)``.

Directory
---------

.. autoclass:: PredictionDirectory()
    :members:

Model
-----

.. autoclass:: Prediction()
    :members:
    :inherited-members:
