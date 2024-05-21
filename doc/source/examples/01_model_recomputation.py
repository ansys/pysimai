"""
.. _ref_last_config_new_build:

Model recomputation
-------------------------

This example demonstrates how to relaunch a model build using the latest 
model configuration in a same project.

"""

###############################################################################
# Import necessary libraries

import ansys.simai.core as asc

simai = asc.from_config()

###############################################################################
# Get the project from the server.
my_project = simai.projects.get(name="old-ps")

###############################################################################
# Get the latest model configuration of the project.
last_build_config = my_project.last_model_configuration

###############################################################################
# Verify that the project meets the requirements for training (model building).
is_trainable_check = my_project.is_trainable()

###############################################################################
# If the project met the requirements, launch a model build.
# Otherwise, print the reasons the project does not meet the requirements.
if is_trainable_check:
    new_model = simai.models.build(last_build_config)
else:
    print(is_trainable_check.reason)

