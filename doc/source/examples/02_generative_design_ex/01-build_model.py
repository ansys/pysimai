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

""".. _ref_build_model:

Build a GeomAI model
====================

This example configures a GeomAI model, starts the model build, and waits for the
model build to finish.

Prerequisites to build a GeomAI model
-------------------------------------

- Complete ":ref:`ref_create_project_upload_data`" to create a project with training data.
- Make sure that all training data points in the project are ready (processed successfully).

"""

###############################################################################
# Import the classes to build a GeomAI model
# ------------------------------------------

import ansys.simai.core as asc
from ansys.simai.core.errors import ProcessingError
from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration

###############################################################################
# Set the project and build preset for the GeomAI model
# -----------------------------------------------------
# Replace these values with your own:

ORGANIZATION = "my_organization"  # Replace with your organization name
PROJECT_NAME = "new-bracket-project"  # Replace with your project name
BUILD_PRESET = "default"  # Options: "debug", "short", "default", "long"

###############################################################################
# The ``BUILD_PRESET`` options correspond to:
#
# - ``"debug"``: quick test to confirm that everything runs (only four training data
#   points and one epoch). About 4 minutes plus 15 seconds per geometry.
# - ``"short"``: fast training with reduced accuracy. About 45 minutes plus 15 seconds
#   per geometry.
# - ``"default"``: balanced training time and quality. About 3 hours plus 15 seconds
#   per geometry.
# - ``"long"``: longer training for best quality. About 15 hours plus 15 seconds
#   per geometry.


###############################################################################
# Get the project of the GeomAI model
# -----------------------------------
# Connect to Ansys SimAI:

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai

###############################################################################
# Retrieve the project by name:

project = geomai_client.projects.get(name=PROJECT_NAME)
print(f"Using project: {project.name}")

###############################################################################
# Check that the GeomAI model training data is ready
# --------------------------------------------------
# Before the model build, make sure that all training data points are processed:

project_data = project.list_training_data()
ready_data = [data for data in project_data if data.is_ready]
print(f"Project has {len(ready_data)}/{len(project_data)} ready training data")

if len(ready_data) < len(project_data):
    print("Warning: Some training data are not ready. Model may fail to build.")

###############################################################################
# Configure the GeomAI model
# --------------------------
# Set either ``build_preset`` or ``nb_epochs`` in the GeomAI model configuration,
# not both. For example, to set the number of epochs directly, replace
# ``build_preset=BUILD_PRESET`` with ``nb_epochs=100``.

configuration = GeomAIModelConfiguration(
    build_preset=BUILD_PRESET,
)

###############################################################################
# Start the GeomAI model build
# ----------------------------
# Start the model build:

model = geomai_client.models.build(project, configuration)
print(f"Started build for model {model.id}")

###############################################################################
# Wait for the GeomAI model build to finish
# -----------------------------------------
# Check the model build every 60 seconds and handle a failure:

print("Waiting for model training to complete (this may take a while)...")
# wait() returns False on timeout and raises ProcessingError if the build fails.
try:
    while not model.wait(timeout=60):  # Check every 60 seconds
        print(f"Model {model.id} is still training...")
    print(f"Model {model.id} trained successfully and is ready to use.")
except ProcessingError:
    print(f"Model training failed: {model.failure_reason}")

###############################################################################
# Generate geometries with the built GeomAI model
# -----------------------------------------------
# When the model build is complete, you can:
#
# - Generate random geometries: :ref:`ref_generate_random_geometries`.
# - Interpolate between geometries: :ref:`ref_interpolate_geometries`.
# - Project a geometry onto the GeomAI model: :ref:`ref_project_geometries`.
#
# For the complete task, see :doc:`/user-guide/geomai-models/build-a-model`.
