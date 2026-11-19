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

Interpolate between geometries with a GeomAI model
==================================================

This example interpolates between two geometries in the latent space of a GeomAI model
and downloads the intermediate geometries as VTP files.

Latent space interpolation lets you:

- Create smooth transitions between existing designs.
- Explore the design space systematically.
- Generate variations that blend features from multiple geometries.

Prerequisites to interpolate geometries with a GeomAI model
-----------------------------------------------------------

- Complete ":ref:`ref_build_model`" to build a GeomAI model.
- Make sure that the model build completed successfully: a new workspace exists for the GeomAI model.

"""


###############################################################################
# Import the classes to interpolate geometries with a GeomAI model
# ----------------------------------------------------------------

import os
from typing import List

import ansys.simai.core as asc
from ansys.simai.core.data.geomai.predictions import GeomAIPrediction, GeomAIPredictionConfiguration
from ansys.simai.core.errors import ProcessingError

###############################################################################
# Set the workspace and the two geometries to interpolate
# -------------------------------------------------------
# Replace these values with your own:

ORGANIZATION = "my_organization"  # Replace with your organization name
PROJECT_NAME = "new-bracket-project"  # Replace with your project name
WORKSPACE_NAME = "new-bracket-project #1"  # Typically "{PROJECT_NAME} #{number}"
OUTPUT_DIR = "interpolations"  # Directory to save interpolated geometries
NUM_STEPS = 10  # Number of interpolation steps

# Choose geometries to interpolate between (by name)
GEOM_A_NAME = "geometry_name_a"  # Replace with actual geometry name
GEOM_B_NAME = "geometry_name_b"  # Replace with actual geometry name


###############################################################################
# Define a linear interpolation function for latent parameters
# ------------------------------------------------------------
# Before you run predictions, define a function that interpolates between two
# latent parameter vectors.


def interpolate_latents(vec1: List[float], vec2: List[float], alpha: float) -> List[float]:
    """Perform linear interpolation between two latent parameter vectors.

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
# Get the workspace of the GeomAI model
# -------------------------------------
# Connect to Ansys SimAI and get the workspace of the built GeomAI model:

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai

workspace = geomai_client.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")

###############################################################################
# Get the latent parameters of the training geometries
# ----------------------------------------------------
# Get the latent parameters of all training geometries in the workspace:

latent_dict = workspace.get_latent_parameters()

###############################################################################
# List the geometries available for interpolation
# -----------------------------------------------
# List all geometries available for interpolation:

print("\nAvailable geometries:")
for i, name in enumerate(latent_dict.keys()):
    print(f"  [{i}] {name}")

###############################################################################
# Check that the two selected geometries exist in the workspace
# -------------------------------------------------------------
# Stop the script if a selected geometry does not exist:

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
# Run GeomAI model predictions along the interpolation path
# ---------------------------------------------------------
# Generate intermediate geometries with a linear interpolation in latent space:

vec_a = latent_dict[GEOM_A_NAME]
vec_b = latent_dict[GEOM_B_NAME]

predictions: list[GeomAIPrediction] = []

for i in range(NUM_STEPS + 1):
    alpha = i / NUM_STEPS
    latent_params = interpolate_latents(vec_a, vec_b, alpha)
    print(f"\nGenerating geometry {i}/{NUM_STEPS} (alpha={alpha:.2f})...")
    config = GeomAIPredictionConfiguration(
        latent_params=latent_params,
    )
    prediction = geomai_client.predictions.run(config, workspace)
    print(f"Prediction {i}: {prediction.id} started...")
    predictions.append(prediction)


###############################################################################
# Download the interpolated geometries
# ------------------------------------
# Wait for each prediction, then download the generated geometry.

for i, prediction in enumerate(predictions):
    # wait() returns False on timeout and raises ProcessingError if the prediction fails.
    try:
        if not prediction.wait(timeout=600):  # Wait up to 10 minutes
            print(f"✗ Prediction {i} timed out.")
            continue
    except ProcessingError:
        print(f"✗ Prediction {i} failed: {prediction.failure_reason}")
        continue

    # Save result
    out_dir = os.path.join(OUTPUT_DIR, workspace.name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"prediction_{i:02d}_{prediction.id}.vtp")
    geomai_client.predictions.download(prediction.id, out_path)
    print(f"✓ Saved prediction to {out_path}")

###############################################################################
# You can use the downloaded VTP files for:
#
# - Visualization in your usual solver.
# - Training data or predictions for a SimAI model.
# - Further analysis and postprocessing.

###############################################################################
# Extend the interpolation with a GeomAI model
# --------------------------------------------
# To go further, you can:
#
# - Interpolate between more than two geometries.
# - Combine interpolation with optimization for specific design goals.
# - Project a new geometry onto the GeomAI model to get its latent parameters:
#   :ref:`ref_project_geometries`.
#
# For the complete task, see :doc:`/user-guide/geomai-models/interpolate-and-project`.
