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

""".. _ref_generate_random_geometries:

Generating Random Geometries
==========================================

This tutorial demonstrates how to:

- Connect to a trained GeomAI workspace
- Generate random geometries using random latent parameters
- Download and save the generated geometries

Before you begin
----------------

- Complete ":ref:`ref_build_model`" to train a GeomAI model
- Ensure the model training completed successfully

"""

###############################################################################
# Import necessary libraries
# --------------------------

import json
import os
import random
from typing import Dict, List

import ansys.simai.core
from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration
from ansys.simai.core.data.predictions import Prediction

###############################################################################
# User Configuration
# ------------------
# Update these variables with your specific settings:

ORGANIZATION = "my_organization"  # Replace with your organization name
PROJECT_NAME = "new-bracket-project"  # Replace with your project name
WORKSPACE_NAME = "new-bracket-project #1"  # Typically "{PROJECT_NAME} #{number}"
OUTPUT_DIR = "random_geometries"  # Directory to save generated geometries
NUM_GEOMETRIES = 5  # Number of random geometries to generate
RESOLUTION = (100, 100, 100)  # Output resolution (x, y, z)

###############################################################################
# Initialize the client and get the workspace
# -------------------------------------------
# Connect to GeomAI and retrieve your trained workspace:

simai = ansys.simai.core.SimAIClient(organization=ORGANIZATION)
client = simai.geomai

###############################################################################
# Retrieve the workspace by name:

workspace = client.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")


###############################################################################
# Get the number of latent parameters
# -----------------------------------
# The number of latent parameters is defined during model training:
def get_latent_parameters(workspace) -> Dict[str, List[float]]:
    """Download and load latent parameters for all geometries in the workspace.

    Parameters
    ----------
    workspace : Workspace
        The GeomAI workspace containing the trained model.

    Returns
    -------
    Dict[str, List[float]]
        Dictionary mapping geometry names to their latent parameter vectors.
    """
    os.makedirs("latent-parameters", exist_ok=True)
    path = os.path.join("latent-parameters", f"{workspace.name}.json")
    workspace.download_latent_parameters_json(path)
    with open(path, "r") as f:
        latent_dict = json.load(f)
    print(f"Loaded {len(latent_dict)} geometries' latent parameters.")
    return latent_dict


latent_dict = get_latent_parameters(workspace)

nb_latent_params = len(next(iter(latent_dict.values())))
print(f"Workspace uses {nb_latent_params} latent parameters")

###############################################################################
# Create output directory
# -----------------------
# Create a directory to save the generated geometries:

output_dir = os.path.join(OUTPUT_DIR, workspace.name)
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory: {output_dir}")

###############################################################################
# Generate random geometries
# --------------------------
# Generate geometries by creating random latent parameter vectors.
# Each latent parameter is randomly sampled from a standard normal distribution.

predictions: list[Prediction] = []

print(f"\nGenerating {NUM_GEOMETRIES} random geometries...")
for i in range(NUM_GEOMETRIES):
    # Generate random latent parameters (from standard normal distribution)
    latent_params = [random.gauss(0, 1) for _ in range(nb_latent_params)]

    # Create prediction configuration
    config = GeomAIPredictionConfiguration(
        latent_params=latent_params,
        resolution=RESOLUTION,
    )

    # Run the prediction
    prediction = client.predictions.run(config, workspace)
    print(f"Prediction {i + 1}/{NUM_GEOMETRIES}: {prediction.id} started...")
    predictions.append(prediction)

for i, prediction in enumerate(predictions):
    # Wait for prediction to complete
    if prediction.wait(timeout=600):  # Wait up to 10 minutes
        prediction.reload()  # Refresh prediction state
        if prediction.has_failed:
            print(f"✗ Prediction {i + 1} failed: {prediction.failure_reason}")
            continue

        # Download the generated geometry
        output_path = os.path.join(output_dir, f"random_{i + 1:02d}_{prediction.id}.vtp")
        client.predictions.download(prediction.id, output_path)
        print(f"✓ Saved geometry to {output_path}")
    else:
        print(f"✗ Prediction {i + 1} timed out")

###############################################################################
# Summary
# -------
# Display generation summary:

print(f"\n{'=' * 50}")
print("Random geometry generation complete!")
print(f"Generated geometries saved in: {output_dir}")

###############################################################################
# Using generated geometries
# --------------------------
# The downloaded VTP files can be used for:
# - Visualization in ParaView or similar tools
# - SimAI training data or predictions
# - Further analysis and post-processing

###############################################################################
# Tips for better results
# -----------------------
# - Latent parameters typically range from -3 to +3 for meaningful results
# - Adjust the resolution to balance quality and file size
# - Increase timeout for complex geometries
# - Use the workspace's latent space statistics (min, max) for better sampling

###############################################################################
# Next steps
# ----------
# To generate geometries with more control, see :ref:`ref_interpolate_geometries`.
