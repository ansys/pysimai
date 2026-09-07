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

""".. _ref_interpolate_geometries:

Interpolating Between Geometries
==============================================

This example demonstrates how to interpolate between two geometries in latent space.

Latent space interpolation allows you to:

- Create smooth transitions between existing designs.
- Explore the design space systematically.
- Generate variations that blend features from multiple geometries.

Before you begin
-------------------------------------------

- Complete ":ref:`ref_build_model`" to train a Generative design model.
- Ensure that the model training has been completed successfully. To do so, verify if a new workspace was created for the trained model.

"""


###############################################################################
# Import necessary libraries
# -------------------------------------------

import os
from typing import List

import ansys.simai.core as asc
from ansys.simai.core.data.geomai.predictions import GeomAIPrediction, GeomAIPredictionConfiguration

###############################################################################
# Configure your settings
# -------------------------------------------
# Update these variables with your specific settings:

ORGANIZATION = "my_organization"  # Replace with your organization name
PROJECT_NAME = "new-bracket-project"  # Replace with your project name
WORKSPACE_NAME = "new-bracket-project #1"  # Typically "{PROJECT_NAME} #{number}"
OUTPUT_DIR = "interpolations"  # Directory to save interpolated geometries
NUM_STEPS = 10  # Number of interpolation steps
RESOLUTION = (100, 100, 100)  # Output resolution (x, y, z)

# Choose geometries to interpolate between (by name)
GEOM_A_NAME = "geometry_name_a"  # Replace with actual geometry name
GEOM_B_NAME = "geometry_name_b"  # Replace with actual geometry name


###############################################################################
# Define the interpolation function
# -------------------------------------------
# Before running predictions, we need a function to interpolate between two latent vectors.


def interpolate_latents(vec1: List[float], vec2: List[float], alpha: float) -> List[float]:
    """Perform linear interpolation between two latent vectors.

    Parameters
    ----------
    vec1 : List[float]
        First latent parameter vector.
    vec2 : List[float]
        Second latent parameter vector.
    alpha : float
        Interpolation factor (0.0 = vec1, 1.0 = vec2).

    Returns
    -------
    List[float]
        Interpolated latent parameter vector.
    """
    return [(1 - alpha) * x + alpha * y for x, y in zip(vec1, vec2)]


###############################################################################
# Initialize the client and get the workspace
# --------------------------------------------------
# Connect to GeomAI and retrieve your trained workspace:

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai

workspace = geomai_client.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")

###############################################################################
# Get latent parameters for all geometries
# -----------------------------------------------
# Download the latent parameters of all training geometries in the workspace:

latent_dict = workspace.get_latent_parameters()

###############################################################################
# Display available geometries
# ----------------------------------
# List all geometries available for interpolation:

print("\nAvailable geometries:")
for i, name in enumerate(latent_dict.keys()):
    print(f"  [{i}] {name}")

###############################################################################
# Validate selected geometries
# -------------------------------------------
# Check if the selected geometries exist:

if GEOM_A_NAME not in latent_dict:
    print(f"Error: Geometry '{GEOM_A_NAME}' not found in workspace.")
    print("Please update GEOM_A_NAME with a valid geometry name from the list above.")
    raise ValueError(f"Geometry '{GEOM_A_NAME}' not found")

if GEOM_B_NAME not in latent_dict:
    print(f"Error: Geometry '{GEOM_B_NAME}' not found in workspace.")
    print("Please update GEOM_B_NAME with a valid geometry name from the list above.")
    raise ValueError(f"Geometry '{GEOM_B_NAME}' not found")

print(f"\nInterpolating from '{GEOM_A_NAME}' to '{GEOM_B_NAME}' in {NUM_STEPS} steps.")

###############################################################################
# Interpolate in latent space and generate geometries
# ----------------------------------------------------------
# Generate intermediate geometries by linearly interpolating in latent space:

vec_a = latent_dict[GEOM_A_NAME]
vec_b = latent_dict[GEOM_B_NAME]

predictions: list[GeomAIPrediction] = []

for i in range(NUM_STEPS + 1):
    alpha = i / NUM_STEPS
    latent_params = interpolate_latents(vec_a, vec_b, alpha)
    print(f"\nGenerating geometry {i}/{NUM_STEPS} (alpha={alpha:.2f})...")
    config = GeomAIPredictionConfiguration(
        latent_params=latent_params,
        resolution=RESOLUTION,
    )
    prediction = geomai_client.predictions.run(config, workspace)
    print(f"Prediction {i}: {prediction.id} started...")
    predictions.append(prediction)


###############################################################################
# Download generated geometries
# -------------------------------------------

for i, prediction in enumerate(predictions):
    if prediction.wait(timeout=600):  # Wait up to 10 minutes
        if prediction.has_failed:
            print(f"✗ Prediction {i} failed: {prediction.failure_reason}")
            continue

        # Save result
        out_dir = os.path.join(OUTPUT_DIR, workspace.name)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"prediction_{i:02d}_{prediction.id}.vtp")
        geomai_client.predictions.download(prediction.id, out_path)
        print(f"✓ Saved prediction to {out_path}")
    else:
        print(f"✗ Prediction {i} timed out.")

###############################################################################
# The downloaded VTP files can be used for:
#
# - Visualization in your usual solver.
# - SimAI training data or predictions.
# - Further analysis and post-processing.

###############################################################################
# Next steps
# -------------------------------------------
# To go further, you can:
#
# - Interpolate between more than two geometries.
# - Combine interpolation with optimization for specific design goals.
