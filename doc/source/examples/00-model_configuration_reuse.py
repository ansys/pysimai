"""
.. _ref_model_configuration_reuse:

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
    "0001_L212.2_B32.2_T13.8_XBOW0.2_XSKEG0.3_BS_10.8_SINK_-8.3_TRIM_0.0 aybyegxw",
    "0001_L72_B10.8_T4.725_XBOW0.2_XSKEG0.3_BS_13.1_SINK_-2.9_TRIM_0.0 nabgeexq",
    "0001_HMBC_1_CB_84_BS_10.0_SINK_-6.4_TRIM_0.0 o2x6g5zm",
    "0001_HBC_1_CB_84_BS_8.0_SINK_-4.8_TRIM_0.0 63b3jwxw",
]

###############################################################################
# Retrieve all the available data samples and associate them with the new
# project based on the provided list.
all_training_data = simai.training_data.list()

training_data = [
    ts.add_to_project(new_project.id)
    for ts in all_training_data
    if ts.name in training_samples_name
]

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
