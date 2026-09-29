""".. _ref_model_configuration_reuse:

Model configuration reuse
=========================

This example demonstrates how to retrieve the latest model configuration
of a project and use it to launch a model build in another project.

"""

###############################################################################
# Import necessary libraries
# --------------------------

import ansys.simai.core as asc

simai = asc.from_config()

###############################################################################
# Create a project and allocate training data
# -------------------------------------------
# Define the project name.
new_project_name = "new-project"

###############################################################################
# Create the project.
new_project = simai.projects.create(new_project_name)

###############################################################################
# Set the names of the data samples to be associated with the created project.
training_samples_name = [
    "TrainingData_001",
    "TrainingData_002",
    "TrainingData_003",
    "TrainingData_004",
]

###############################################################################
# Retrieve the desired training data samples and associate them with
# the new project.
for td_name in training_samples_name:
    filt = {"name": td_name}
    td = simai.training_data.list(filters=filt)
    td[0].add_to_project(new_project)

###############################################################################
# Select a model configuration and associate it with the newly created project
# ----------------------------------------------------------------------------
# Retrieve the model configuration from another project that you wish to reuse.
old_project = "old-ps"
my_project = simai.projects.get(name=old_project)

last_build_config = my_project.last_model_configuration

###############################################################################
# If the new project meets the requirements for training, associate
# the project's ID with the configuration and launch a model build.
if new_project.is_trainable():
    # Assign the new project's ID to the configuration to transfer the
    # configuration from the old project to the new one
    last_build_config.project_id = new_project.id

    # Launch a model build for the new project
    new_model = simai.models.build(last_build_config)
