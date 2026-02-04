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

""".. _ref_non_parametric_optimization:

Non-parametric optimization
===========================

This example demonstrates how to perform non-parametric optimization in SimAI
using the automorphing feature. Non-parametric optimization improves the performance
of a baseline geometry by applying smooth, data-driven deformations based on
predicted sensitivity maps.

This approach is especially useful when there are no predefined design parameters,
as it enables you to optimize the geometry directly by applying smooth and continuous
deformations without generating new geometries or reparametrizing existing designs.

Before you begin
----------------

Make sure you have:

- A trained SimAI model with an associated workspace.
- A baseline geometry uploaded to the workspace (supported formats: ``vtp``, ``stl``, ``zip``, ``cgns``).
- Defined bounding boxes that specify regions where deformations can occur.
- The ``ansys-simai-core`` library installed.
- (Optional) The ``pyvista`` library installed for bounding box visualization.

Key concepts
------------

**Baseline geometry**: The geometry to optimize. Choose a representative geometry from your dataset.

**Bounding boxes**: Define the regions where deformations can occur.
Bounding boxes are specified as ``[xmin, xmax, ymin, ymax, zmin, zmax]``.
Start with boxes covering areas most likely to influence performance improvements.

**Symmetries**: Optional constraints to reduce computational costs. Can be planar (e.g., ``["X"]``
for YZ plane symmetry) or axial.

**Scalars**: Must correspond to the scalars defined in the SimAI workspace configuration.

**Number of iterations**: Determines how many rounds of improvement are executed.
Use 5 iterations for quick tests, or 100+ for production runs.

**Objective**: The performance indicator to optimize (e.g., minimize drag, maximize lift).
Only one objective can be defined for non-parametric optimization.

"""

###############################################################################
# Visualize bounding boxes (optional)
# -----------------------------------
# Before running the optimization, you can visualize the bounding boxes
# on your geometry using PyVista to ensure they cover the correct regions.

import pyvista as pv

# Path to the surface mesh file
file_path = "your_geometry.vtp"

# Define bounding boxes as [xmin, xmax, ymin, ymax, zmin, zmax]
bounding_boxes = [[-3100, -1660, 660, 850, 170, 360]]

# Load the mesh from file
mesh = pv.read(file_path)

# Initialize the PyVista plotter
plotter = pv.Plotter()

# Add the mesh to the scene
plotter.add_mesh(mesh, color="white", show_edges=False)

# Add bounding boxes to the scene
for bounds in bounding_boxes:
    box = pv.Cube(bounds=bounds)
    plotter.add_mesh(box, color="lightblue", opacity=0.3)

# Display the plot
plotter.show()

###############################################################################
# Import necessary libraries
# --------------------------

import os

import ansys.simai.core as asc
from ansys.simai.core.data.predictions import Prediction

###############################################################################
# Configure your settings
# -----------------------
# Update these variables with your specific settings:

ORGANIZATION_NAME = "<your_organization>"  # Replace with your organization name
WORKSPACE_NAME = "<your_workspace_name>"  # Replace with your workspace name
CHOSEN_GEOMETRY_NAME = "<your_geometry.vtp>"  # Your geometry must be uploaded to the workspace
BOUNDING_BOXES = [[-3100.0, -1660.0, 660.0, 850.0, 170.0, 360.0]]  # Define your bounding boxes
N_ITERS = 50  # Number of optimization iterations
SYMMETRIES = []  # Symmetry constraints (e.g., ["X"] for YZ plane symmetry)
OBJECTIVE = ["gc_Force"]  # Objective to maximize (use minimize parameter for minimization)
OUTPUT_FOLDER = "simai_output"  # Folder to save results

###############################################################################
# Initialize SimAI client and workspace
# -------------------------------------
# Connect to SimAI and retrieve the workspace and baseline geometry:

simai = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Retrieve the workspace containing your trained model:

workspace = simai.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")

###############################################################################
# Retrieve the baseline geometry to optimize:

geometry = simai.geometries.get(workspace=workspace, name=CHOSEN_GEOMETRY_NAME)
print(f"Baseline geometry: {geometry.name}")

###############################################################################
# Run non-parametric optimization
# -------------------------------
# Launch the optimization with the configured parameters.
# The optimization will generate new geometries at each iteration
# by applying smooth deformations to the baseline geometry.

optimization_result = simai.optimizations.run_non_parametric(
    geometry=geometry,
    bounding_boxes=BOUNDING_BOXES,
    scalars={"Time": 54},  # Scalars must match your workspace configuration
    n_iters=N_ITERS,
    symmetries=SYMMETRIES,
    maximize=OBJECTIVE,  # Use 'minimize' parameter for minimization objectives
    show_progress=True,
)

###############################################################################
# Display optimization results
# ----------------------------
# Print the optimization ID, generated geometries, and objective values:

print(f"Optimization ID: {optimization_result.optimization.id}")
print(f"Generated geometries: {[geo.name for geo in optimization_result.list_geometries()]}")
print(f"Objectives: {optimization_result.list_objectives()}")

###############################################################################
# Run predictions on optimized geometries
# ---------------------------------------
# You can get back your optimization from its ID when done asynchronously. 
# Run predictions on all generated geometries to evaluate their performance:

predictions: list[Prediction] = []

for geom in optimization_result.list_geometries():
    print(f"Running prediction for: {geom.name} (ID: {geom.id})")
    prediction = geom.run_prediction(scalars={"Time": 54}) # Scalars must match your workspace configuration
    predictions.append(prediction)

###############################################################################
# Download post-processing results
# --------------------------------
# Download global coefficients and surface VTP files for each prediction:

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for prediction in predictions:
    # Wait for prediction to complete
    prediction.wait()

    geom = prediction.geometry
    geom_name = geom.name.split(".")[0]

    print(f"Downloading results for: {geom.name} (ID: {geom.id})")

    # Get and save global coefficients as JSON
    global_coeffs = prediction.post.global_coefficients()
    global_coeffs.export().download(f"{OUTPUT_FOLDER}/{geom_name}_global_coefficients.json")

    # Download surface VTP file for visualization
    surface_vtp = prediction.post.surface_vtp()
    surface_vtp.data.download(f"{OUTPUT_FOLDER}/{geom_name}_surface.vtp")

print("All results downloaded successfully!")

###############################################################################
# Tips for effective optimization
# -------------------------------
#
# **Data preparation**: Ensure the maximum magnitude within simulation data matches
# the minimal optimization gain you want. For example, for a 4% drag reduction,
# ensure there is around 4% drag difference between the best and worst training data.
#
# **Bounding boxes**: Start with boxes covering areas most likely to influence performance.
# If results don't improve, increase box size or add more boxes. Avoid excessively large
# boxes that may cause unrealistic deformations.
#
# **Baseline geometry**: If optimization doesn't improve after several iterations,
# try a different geometry from the training data. Ensure the geometry is clean
# and of high quality.
#
# **Iterative workflow**: For best results, run the optimization, verify results
# with your solver, add optimums as new training data, rebuild the model, and repeat
# at least 3 times.

###############################################################################
# Next steps
# ----------
#
# - Visualize the surface VTP files.
# - Compare global coefficients across generated geometries.
# - Run solver verification on selected optimized geometries.
# - Add validated results as new training data for model improvement.
#
# For more details on configuration options, see the
# :ref:`automorphing configuration guide <configure_automorphing>`.
