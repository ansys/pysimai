.. _index:

.. toctree::
   :maxdepth: 1
   :hidden:

   user_guide
   api_reference

PySimAI documentation
=====================

Release v\ |version| (:ref:`Changelog <changelog>`)

The PySimAI library is a Python library for the Ansys SimAI API.
With it you can manage and access your data on the platform from within Python applications and scripts.

What is PySimAI ?
=================

PySimAI is part of the `PyAnsys <https://docs.pyansys.com>`_ ecosystem that let's you use SimAI within a Python environment of your choice in conjunction with other PyAnsys libraries and external Python libraries.

Install
=======

PySimAI requires **Python >= 3.9**

SDK Installation
++++++++++++++++

Install the SDK with the following command:

.. code-block:: bash

   pip install ansys-simai-core --upgrade

This same command can be used every time you want to update the PySimAI library.

Getting started
===============

The :class:`~ansys.simai.core.client.SimAIClient` is the core of the SDK, all operations are made through it.

.. code-block:: python

   from ansys.simai.core import SimAIClient

   simai = SimAIClient()

You will be prompted for your credentials.
Alternative ways to authenticate are described in the :ref:`configuration section<configuration>`.

Using the :class:`~ansys.simai.core.client.SimAIClient`,
you can now :meth:`~ansys.simai.core.data.geometries.GeometryDirectory.upload` your first geometry.

.. code-block:: python

   geometry = simai.geometries.upload(
       "/path-to-my-stl-file.stl",
       name="A name for my geometry",
       metadata={
           "geom_property_1": "A",
           "geom_property_2": 1.2,
       },
   )

To learn more about what geometries are and how they should be formatted, see the :ref:`geometry_format` section.

You can then run a prediction on your geometry:

.. code-block:: python

   prediction = geometry.run_prediction(boundary_conditions=dict(Vx=10.0))

You can now analyse the prediction by :class:`post-processing<ansys.simai.core.data.post_processings.PredictionPostProcessings>` it.

Run or get a post-processing through the :attr:`~ansys.simai.core.data.predictions.Prediction.post` attribute of the prediction.

.. code-block:: python

   # Run the post-processing
   global_coefficients = prediction.post.global_coefficients()
   # Access its data
   print(global_coefficients.data)

.. note::

   Depending on the post-processing :attr:`~ansys.simai.core.data.post_processings.PostProcessing.data`
   will return a dict or a :class:`~ansys.simai.core.data.post_processings.DownloadableResult`.


You can learn more about the available post-processings :ref:`here<post_processings>`.

You're all set: you can now look into more advanced concepts like :ref:`configuring your SDK<configuration>`,
:ref:`data exploration<data_exploration>` or :ref:`best practices<best_practices>`.
If you want to explore the functions and methods available to you in the SDK,
you can head over to the :ref:`API reference<api_reference>` section.
