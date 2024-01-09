Training
========

.. _training:

.. note::

   Training is still experimental and subject to API changes.

Before you can use the solver, you must train the SimAI solution on your prediction
data. First, you upload your prediction data into a global pool of
:class:`training data<ansys.simai.core.data.training_data.TrainingData>` instances
and then assign this data to different :class:`Projects<ansys.simai.core.data.projects.Project>`
instances, which you configure for training your model.

Train on prediction data
========================

#. Create a :class:`~ansys.simai.core.client.SimAIClient` instance::

     import ansys.simai.core

     simai = ansys.simai.core.SimAIClient()

   You are prompted for your credentials.

   If desired, you can create an instance using a configuration file. For more
   information, see :ref:`configuration`.

#. Upload your prediction data by creating a
   :class:`training data<ansys.simai.core.data.training_data.TrainingData>` instance
   and then loading your files into it::

     td = simai.training_data.create("my-first-data")
     td.upload_folder("/path/to/folder/where/files/are/stored")

#. Create a project::

     project = simai.projects.create("my-first-project")

#. Assign the created training data to your project::

     td.add_to_project(project)

Once you have training data in your project, you can use the web app to
train a model.

Learn more
==========

For more information on the actions available to you, see :ref:`training_data`,
:ref:`training_data_parts`, and :ref:`projects`.
