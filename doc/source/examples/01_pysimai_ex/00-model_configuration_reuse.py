# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""".. _ref_model_configuration_reuse:

Reuse a model configuration to build a SimAI model in another project
=====================================================================

This example gets the latest model configuration of a SimAI model project and uses it
to start a SimAI model build in another project.

"""

###############################################################################
# Import PySimAI and create the client to reuse a model configuration
# -------------------------------------------------------------------

import ansys.simai.core as asc

simai_client = asc.from_config()

###############################################################################
# Create a project and add training data points to it
# ---------------------------------------------------
# Define the project name.
new_project_name = "new-project"

###############################################################################
# Create the project.
new_project = simai_client.projects.create(new_project_name)

###############################################################################
# Set the names of the training data points to add to the new project.
training_samples_name = [
    "TrainingData_001",
    "TrainingData_002",
    "TrainingData_003",
    "TrainingData_004",
]

###############################################################################
# Get each training data point and add it to the new project.
for td_name in training_samples_name:
    filt = {"name": td_name}
    td = simai_client.training_data.list(filters=filt)
    td[0].add_to_project(new_project)

###############################################################################
# Copy the model configuration of another project to the new project
# ------------------------------------------------------------------
# Get the latest model configuration of the project that you want to reuse.
old_project = "old-ps"
my_project = simai_client.projects.get(name=old_project)

last_build_config = my_project.last_model_configuration

###############################################################################
# If the new project meets the requirements for a model build, assign the
# new project to the model configuration and start a SimAI model build.
if new_project.is_trainable():
    # Assign the new project to the configuration to transfer the
    # configuration from the old project to the new one
    last_build_config.project = new_project

    # Start a SimAI model build for the new project
    new_model = simai_client.models.build(last_build_config)

###############################################################################
# Learn more about SimAI model configurations
# -------------------------------------------
# For the complete tasks, see :doc:`/user-guide/simai-models/configure-a-model` and
# :doc:`/user-guide/simai-models/build-a-model`.
