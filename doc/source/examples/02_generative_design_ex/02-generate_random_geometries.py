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

""".. _ref_generate_random_geometries:

Generate random geometries with a GeomAI model
==============================================

This example generates geometries with a GeomAI model from random latent parameters
and downloads them as VTP files.

Prerequisites to generate random geometries with a GeomAI model
---------------------------------------------------------------

- Complete ":ref:`ref_build_model`" to build a GeomAI model.
- Make sure that the model build completed successfully.

"""

###############################################################################
# Import the classes to generate geometries with a GeomAI model
# -------------------------------------------------------------

import os
import random

import ansys.simai.core as asc
from ansys.simai.core.data.geomai.predictions import GeomAIPrediction, GeomAIPredictionConfiguration
from ansys.simai.core.errors import ProcessingError

###############################################################################
# Set the workspace and output folder for the random geometries
# -------------------------------------------------------------
# Replace these values with your own:

ORGANIZATION = "my_organization"  # Replace with your organization name
PROJECT_NAME = "new-bracket-project"  # Replace with your project name
WORKSPACE_NAME = "new-bracket-project #1"  # Typically "{PROJECT_NAME} #{number}"
OUTPUT_DIR = "random_geometries"  # Directory to save generated geometries
NUM_GEOMETRIES = 5  # Number of random geometries to generate

###############################################################################
# Get the workspace of the GeomAI model
# -------------------------------------
# Connect to Ansys SimAI:

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai

###############################################################################
# Get the workspace of the built GeomAI model by its name:

workspace = geomai_client.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")


###############################################################################
# Get the number of latent parameters of the GeomAI model
# -------------------------------------------------------
# The number of latent parameters is set in the GeomAI model configuration
# (``nb_latent_param``) before the model build:

latent_dict = workspace.get_latent_parameters()

nb_latent_params = len(next(iter(latent_dict.values())))
print(f"Workspace uses {nb_latent_params} latent parameters")

###############################################################################
# Create the folder for the random geometries
# -------------------------------------------
# Create a folder to save the generated geometries:

output_dir = os.path.join(OUTPUT_DIR, workspace.name)
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory: {output_dir}")

###############################################################################
# Run GeomAI model predictions with random latent parameters
# ----------------------------------------------------------
# Generate geometries by creating random latent parameters.
# Each latent parameter is randomly sampled from a standard normal distribution.

predictions: list[GeomAIPrediction] = []

print(f"\nGenerating {NUM_GEOMETRIES} random geometries...")
for i in range(NUM_GEOMETRIES):
    # Generate random latent parameters (from standard normal distribution)
    latent_params = [random.gauss(0, 1) for _ in range(nb_latent_params)]

    # Create prediction configuration
    config = GeomAIPredictionConfiguration(
        latent_params=latent_params,
    )

    # Run the prediction
    prediction = geomai_client.predictions.run(config, workspace)
    print(f"Prediction {i + 1}/{NUM_GEOMETRIES}: {prediction.id} started...")
    predictions.append(prediction)


###############################################################################
# Download the random geometries
# ------------------------------
# Wait for each prediction, then download the generated geometry.

for i, prediction in enumerate(predictions):
    # wait() returns False on timeout and raises ProcessingError if the prediction fails.
    try:
        if not prediction.wait(timeout=600):  # Wait up to 10 minutes
            print(f"✗ Prediction {i + 1} timed out")
            continue
    except ProcessingError:
        print(f"✗ Prediction {i + 1} failed: {prediction.failure_reason}")
        continue

    # Download the generated geometry
    output_path = os.path.join(output_dir, f"random_{i + 1:02d}_{prediction.id}.vtp")
    geomai_client.predictions.download(prediction.id, output_path)
    print(f"✓ Saved geometry to {output_path}")

###############################################################################
# You can use the downloaded VTP files for:
#
# - Visualization in your usual solver.
# - Training data or predictions for a SimAI model.
# - Further analysis and postprocessing.

###############################################################################
# Improve random geometries generated by a GeomAI model
# -----------------------------------------------------
#
# - Latent parameters typically range from -3 to +3 for meaningful results.
# - A higher ``resolution`` in ``GeomAIPredictionConfiguration`` captures finer details,
#   but it also increases the prediction time.
# - Increase the timeout for complex geometries.
# - To sample in a realistic range, compute the minimum and maximum of each latent
#   parameter over the training geometries returned by ``workspace.get_latent_parameters()``.

###############################################################################
# Control the geometries generated by a GeomAI model
# --------------------------------------------------
# To generate geometries with more control, interpolate between existing
# geometries: :ref:`ref_interpolate_geometries`.
#
# For the complete task, see :doc:`/user-guide/geomai-models/generate-geometries`.
