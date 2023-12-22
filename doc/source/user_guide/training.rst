Training
========

.. _training:

.. note::

   The training section is still experimental and subject to API changes.

In order to use the solver, the SimAI solution must first be trained on your prediction data.
Your prediction data is uploaded onto a global pool of :class:`training data<ansys.simai.core.data.training_data.TrainingData>` and can then be assigned to different :class:`projects<ansys.simai.core.data.projects.Project>` where you can configure how to train your model.

Getting started
===============

Create an :class:`~ansys.simai.core.client.SimAIClient` object::

  import ansys.simai.core

  simai = ansys.simai.core.SimAIClient()

You will be prompted for your credentials and for the name of the workspace you want to use.
Alternative ways to authenticate are described :ref:`here<configuration>`.

Start by uploading your prediction data by creating a training data and uploading your files into it::

  td = simai.training_data.create("my-first-data")
  td.upload_folder("/path/to/folder/where/files/are/stored")

You can then create a project::

  project = simai.projects.create("my-first-project")

And assign the created training data to this project::

  td.add_to_project(project)

You can start training a model from the web-app once you have a few training data in your project.

Learn more
==========

Check out the API references for :ref:`training_data`, :ref:`training_data_parts` and :ref:`projects` to learn more about the actions available to you.
