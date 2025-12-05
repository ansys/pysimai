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

""".. _ref_build_model:

Building a Generative Design Model
================================================

This example demonstrates how to configure a Generative Design model, start the model training process, and monitor the build progress.

Before you begin
-------------------------------------------

- Complete ":ref:`ref_create_project_upload_data`" to create a project with training data.
- Ensure all training data in your project are ready (processed successfully).

"""

###############################################################################
# Import necessary libraries
# -------------------------------------------

import ansys.simai.core as asc
from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration

###############################################################################
# Configure your settings
# -------------------------------------------
# Update these variables with your specific settings:

ORGANIZATION = "my_organization"  # Replace with your organization name
PROJECT_NAME = "new-bracket-project"  # Replace with your project name
NB_LATENT_PARAMS = 15  # Number of latent parameters (2-256)
BUILD_PRESET = "default"  # Options: "debug", "short", "default", "long"

###############################################################################
# The ``BUILD_PRESET`` options correspond to:
#
# - ``"debug"``: Fast training for testing (very few epochs).
# - ``"short"``: Quick training with reduced accuracy.
# - ``"default"``: Balanced training time and quality.
# - ``"long"``: Longer training for best quality.


###############################################################################
# Initialize the client and get the project
# -------------------------------------------
# Connect to the instance:

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai

###############################################################################
# Retrieve the project by name:

project = geomai_client.projects.get(name=PROJECT_NAME)
print(f"Using project: {project.name}")

###############################################################################
# Verify project data are ready
# -------------------------------------------
# Before building a model, ensure all training data are processed:

project_data = project.data()
ready_data = [data for data in project_data if data.is_ready]
print(f"Project has {len(ready_data)}/{len(project_data)} ready training data")

if len(ready_data) < len(project_data):
    print("Warning: Some training data are not ready. Model may fail to build.")

###############################################################################
# Configure the model
# -------------------------------------------
# To define the configuration for your model, you can either specify the build preset or the number
# of epochs.
# To do so, instead of ``build_preset``, you can specify the number of epochs directly. Example: ``nb_epochs=100``.
#
# The number of latent parameters defines the complexity of the model's latent space; start with a small number (e.g., 10) and adjust based on your needs.


configuration = GeomAIModelConfiguration(
    build_preset=BUILD_PRESET,
    nb_latent_param=NB_LATENT_PARAMS,  # Must be between 2 and 256
)

###############################################################################
# Build the model
# -------------------------------------------
# Start the model training process:

model = geomai_client.models.build(project, configuration)
print(f"Started build for model {model.id}")

###############################################################################
# Wait for model training to complete
# -------------------------------------------
# Monitor the training process and handle completion:

print("Waiting for model training to complete (this may take a while)...")
while not model.wait(timeout=60):  # Check every 60 seconds
    print(f"Model {model.id} is still training...")

if model.has_failed:
    print(f"Model training failed: {model.failure_reason}")
else:
    print(f"Model {model.id} trained successfully and is ready to use.")

###############################################################################
# Next steps
# -------------------------------------------
# Once your model is trained, you can:
#
# - Generate random geometries: :ref:`ref_generate_random_geometries`
# - Interpolate between geometries: :ref:`ref_interpolate_geometries`
