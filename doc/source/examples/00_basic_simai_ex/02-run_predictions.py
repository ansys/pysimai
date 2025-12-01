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

""".. _ref_basic_run_predictions:

Running Physics Predictions
================================================

This example demonstrates how to upload geometries to a workspace and run predictions
using a trained SimAI model. It also shows how to extract and save prediction results,
including global coefficients and confidence scores.

Before you begin
----------------------------------------------------

- Complete ":ref:`ref_basic_build_model`" to train a SimAI model.
- Ensure the model training completed successfully.
- Have a dataset folder with subdirectories containing geometry files. These geometry files can come from a Generative Design model.
- (Optional) Prepare boundary condition JSON files if your model requires them.

"""

###############################################################################
# Import necessary libraries
# ----------------------------------------------------

import json
import os

import ansys.simai.core as asc
from ansys.simai.core.data.geometries import Geometry
from ansys.simai.core.data.predictions import Prediction

###############################################################################
# Configure your settings
# ----------------------------------------------------
# Update these variables with your specific settings:

ORGANIZATION_NAME = "<your_organization>"  # Replace with your organization name
WORKSPACE_NAME = "<your_workspace_name>"  # Replace with your workspace name
DATASET_PATH = "<your_dataset>"  # Path to your dataset directory

###############################################################################
# Initialize the client and set workspace
# ----------------------------------------------------
# Connect to SimAI and set the workspace to use for predictions:

simai_client = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Set the current workspace
# A workspace contains a trained model and is created when a model build completes successfully:

simai_client.set_current_workspace(WORKSPACE_NAME)
current_workspace = simai_client.current_workspace
print(f"Using workspace: {current_workspace.name}")

###############################################################################
# Prepare data structures
# ----------------------------------------------------
# Create lists to store geometries and their boundary conditions:

geometries: list[Geometry] = []
boundary_conditions: list[dict] = []

###############################################################################
# Upload geometries and load boundary conditions
# ----------------------------------------------------
# Process each subdirectory in the dataset:

for dir in os.listdir(f"{DATASET_PATH}"):
    print(f"Processing directory: {dir}")

    # Define the geometry file path
    # The file is uploaded with a specific name for easy identification
    file = (
        f"{DATASET_PATH}/{dir}/surface.vtp",  # Local file path
        f"{dir}.vtp",  # Name to use in SimAI
    )

    # Check if this geometry already exists in the workspace
    geoms = simai_client.geometries.list(
        workspace=current_workspace,
    )

    if f"{dir}.vtp" in [geom.name for geom in geoms]:
        print(f"Geometry {dir}.vtp already uploaded, skipping upload.")
        # Find and use the existing geometry
        existing_geom = [geom for geom in geoms if geom.name == f"{dir}.vtp"][0]
        geometries.append(existing_geom)
    else:
        print(f"Uploading geometry {dir}.vtp...")
        geom = simai_client.geometries.upload(file, workspace=current_workspace)
        geometries.append(geom)

    ###########################################################################
    # Load boundary conditions (if applicable)
    # ----------------------------------------------------
    # This section is optional and only needed if your model requires boundary conditions.
    # If your model doesn't use boundary conditions, you can skip this section.

    try:
        with open(f"{DATASET_PATH}/{dir}/boundary_conditions.json", "r") as f:
            print(f"Loading boundary conditions for {dir}...")
            boundary_conditions_for_geom = json.load(f)
            boundary_conditions.append(boundary_conditions_for_geom)
    except FileNotFoundError:
        print(f"No boundary conditions file found for {dir}, using empty boundary conditions.")
        boundary_conditions.append({})

###############################################################################
# Run predictions on all geometries
# ----------------------------------------------------
# Wait for all geometries to be processed, then run predictions:

preds: list[Prediction] = []

print("\nWaiting for geometries to be processed...")
for geom in geometries:
    print(f"Waiting for geometry {geom.name}...")
    geom.wait()
    print(f"Geometry {geom.name} is processed.")

    # Run prediction with boundary conditions if available
    if boundary_conditions[geometries.index(geom)]:
        preds.append(
            geom.run_prediction(boundary_conditions=boundary_conditions[geometries.index(geom)])
        )
        print(f"Prediction started for geometry {geom.name} with boundary conditions.")
    else:
        # Run prediction without boundary conditions
        preds.append(geom.run_prediction())
        print(f"Prediction started for geometry {geom.name}.")

###############################################################################
# Collect prediction results
# ----------------------------------------------------
# Wait for all predictions to complete and extract results:

results = {}

print("\nWaiting for predictions to complete...")
for pred in preds:
    geom_name = geometries[preds.index(pred)].name
    print(f"Waiting for prediction on geometry {geom_name}...")
    pred.wait()
    print(f"Prediction completed for geometry {geom_name}.")

    # Extract global coefficients and confidence score
    results[geom_name] = pred.post.global_coefficients().data
    results[geom_name]["confidence_score"] = pred.raw_confidence_score

###############################################################################
# Save results to file
# ----------------------------------------------------
# Export all prediction results to a JSON file for further analysis:

print("\nSaving results to results.json...")
with open("results.json", "w") as f:
    json.dump(results, f, indent=4)

print("Results saved successfully!")

###############################################################################
# Understanding the results
# ----------------------------------------------------
# The results dictionary contains:
#
# - Global coefficients: Scalar values computed from the prediction,
# - Confidence score: A measure of how familiar this prediction is for the model.
#
# You can also download full field results (VTP files) for visualization:
#
# - Use ``pred.post.surface_vtp()`` to get surface fields.
# - Use ``pred.post.volume_vtu()`` to get volume fields.

###############################################################################
# Example: Download surface VTP for visualization
# ----------------------------------------------------
# Run the following code to download the first prediction's surface VTP:

if preds:
    first_pred = preds[0]
    first_geom_name = geometries[0].name
    output_path = f"{first_geom_name}_result.vtp"
    first_pred.post.surface_vtp().data.download(output_path)
    print(f"Downloaded surface VTP to {output_path}")

###############################################################################
# Next steps
# ----------------------------------------------------
# With your prediction results, you can:
#
# - Analyze global coefficients to evaluate design performance.
# - Visualize field results in ParaView or similar tools.
# - Compare predictions against validation data.
# - Use results to guide design optimization.
