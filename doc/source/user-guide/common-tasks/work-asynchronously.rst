:description: Wait for PySimAI objects that the server computes, with wait(), a timeout, or SimAIClient.wait(), and send many requests before reading any result.

.. _best_practices:

Wait for objects computed by the server
=======================================

**Applies to:** SimAI models and GeomAI models

The Ansys SimAI server computes training data points, model builds, geometries, predictions,
and postprocessings after PySimAI requests them. This page shows how to wait for these objects
with their ``wait()`` method, such as
:meth:`Prediction.wait() <ansys.simai.core.data.predictions.Prediction.wait>`, and with
:meth:`SimAIClient.wait() <ansys.simai.core.client.SimAIClient.wait>`, and how to send many
requests at once.

Script to wait for objects computed by the server
-------------------------------------------------

This script runs predictions for every geometry of a workspace and three values of a scalar,
then reads the global coefficients once every prediction is done:

.. code-block:: python

    import ansys.simai.core as asc
    from ansys.simai.core.errors import MultipleErrors, ProcessingError

    simai_client = asc.SimAIClient(organization="<your_organization>")
    simai_client.set_current_workspace("<your_workspace_name>")

    speeds = [5.9, 5.10, 5.11]
    predictions = []

    # Send all requests before you read any result: these calls don't wait for the results
    for geometry in simai_client.geometries.list():
        for speed in speeds:
            prediction = geometry.run_prediction(scalars={"<your_scalar_name>": speed})
            prediction.post.global_coefficients()
            predictions.append(prediction)

    # Wait for all predictions and postprocessings requested by this script
    try:
        simai_client.wait()
    except MultipleErrors as errors:
        for error in errors.exceptions:
            print(f"Failed: {error}")
    except ProcessingError as error:
        print(f"Failed: {error}")

    for prediction in predictions:
        if prediction.is_ready:
            print(prediction.post.global_coefficients().data)

How PySimAI handles server computations
---------------------------------------

PySimAI doesn't use the ``async`` and ``await`` keywords of Python, but most requests return
before the server finishes its work. Uploading a geometry blocks until the upload ends. Running
a prediction or a postprocessing returns the new object immediately, before the server computes
the result. You can then request many computations without waiting for any of them.

Objects that the server computes have these properties:

- ``is_pending``: ``True`` while the server computes the object.
- ``is_ready``: ``True`` when the computation succeeded.
- ``has_failed``: ``True`` when the computation failed.
- ``failure_reason``: the message that explains the failure, if any.

Wait for one object
-------------------

To wait for one object, call its ``wait()`` method, for example
:meth:`Prediction.wait() <ansys.simai.core.data.predictions.Prediction.wait>`. The method blocks
until the computation ends and returns ``True``. If the computation fails, it raises
:class:`~ansys.simai.core.errors.ProcessingError`, whose message includes the failure reason.
Handle the failure with ``try`` and ``except``:

.. code-block:: python

    import ansys.simai.core as asc
    from ansys.simai.core.errors import ProcessingError

    simai_client = asc.SimAIClient(organization="<your_organization>")
    simai_client.set_current_workspace("<your_workspace_name>")

    geometry = simai_client.geometries.get(name="<your_geometry_name>")
    prediction = geometry.run_prediction(scalars={"<your_scalar_name>": 10.0})
    try:
        prediction.wait()
        print("The prediction is ready.")
    except ProcessingError:
        print(f"The prediction failed: {prediction.failure_reason}")

Wait with a timeout
-------------------

Pass ``timeout`` in seconds to stop waiting after this time. With a timeout, ``wait()`` returns
``False`` if the computation is still running, and the computation continues on the server.
Use a loop to report progress during a long computation, such as a model build:

.. code-block:: python

    import ansys.simai.core as asc
    from ansys.simai.core.errors import ProcessingError

    simai_client = asc.SimAIClient(organization="<your_organization>")
    project = simai_client.projects.get(name="<your_project_name>")

    # Reuse the configuration of the last build of the project
    model = simai_client.models.build(project.last_model_configuration)
    try:
        while not model.wait(timeout=600):
            print("The model build is still running...")
        print("The model is ready.")
    except ProcessingError:
        print(f"The model build failed: {model.failure_reason}")

A ``False`` return value only means that the timeout expired. A failure always raises
:class:`~ansys.simai.core.errors.ProcessingError`.

Wait for all predictions and postprocessings
--------------------------------------------

:meth:`SimAIClient.wait() <ansys.simai.core.client.SimAIClient.wait>` waits for every prediction
and postprocessing known to the client in the current script. It doesn't wait for training data,
geometries, or model builds: call ``wait()`` on those objects. If one computation fails,
``SimAIClient.wait()`` raises its exception. If several computations fail, it raises
:class:`~ansys.simai.core.errors.MultipleErrors`, whose ``exceptions`` attribute lists the
errors.

Send all requests before you read any result
--------------------------------------------

When you read the data of an object that isn't ready, PySimAI waits for it. For example,
``prediction.post.global_coefficients().data`` blocks until the postprocessing is done. If a loop
reads each result right after its request, the requests run one after the other:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")
    simai_client.set_current_workspace("<your_workspace_name>")

    for geometry in simai_client.geometries.list():
        for speed in [5.9, 5.10, 5.11]:
            prediction = geometry.run_prediction(scalars={"<your_scalar_name>": speed})
            # Reading the data blocks until the computation is done
            print(prediction.post.global_coefficients().data)

To run many computations in parallel on the server, send all the requests first, then wait, then
read the results, as in the complete script.

Expected result when you wait for objects computed by the server
----------------------------------------------------------------

The complete script prints the global coefficients of each prediction that succeeded, and one
message for each prediction or postprocessing that failed.

Errors when you wait for objects computed by the server
-------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The server failed to compute the object.
     - Read ``failure_reason`` on the object.
   * - :class:`~ansys.simai.core.errors.MultipleErrors`
     - Several computations failed during ``SimAIClient.wait()``.
     - Read each error in the ``exceptions`` attribute.

More about how to wait for objects computed by the server
---------------------------------------------------------

- :meth:`Prediction.wait() <ansys.simai.core.data.predictions.Prediction.wait>`
- :meth:`SimAIClient.wait() <ansys.simai.core.client.SimAIClient.wait>`
- :doc:`/user-guide/common-tasks/handle-errors`
- :doc:`/user-guide/simai-models/run-predictions`
