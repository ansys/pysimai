# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

""".. _ref_basic_build_model:

Building a SimAI Model
============================================

This example demonstrates how to configure a SimAI model with inputs, outputs, global coefficients,
and domain of analysis, then start the model training process.

Before you begin
-------------------------------------------

- Complete ":ref:`ref_basic_create_project_upload_data`" to create a project with training data.
- Ensure all training data in your project are ready (processed successfully).
- Know the names of surfaces and boundary conditions in your training data.
- Determine which global coefficients you want to compute.

"""

###############################################################################
# Import necessary libraries
# -------------------------------------------

import ansys.simai.core as asc
from ansys.simai.core.data.model_configuration import (
    DomainOfAnalysis,
    GlobalCoefficientDefinition,
    ModelConfiguration,
    ModelInput,
    ModelOutput,
)

###############################################################################
# Configure your settings
# -------------------------------------------
# Update these variables with your specific settings:

ORGANIZATION_NAME = "<your_organization>"  # Replace with your organization name
PROJECT_NAME = "<your_project_name>"  # Replace with your project name

###############################################################################
# Initialize the client and get the project
# -------------------------------------------
# Connect to SimAI:

simai_client = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Retrieve the project by name:

project = simai_client.projects.get(name=PROJECT_NAME)
print(f"Using existing project: {PROJECT_NAME}")

###############################################################################
# Configure model inputs
# -------------------------------------------
# Define which surfaces and boundary conditions the model will use as inputs.
# Replace the placeholder names with the actual names from your training data:

model_input = ModelInput(
    surface=["<your_surface_name>"],  # List of surface names to use as input
    boundary_conditions=["<your_BC_name>"],  # List of boundary condition names
)

###############################################################################
# Configure model outputs
# -------------------------------------------
# Define which surfaces the model will predict.
# These are typically the same surfaces as the inputs, but you can specify different ones:

model_output = ModelOutput(
    surface=["<your_surface_name>"],  # List of surface names to predict
)

###############################################################################
# Define global coefficients
# -------------------------------------------
#
# Global coefficients are scalar values computed from the prediction results.
# They can be used to extract key performance indicators from your simulations.
#
# In this example, we compute the integral of a field called "Photometric".
# You can define multiple global coefficients with different formulas.
#
# Available locations: ``"points"`` or ``"cells"``.

global_coefficients = [
    GlobalCoefficientDefinition(
        name="<your_global_coefficient_name>",  # Name for this global coefficient
        formula="integral(Photometric)",  # Formula to compute the value
        gc_location="points",  # Compute on points (or "cells")
    )
]

###############################################################################
# Define domain of analysis
# -------------------------------------------
# The domain of analysis specifies the spatial extent that the model will analyze.
# Values can be specified as absolute dimensions or relative to minimum values.
#
# Format: reference_type, min_value, max_value
#
# - ``reference_type``: ``"relative_to_min"``, ``"relative_to_max"``, ``"relative_to_center``" or ``"absolute"``.
# - ``min_value``: minimum dimension value.
# - ``max_value``: maximum dimension value.
#
# You can find appropriate values by analyzing your training data in the SimAI platform.

doa = DomainOfAnalysis(
    length=("relative_to_min", 0.102, 1.219),  # Length bounds
    width=("relative_to_min", 0.102, 1.219),  # Width bounds
    height=("relative_to_min", 0.134, 1.61),  # Height bounds
)

###############################################################################
# Create model configuration
# -------------------------------------------
# Combine all the configuration elements into a ModelConfiguration object.
#
# Build presets determine the training duration:
#
# - ``debug``: Quick training for testing.
# - ``1_day``: Short training.
# - ``2_days``: Standard training (recommended).
# - ``7_days``: Maximum training for best accuracy.


mdl_conf = ModelConfiguration(
    project=project,  # Project containing the training data
    build_preset="1_day",  # Duration of the build
    build_on_top=False,  # Start training from scratch
    input=model_input,  # Model input configuration
    output=model_output,  # Model output configuration
    global_coefficients=global_coefficients,  # Global coefficient definitions
    domain_of_analysis=doa,  # Domain of analysis bounds
)

###############################################################################
# Verify and build the model
# -------------------------------------------
# Before building, check if the project meets all requirements for training:

if project.is_trainable():
    print("Project is trainable. Starting model build...")
    new_model = simai_client.models.build(mdl_conf)
    print(f"Model build started with ID: {new_model.id}")
    print(
        "The model will take some time to train. You can monitor its progress in the SimAI platform."
    )
else:
    print("Project is not trainable. Please check the following:")
    print("- All training data must be processed successfully.")
    print("- The project must have enough training data.")
    print("- All required surfaces and boundary conditions must exist in the training data.")

###############################################################################
# Next steps
# -------------------------------------------
# Once your model is trained, you can:
#
# - Monitor the training progress in the SimAI platform.
# - Run predictions on new geometries: :ref:`ref_basic_run_predictions`.
# - Evaluate model performance using validation data.
