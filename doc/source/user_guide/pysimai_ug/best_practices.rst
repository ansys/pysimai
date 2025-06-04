.. _best_practices:

Best practices
==============

Asynchronicity
--------------

While the SimAI client doesn't use async/await mechanics, it is somewhat asynchronous in nature.
While uploading geometries is a blocking method, running a prediction or a postprocessing returns
the created object immediately, before the result is computed on the servers or available locally.
This behavior makes it possible to request that multiple computations be run on the SimAI platform
without waiting for any of the data to be available.

To wait for an object to be fully available, you can call the ``wait()`` method on the object.
For example, you can call the :meth:`Prediction.wait()<ansys.simai.core.data.predictions.Prediction.wait>`
method on a prediction. Or, you can call the global :meth:`SimAIClient.wait()<ansys.simai.core.client.SimAIClient.wait>`
method to wait for all requests to complete.

Alternatively, you can try to access the object's data, in which case the SimAI client automatically
waits for the data to be ready if needed. Because of this behavior, when running a large number of
computations, you should send all requests before accessing any of the data.

This example requests the predictions and postprocessings sequentially, which requires waiting
for the data to be available and used before requesting the next one.

.. code-block:: python
   :name: sequential-way

   import ansys.simai.core

   simai = ansys.simai.core.from_config()
   speeds = [5.9, 5.10, 5.11]

   for geom in simai.geometries.list():
       for vx in speeds:
           # Run prediction
           pred = geom.run_prediction(Vx=vx)
           # Request global coefficients postprocessing
           # Because you are accessing the data, you must wait for the computation to finish
           coeffs = pred.post.global_coefficients().data
           # do something with the data
           print(coeffs)


This more efficient example requests all the predictions and postprocessings right away
and then processes the data once they are all available.

.. code-block:: python
   :name: requests-first

   import ansys.simai.core

   simai = ansys.simai.core.from_config()
   speeds = [5.9, 5.10, 5.11]
   predictions = []

   for geom in simai.geometries.list():
       for vx in speeds:
           # Run prediction
           pred = geom.run_prediction(Vx=vx)
           # Request global coefficients postprocessing
           # Because you are not accessing the data, you are not blocked
           pred.post.global_coefficients()
           predictions.append(pred)

   simai.wait()  # Wait for all objects requested locally to be complete
   for pred in predictions:
       # do something with the data
       print(pred.post.global_coefficients().data)

