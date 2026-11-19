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

""".. _ref_basic_run_predictions:

Run predictions with a SimAI model
==================================

This example uploads geometries to the workspace of a SimAI model, runs a prediction on each
geometry, and saves the global coefficients and confidence score of each prediction.

Prerequisites to run predictions with a SimAI model
---------------------------------------------------

- Complete ":ref:`ref_basic_build_model`" to build a SimAI model.
- Make sure that the model build completed successfully.
- A dataset folder whose subdirectories each contain a ``surface.vtp`` geometry file.
  The geometries can come from a GeomAI model.
- (Optional) A ``scalars.json`` scalar file in each subdirectory, if the SimAI model uses scalars.

"""

###############################################################################
# Import the classes to run SimAI model predictions
# -------------------------------------------------

import json
import os

import ansys.simai.core as asc
from ansys.simai.core.data.geometries import Geometry
from ansys.simai.core.data.predictions import Prediction

###############################################################################
# Set the workspace and dataset path for the SimAI model predictions
# ------------------------------------------------------------------
# Replace these values with your own:

ORGANIZATION_NAME = "<your_organization>"  # Replace with your organization name
WORKSPACE_NAME = "<your_workspace_name>"  # Replace with your workspace name
DATASET_PATH = "<your_dataset>"  # Path to your dataset directory

###############################################################################
# Set the workspace of the SimAI model as the current workspace
# -------------------------------------------------------------
# Connect to Ansys SimAI and set the workspace to use for predictions:

simai_client = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Set the current workspace:

simai_client.set_current_workspace(WORKSPACE_NAME)
current_workspace = simai_client.current_workspace
print(f"Using workspace: {current_workspace.name}")

###############################################################################
# A workspace contains a built SimAI model. Ansys SimAI creates the workspace when a
# model build completes successfully.

###############################################################################
# Prepare lists for the geometries and their scalars
# --------------------------------------------------
# Create lists to store the geometries and their scalars:

geometries: list[Geometry] = []
scalars: list[dict] = []

###############################################################################
# Upload the geometries and load their scalars
# --------------------------------------------
# Process each subdirectory of the dataset:

for dir in os.listdir(f"{DATASET_PATH}"):
    print(f"Processing directory: {dir}")

    # Define the geometry file path
    # The file is uploaded with a specific name for easy identification
    file = (
        f"{DATASET_PATH}/{dir}/surface.vtp",  # Local file path
        f"{dir}.vtp",  # Name to use in Ansys SimAI
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
    # Load the scalars of each geometry (optional)
    # --------------------------------------------
    # Load scalars only if the SimAI model uses scalars as model inputs.
    # Otherwise, skip this step.

    try:
        with open(f"{DATASET_PATH}/{dir}/scalars.json", "r") as f:
            print(f"Loading scalars for {dir}...")
            scalars_for_geom = json.load(f)
            scalars.append(scalars_for_geom)
    except FileNotFoundError:
        print(f"No scalar file found for {dir}, using empty dict.")
        scalars.append({})

###############################################################################
# Run a SimAI model prediction on each geometry
# ---------------------------------------------
# Wait for all geometries to be processed, then run predictions:

preds: list[Prediction] = []

print("\nWaiting for geometries to be processed...")
for geom in geometries:
    print(f"Waiting for geometry {geom.name}...")
    geom.wait()
    print(f"Geometry {geom.name} is processed.")

    # Run prediction with scalars if available
    if scalars[geometries.index(geom)]:
        preds.append(geom.run_prediction(scalars=scalars[geometries.index(geom)]))
        print(f"Prediction started for geometry {geom.name} with scalars.")
    else:
        # Run prediction without scalars
        preds.append(geom.run_prediction())
        print(f"Prediction started for geometry {geom.name}.")

###############################################################################
# Collect the global coefficients and confidence scores of the predictions
# ------------------------------------------------------------------------
# Wait for all predictions to complete and extract the results:

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
# Save the SimAI model prediction results to a JSON file
# ------------------------------------------------------
# Export all prediction results to a JSON file for further analysis:

print("\nSaving results to results.json...")
with open("results.json", "w") as f:
    json.dump(results, f, indent=4)

print("Results saved successfully!")

###############################################################################
# Read the SimAI model prediction results
# ---------------------------------------
# The results dictionary contains, for each geometry:
#
# - Global coefficients: scalar values computed from the prediction.
# - Confidence score: a measure of how familiar this prediction is for the SimAI model.
#
# You can also download full field results (VTP and VTU files) for visualization:
#
# - Use ``pred.post.surface_vtp()`` to get surface fields.
# - Use ``pred.post.volume_vtu()`` to get volume fields.

###############################################################################
# Download the surface VTP file of the first SimAI model prediction
# -----------------------------------------------------------------
# Download the surface VTP file of the first prediction:

if preds:
    first_pred = preds[0]
    first_geom_name = geometries[0].name
    output_path = f"{first_geom_name}_result.vtp"
    first_pred.post.surface_vtp().data.download(output_path)
    print(f"Downloaded surface VTP to {output_path}")

###############################################################################
# Analyze and reuse the SimAI model predictions
# ---------------------------------------------
# With your prediction results, you can:
#
# - Analyze global coefficients to evaluate design performance.
# - Visualize field results in ParaView or similar tools.
# - Compare predictions against validation data.
# - Optimize a design: :doc:`/user-guide/simai-models/optimize-a-design`.
#
# For the complete tasks, see :doc:`/user-guide/simai-models/run-predictions` and
# :doc:`/user-guide/simai-models/postprocess-predictions`.
