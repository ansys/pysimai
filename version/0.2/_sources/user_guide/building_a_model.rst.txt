Building a model
================

.. _building_a_model:

.. note::

   Building a model with PySimAI is still experimental and subject to API changes.

   Rebuilding a model using the last configuration of a project is supported for models created
   after v0.1.5 (April 15, 2024).

SimAI allows you to build AI models using past simulation data. This first step to building such models is to upload
your simulation data into a global pool of :class:`training data<ansys.simai.core.data.training_data.TrainingData>` instances.
Then, you assign the imported data to different :class:`Project<ansys.simai.core.data.projects.Project>` instances,
which you will eventually configure in order to build your AI model.

Create a project and upload data
--------------------------------

#. Create a :class:`~ansys.simai.core.client.SimAIClient` instance::

     import ansys.simai.core

     simai = ansys.simai.core.SimAIClient()

   You are prompted for your credentials.

   If desired, you can create an instance using a configuration file. For more
   information, see :ref:`configuration`.

#. Create a
   :class:`TrainingData<ansys.simai.core.data.training_data.TrainingData>` instance
   and upload your simulation data into it::

     td = simai.training_data.create("my-first-data")
     td.upload_folder("/path/to/folder/where/files/are/stored")

#. Create a project::

     project = simai.projects.create("my-first-project")

#. Associate the created training data with the created project::

     td.add_to_project(project)

Your project is created and your simulation data is associated with it. You can now configure and build your AI model.

Configure and build the model
-----------------------------

#.   Import the modules related to model building::

          from ansys.simai.core.data.model_configuration import (
               DomainOfAnalysis,
               ModelConfiguration,
               ModelInput,
               ModelOutput,
          )

#.   Set the inputs (:class:`ModelInput<ansys.simai.core.data.model_configuration.ModelInput>`) and outputs (:class:`ModelOutput<ansys.simai.core.data.model_configuration.ModelOutput>`) of the model::

          model_input = ModelInput(surface=["wallShearStress"], boundary_conditions=["Vx"])

          model_output = ModelOutput(surface=["alpha.water"], volume=["p", "p_rgh"])

#.   Set the Global Coefficients::

          global_coefficients = [('min("alpha.water")', "minalpha")]

#.   Set the Domain of Analysis of the model using the :class:`DomainOfAnalysis<ansys.simai.core.data.model_configuration.DomainOfAnalysis>` instance::

          doa = DomainOfAnalysis(
               length=("relative_to_min", 15.321, 183.847),
               width=("relative_to_min", 1.034, 12.414),
               height=("relative_to_min", 2.046, 24.555),
          )


#.   Configure the model using the :class:`ModelConfiguration<ansys.simai.core.data.model_configuration.ModelConfiguration>` instance::

          mdl_conf = ModelConfiguration(
               project=project,                             # project of the model configuration
               build_preset="debug",                        # duration of the build
               build_on_top=False,                          # build on top of previous model
               input=model_input,                           # model input
               output=model_output,                         # model output
               global_coefficients=global_coefficients,     # Global Coefficients
               domain_of_analysis=doa                       # Domain of Analysis
          )

#.   Verify if the project meets the requirements for training and launch a build::

          if project.is_trainable():
               new_model = simai.models.build(mdl_conf)

Your AI model is configured and building.

Learn more
----------

For more information on the actions available to you, see :ref:`training_data`,
:ref:`training_data_parts`, :ref:`projects`, :ref:`model_configuration`, and :ref:`models`
