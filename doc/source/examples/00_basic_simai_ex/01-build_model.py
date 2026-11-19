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

""".. _ref_basic_build_model:

Build a SimAI model
===================

This example configures a SimAI model with model inputs, model outputs, global coefficients,
and a Domain of Analysis (DoA), then starts the model build.

Prerequisites to build a SimAI model
------------------------------------

- Complete ":ref:`ref_basic_create_project_upload_data`" to create a project with training data.
- Make sure that all training data points in the project are ready (processed successfully).
- Know the names of the surfaces and scalars in your training data.
- Decide which global coefficients you want to calculate.

"""

###############################################################################
# Import the classes to build a SimAI model
# -----------------------------------------

import ansys.simai.core as asc
from ansys.simai.core.data.model_configuration import (
    DomainOfAnalysis,
    GlobalCoefficientDefinition,
    ModelConfiguration,
    ModelInput,
    ModelOutput,
)

###############################################################################
# Set the project and organization names for the SimAI model build
# ----------------------------------------------------------------
# Replace these values with your own:

ORGANIZATION_NAME = "<your_organization>"  # Replace with your organization name
PROJECT_NAME = "<your_project_name>"  # Replace with your project name

###############################################################################
# Get the project that contains the SimAI model training data
# -----------------------------------------------------------
# Connect to Ansys SimAI:

simai_client = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Retrieve the project by name:

project = simai_client.projects.get(name=PROJECT_NAME)
print(f"Using existing project: {PROJECT_NAME}")

###############################################################################
# Define the model inputs of the SimAI model
# ------------------------------------------
# Define the surfaces and scalars that the SimAI model uses as model inputs.
# Replace the placeholder names with the actual names from your training data:

model_input = ModelInput(
    surface=["<your_surface_name>"],  # List of surface names to use as input
    scalars=["<your_scalar_name>"],  # List of scalar names
)

###############################################################################
# Define the model outputs of the SimAI model
# -------------------------------------------
# Define the surfaces that the SimAI model predicts.
# These are typically the same surfaces as the inputs, but you can specify different ones:

model_output = ModelOutput(
    surface=["<your_surface_name>"],  # List of surface names to predict
)

###############################################################################
# Define the global coefficients of the SimAI model
# -------------------------------------------------
#
# Global coefficients are scalar values calculated from the prediction results.
# They can be used to extract key performance indicators from your simulations.
#
# This example calculates the integral of the ``Pressure`` field.
# You can define multiple global coefficients with different formulas.
#
# Available locations: ``"points"`` or ``"cells"``.

global_coefficients = [
    GlobalCoefficientDefinition(
        name="<your_global_coefficient_name>",  # Name for this global coefficient
        formula="integral(Pressure)",  # Formula to calculate the global coefficient value
        gc_location="points",  # Calculate at points (or at "cells")
    )
]

###############################################################################
# Define the Domain of Analysis (DoA) of the SimAI model
# ------------------------------------------------------
# The Domain of Analysis (DoA) sets the spatial extent that the SimAI model analyzes.
# Each dimension is either absolute or relative to the minimum, maximum, or center
# of the geometry.
#
# Format: ``(position, value, length)``
#
# - ``position``: ``"relative_to_min"``, ``"relative_to_max"``, ``"relative_to_center"`` or ``"absolute"``.
# - ``value``: distance of the anchor from the position.
# - ``length``: length of the Domain of Analysis along the axis.
#
# To find appropriate values, analyze your training data in Ansys SimAI.

doa = DomainOfAnalysis(
    length=("relative_to_min", 0.102, 1.219),  # (position, value, length)
    width=("relative_to_min", 0.102, 1.219),  # (position, value, length)
    height=("relative_to_min", 0.134, 1.61),  # (position, value, length)
)

###############################################################################
# Create the model configuration of the SimAI model
# -------------------------------------------------
# Combine all the configuration elements into a ``ModelConfiguration`` object.
#
# The ``build_preset`` parameter sets the build setting and the build duration:
#
# - ``debug``: debug mode, less than 30 minutes, 4 training data points. Not for production.
# - ``1_day``: production mode, build duration of up to 24 hours.
# - ``2_days``: production mode, build duration of up to 48 hours (default).
# - ``7_days``: production mode, build duration of up to 7 days.


mdl_conf = ModelConfiguration(
    project=project,  # Project containing the training data
    build_preset="1_day",  # Production build with a build duration of up to 24 hours
    input=model_input,  # Model input configuration
    output=model_output,  # Model output configuration
    global_coefficients=global_coefficients,  # Global coefficient definitions
    domain_of_analysis=doa,  # Domain of analysis bounds
)

###############################################################################
# Check that the project is trainable and build the SimAI model
# -------------------------------------------------------------
# Before the model build, check that the project meets all requirements:

if project.is_trainable():
    print("Project is trainable. Starting model build...")
    new_model = simai_client.models.build(mdl_conf)
    print(f"Model build started with ID: {new_model.id}")
    print(
        "The model build takes some time. You can monitor its progress in Ansys SimAI."
    )
else:
    print("Project is not trainable. Please check the following:")
    print("- All training data must be processed successfully.")
    print("- The project must have enough training data.")
    print("- All required surfaces and scalars must exist in the training data.")

###############################################################################
# Run predictions with the built SimAI model
# ------------------------------------------
# When the model build is complete, you can:
#
# - Run predictions on new geometries: :ref:`ref_basic_run_predictions`.
# - Evaluate the SimAI model: :doc:`/user-guide/simai-models/evaluate-a-model`.
#
# For the complete tasks, see :doc:`/user-guide/simai-models/configure-a-model` and
# :doc:`/user-guide/simai-models/build-a-model`.
