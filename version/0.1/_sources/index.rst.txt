.. _index:

.. toctree::
   :maxdepth: 1
   :hidden:

   user_guide
   api_reference

PySimAI documentation
=====================

Release v\ |version| (:ref:`Changelog <changelog>`)

PySimAI is part of the `PyAnsys <https://docs.pyansys.com>`_ ecosystem that allows you to use SimAI within
a Python environment of your choice in conjunction with other PyAnsys libraries and external Python
libraries. With PySimAI, you can manage and access your data on the platform from within Python apps and
scripts.

Requirements
============

PySimAI requires Python 3.9 or later.

Installation
================

Install PySimAI with this command:

.. code-block:: bash

   pip install ansys-simai-core --upgrade

Use this same command every time you want to update PySimAI.

.. _getting_started:

Getting started
===============

The :class:`~ansys.simai.core.client.SimAIClient` class is the core of PySimAI.
All operations are made through it.

.. code-block:: python

   from ansys.simai.core import SimAIClient

   simai = SimAIClient()

You are prompted for your credentials.

.. note::
   You can also start a :class:`~ansys.simai.core.client.SimAIClient` instance
   from a configuration file. For more information, see :ref:`configuration`.

Once the :class:`~ansys.simai.core.client.SimAIClient` class is started,
you use the :meth:`~ansys.simai.core.data.geometries.GeometryDirectory.upload`
method to load a geometry:

.. code-block:: python

   geometry = simai.geometries.upload(
       "/path-to-my-stl-file.stl",
       name="A name for my geometry",
       metadata={
           "geom_property_1": "A",
           "geom_property_2": 1.2,
       },
   )

To learn more about what geometries are and how they should be formatted, see
:ref:`geometries`.

You use the :meth:`~ansys.simai.core.data.selections.Selection.run_predictions`
method to run a prediction on the geometry:

.. code-block:: python

   prediction = geometry.run_prediction(boundary_conditions=dict(Vx=10.0))

The :class:`PredictionPostProcessing<ansys.simai.core.data.post_processings.PredictionPostProcessings>`
class provides for postprocessing and analzing your prediction data.

You use the :attr:`~ansys.simai.core.data.predictions.Prediction.post`
attribute of the prediction to run the postprocessing and access its data:

.. code-block:: python

   # Run postprocessing
   global_coefficients = prediction.post.global_coefficients()
   # Access its data
   print(global_coefficients.data)

.. note::

   Depending on the postprocessing, the :attr:`~ansys.simai.core.data.post_processings.PostProcessing.data`
   attribute returns either a dictionary or a :class:`~ansys.simai.core.data.post_processings.DownloadableResult`
   object.

For more information, see :ref:`post_processings`.

You're all set. You can now learn about more advanced concepts, such as starting the
SimAI client from a :ref:`configuration file<configuration>`, :ref:`exploring your data<data_exploration>`,
and :ref:`best practices<best_practices>`.

To explore the functions and methods available to you, see :ref:`api_reference`.
