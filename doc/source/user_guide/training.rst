Building a model
========

.. _building a model:

.. note::

   Building a model with PySimAI is still experimental and subject to API changes.

   Rebuilding a model using the last configuration of a project is supported for models created
   after v0.1.5 (April 15, 2024).

SimAI allows you to build AI models on your simulation data. This first step is to upload your simulation data
into a global pool of :class:`training data<ansys.simai.core.data.training_data.TrainingData>` instances
and then assign this data to different :class:`Project<ansys.simai.core.data.projects.Project>`
instances, which you configure in order to build your model.

Building an AI model on your simulation data
========================

#. Create a :class:`~ansys.simai.core.client.SimAIClient` instance::

     import ansys.simai.core

     simai = ansys.simai.core.SimAIClient()

   You are prompted for your credentials.

   If desired, you can create an instance using a configuration file. For more
   information, see :ref:`configuration`.

#. Upload your prediction data by creating a
   :class:`TrainingData<ansys.simai.core.data.training_data.TrainingData>` instance
   and then loading your files into it::

     td = simai.training_data.create("my-first-data")
     td.upload_folder("/path/to/folder/where/files/are/stored")

#. Create a project::

     project = simai.projects.create("my-first-project")

#. Assign the created training data to your project::

     td.add_to_project(project)

Learn more
==========

For more information on the actions available to you, see :ref:`training_data`,
:ref:`training_data_parts`, and :ref:`projects`.
