.. _best_practices:

Best Practices
==============

Asynchronicity
--------------

While the SDK doesn't use async/await mechanics, it is somewhat asynchronous in nature:
uploading geometries is a blocking method but running a prediction or a post-processing will
return the created object immediately before the result is computed on the servers or available locally.
This behavior makes it possible to request multiple computations to be ran on the
SimAI platform without waiting for any of the data to be available.

To wait for an object to be fully available, you can call the ``wait()`` method on the object
(e.g. :meth:`Prediction.wait()<ansys.simai.core.data.predictions.Prediction.wait>`) or you can call the global
:meth:`SimAIClient.wait()<ansys.simai.core.client.SimAIClient.wait>` method to wait for all requests to be complete.
Alternatively you can try to access the object's data in which case the SDK will automatically wait for the data to be ready if needed.

Because of this behavior, it is recommended when running a large number of computations to send all the
requests before accessing any of the data.

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
           # Since we're accessing the data, this will wait for the computation to finish
           coeffs = pred.post.global_coefficients().data
           # do something with the data
           print(coeffs)

In the previous example, the predictions and post-processings will be requested sequentially, waiting for the data
to be available and used before requesting the next one.
Thus a more efficient way would be as follows:

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
           # Since we're not accessing the data, this will not block
           pred.post.global_coefficients()
           predictions.append(pred)

   simai.wait()  # Wait for all objects requested locally to be complete
   for pred in predictions:
       # do something with the data
       print(pred.post.global_coefficients().data)

In this example, all the predictions and post-processings are requested right away and the
data crunching will happen once all of it is available.
