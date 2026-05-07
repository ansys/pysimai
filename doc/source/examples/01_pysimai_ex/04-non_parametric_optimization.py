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

# ruff: noqa: ERA001

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
- (Optional) The ``pyvista`` library (or your preferred CAD tool) installed for bounding box visualization.

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

**Offline token**: Required for server-side optimization. Allows the server to authenticate
on your behalf while uploading geometries at each iteration. Generated via
``simai.me.generate_offline_token()`` and valid for 30 days.

**Detail level**: Controls deformation refinement (integer from 1 to 10, default: 5).
Low values produce coarse shape changes; high values allow fine local adjustments.

**Part morphing**: Optional constraint that restricts deformation to specific geometry parts
identified by a ``PartId`` cell field.
"""

###############################################################################
# Visualize bounding boxes (optional)
# -----------------------------------
# Before running the optimization, you can visualize the bounding boxes
# on your geometry using PyVista to ensure they cover the correct regions.

import pyvista as pv

# Path to the surface mesh file - replace with your geometry file path
file_path = "<your_geometry_file.vtp>"

# Define bounding boxes as [xmin, xmax, ymin, ymax, zmin, zmax]
BOUNDING_BOXES = [[-0.07, 0.15, -0.06, 0.12, -0.09, 0.15]]

mesh = pv.read(file_path)
plotter = pv.Plotter()
plotter.add_mesh(mesh, color="white", show_edges=False)

# Add bounding boxes to the scene
for bounds in BOUNDING_BOXES:
    box = pv.Cube(bounds=bounds)
    plotter.add_mesh(box, color="lightblue", opacity=0.3)

plotter.show()

###############################################################################
# Run non-parametric optimization
# ----------------------------------
# **This is the only section you need to edit.**
# Update the variables below to match your setup and the rest of the script
# will run automatically without any further changes.
#
# The one exception is if you want to **minimize** the objective instead of
# maximizing it: replace ``maximize=OBJECTIVE`` with ``minimize=OBJECTIVE``
# in the ``run_non_parametric`` call further below.

import os

import ansys.simai.core as asc
from ansys.simai.core.data.predictions import Prediction

ORGANIZATION_NAME = "<your_organization_name>"
WORKSPACE_NAME = "<your_workspace_name>"
CHOSEN_GEOMETRY_NAME = "<your_geometry_file.vtp>"

# A bounding box must be defined as [xmin, xmax, ymin, ymax, zmin, zmax]
BOUNDING_BOXES = [[-0.07, 0.15, -0.06, 0.12, -0.09, 0.15]]
NUMBER_OF_ITERATIONS = 10
# Maximum displacement per bounding box (one value per box, same unit as geometry)
MAX_DISPLACEMENT = [0.1]
# Symmetry constraints (e.g., ["X"] for YZ plane symmetry)
SYMMETRIES = []
# Objective to maximize (use minimize parameter for minimization)
OBJECTIVE = ["<global_coefficient_objective>"]
# Detail level controls deformation refinement (integer from 1 to 10, default: 5)
DETAIL_LEVEL = 5
# Output folder for results
OUTPUT_FOLDER = "simai_output"

###############################################################################
# Part morphing (optional)
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Part morphing restricts deformation to specific parts of the geometry
# identified by a ``PartId`` cell field. The ``continuity_constraint``
# parameter (0 to 1) controls how smoothly the deformed region blends
# with the rest. A value of 0 means no continuity enforcement; 1 gives
# the best continuity but reduces the overall deformation magnitude.
# Before adjusting ``detail_level`` to compensate, first experiment with
# different ``continuity_constraint`` values to find the right balance
# between interface smoothness and deformation magnitude.

from ansys.simai.core.data.optimizations import OptimizationPartMorphingSchema

PART_MORPHING = OptimizationPartMorphingSchema(
    part_ids=[0],  # IDs matching the ``PartId`` cell field
    continuity_constraint=0.5,  # 0 = no constraint, 1 = maximum continuity
)

###############################################################################
# Initialize SimAI client and workspace
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Connect to SimAI and retrieve the workspace and baseline geometry:

simai = asc.SimAIClient(organization=ORGANIZATION_NAME)

workspace = simai.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")

geometry = simai.geometries.get(workspace=workspace, name=CHOSEN_GEOMETRY_NAME)
print(f"Baseline geometry: {geometry.name}")

###############################################################################
# Generate an offline token
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The optimization runs server-side. At each iteration the geometry
# corresponding to the current step is uploaded to your workspace.
# An ``offline_token`` is required so that the server can authenticate
# on your behalf during this process.
#
# Generating the token requires a manual action (browser login).
# Once generated, the token is valid for 30 days. You can generate as many
# tokens as needed.

offline_token = simai.me.generate_offline_token()

###############################################################################
# Start the optimization
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Launch the optimization with the configured parameters.
# The optimization will generate new geometries at each iteration
# by applying smooth deformations to the baseline geometry.

optimization = simai.optimizations.run_non_parametric(
    geometry=geometry,
    offline_token=offline_token,
    bounding_boxes=BOUNDING_BOXES,
    max_displacement=MAX_DISPLACEMENT,
    scalars={},  # Scalars must match your workspace configuration
    n_iters=NUMBER_OF_ITERATIONS,
    symmetries=SYMMETRIES,
    detail_level=DETAIL_LEVEL,
    maximize=OBJECTIVE,  # Use 'minimize' parameter for minimization objectives
    show_progress=True,
    part_morphing=PART_MORPHING,  # Comment to disable part morphing
)
optimization.wait()

###############################################################################
# Display optimization results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Print the optimization ID, generated geometries, and objective values:

from ansys.simai.core.data.optimizations import Optimization

optimization_id = (
    optimization.id if isinstance(optimization, Optimization) else optimization.optimization.id
)

print(f"Optimization ID: {optimization_id}")
print(f"Generated geometries: {[geo.name for geo in optimization.list_geometries()]}")
print(f"Objectives: {optimization.list_objectives()}")

###############################################################################
# Run predictions on optimized geometries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can get back your optimization from its ID when done asynchronously.
# Run predictions on all generated geometries to evaluate their performance:

predictions: list[Prediction] = []

for geom in optimization.list_geometries():
    print(f"Running prediction for: {geom.name} (ID: {geom.id})")
    prediction = geom.run_prediction(scalars={})  # Scalars must match your workspace configuration
    predictions.append(prediction)

###############################################################################
# Analyze the results from an optimization run
# ----------------------------------------------
# Download surface VTP files for each prediction:
VTPS_FOLDER = f"{OUTPUT_FOLDER}/optimization_{optimization_id}/VTPs"
os.makedirs(VTPS_FOLDER, exist_ok=True)

for prediction in predictions:
    # Wait for prediction to complete
    prediction.wait()

    geom = prediction.geometry
    geom_name = geom.name.split(".")[0]

    print(f"Downloading results for: {geom.name} (ID: {geom.id})")
    surface_vtp = prediction.post.surface_vtp()
    surface_vtp.data.download(f"{VTPS_FOLDER}/{geom_name}_surface.vtp")

print("All results downloaded successfully!")

###############################################################################
# Visualize optimization progression
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot the objective value at each iteration alongside the baseline and
# ±5 % reference bands, then plot mean and maximum displacement per iteration.

import matplotlib.pyplot as plt
import numpy as np

###############################################################################
# Get the baseline objective value
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run a prediction on the original baseline geometry to obtain the
# reference objective value used for the ±5 % horizontal bands.

CHARTS_FOLDER = f"{OUTPUT_FOLDER}/optimization_{optimization_id}/charts"
os.makedirs(CHARTS_FOLDER, exist_ok=True)

print("Running baseline prediction for visualization reference...")
baseline_pred = geometry.run_prediction()
baseline_pred.wait()
baseline_gc_data = baseline_pred.post.global_coefficients().data
baseline_value = float(baseline_gc_data[OBJECTIVE[0]]["data"])

print(f"Baseline {OBJECTIVE[0]}: {baseline_value:.4f}")

###############################################################################
# Collect per-iteration objective values
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The optimization records the scalar objective at each iteration.

raw_objectives = optimization.list_objectives()
obj_values = [float(obj[OBJECTIVE[0]]) for obj in raw_objectives]

iterations = range(1, len(obj_values) + 1)

###############################################################################
# Chart 1 – Objective progression over iterations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The dashed and dotted horizontal lines mark a ±5 % band around the baseline.

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(iterations, obj_values, marker="o", linewidth=2, label=OBJECTIVE[0])
ax.axhline(baseline_value, color="black", linewidth=1.5, linestyle="-", label="Baseline")
ax.axhline(
    baseline_value * 1.05,
    color="gray",
    linewidth=1,
    linestyle="--",
    label="Baseline +5 %",
)
ax.axhline(
    baseline_value * 0.95,
    color="gray",
    linewidth=1,
    linestyle=":",
    label="Baseline \u22125 %",
)

ax.set_xlabel("Iteration")
ax.set_ylabel(OBJECTIVE[0])
ax.set_title("Objective progression over optimization iterations")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{CHARTS_FOLDER}/objective_progression.png", dpi=150)
plt.show()

###############################################################################
# Collect per-iteration displacement statistics
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Read the surface VTP file for each generated geometry and extract the
# ``Delta`` field.  Nodes that did not move (value == 0) are
# filtered out because many surface nodes are intentionally frozen by the
# bounding-box constraints.  Mean and maximum magnitude are then computed
# from the remaining active nodes.

geom_list = optimization.list_geometries()
mean_displacements = []
max_displacements = []

for geom in geom_list:
    geom_name = geom.name.split(".")[0]
    vtp_path = f"{VTPS_FOLDER}/{geom_name}_surface.vtp"
    mesh = pv.read(vtp_path)
    delta = mesh.point_data["Delta"]

    # Compute per-node magnitude
    magnitude = np.linalg.norm(delta, axis=1)

    # Exclude nodes that did not move by design
    nonzero = magnitude[magnitude > 0]
    mean_displacements.append(float(nonzero.mean()) if nonzero.size > 0 else 0.0)
    max_displacements.append(float(nonzero.max()) if nonzero.size > 0 else 0.0)

###############################################################################
# Chart 2 – Displacement statistics over iterations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Shows how the surface deformation evolves iteration by iteration.
# A growing maximum displacement indicates the optimizer is making increasingly
# bold geometry changes; a plateau suggests convergence.

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    iterations,
    mean_displacements,
    marker="o",
    linewidth=2,
    label="Mean displacement (active nodes)",
)
ax.plot(
    iterations,
    max_displacements,
    marker="s",
    linewidth=2,
    linestyle="--",
    label="Max displacement (active nodes)",
)

ax.set_xlabel("Iteration")
ax.set_ylabel("Delta magnitude")
ax.set_title("Surface displacement statistics over optimization iterations")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{CHARTS_FOLDER}/displacement_statistics.png", dpi=150)
plt.show()

print(f"Charts saved to {CHARTS_FOLDER}.")

###############################################################################
# Tips for effective optimization
# ------------------------------------------------------
#
# **Data preparation**: Ensure the maximum magnitude within simulation data matches
# the minimal optimization gain you want. For example, for a 4% drag reduction,
# ensure there is around 4% drag difference between the best and worst training data.
#
# **Bounding boxes**: Start with boxes covering areas most likely to influence performance.
# If results do not improve, increase box size or add more boxes. Avoid excessively large
# boxes that may cause unrealistic deformations.
#
# **Baseline geometry**: If optimization does not improve after several iterations,
# try a different geometry from the training data. Ensure the geometry is clean
# and of high quality.
#
# **Iterative workflow**: For best results, run the optimization, verify results
# with your solver, add optimums as new training data, rebuild the model, and repeat
# at least 3 times.

###############################################################################
# Next steps
# ------------------------------------------------------
#
# - Visualize the surface VTP files.
# - Run solver verification on selected optimized geometries.
# - Add validated results as new training data for model improvement.
#
# For more details on configuration options, see the
# :ref:`automorphing configuration guide <configure_automorphing>`.

###############################################################################
# Other tools: Generate screenshots and GIFs
# ------------------------------------------------------
# For every optimized geometry, render a screenshot from each camera angle.
# Then assemble one GIF per angle so the deformation is
# clearly visible.
#
# Requirements: ``pip install imageio``

import imageio.v3 as iio

SCREENSHOTS_FOLDER = f"{OUTPUT_FOLDER}/optimization_{optimization_id}/screenshots"
GIFS_FOLDER = f"{OUTPUT_FOLDER}/optimization_{optimization_id}/GIFs"

os.makedirs(SCREENSHOTS_FOLDER, exist_ok=True)
os.makedirs(GIFS_FOLDER, exist_ok=True)

# Output image resolution (width, height) in pixels
IMG_SIZE = (1920, 1080)

# Visual style
BACKGROUND_COLOR = "white"
MESH_COLOR = "lightgray"

GIF_FRAME_DURATION_MS = 120

# Named camera angles
CAMERA_ANGLES = {
    "front": ((0, -1, 0), (0, 0, 1)),
    "rear": ((0, 1, 0), (0, 0, 1)),
    "left": ((-1, 0, 0), (0, 0, 1)),
    "right": ((1, 0, 0), (0, 0, 1)),
    "top": ((0, 0, 1), (0, 1, 0)),
    "bottom": ((0, 0, -1), (0, 1, 0)),
    "isometric": ((1, 1, 1), (0, 0, 1)),
}


def _apply_camera(plotter: pv.Plotter, camera_angle: str) -> None:
    """Point the camera in the direction specified by ``camera_angle``."""
    position_dir, view_up = CAMERA_ANGLES[camera_angle]

    plotter.reset_camera()
    focal = np.array(plotter.camera.focal_point)
    dist = plotter.camera.distance
    pos_dir = np.array(position_dir, dtype=float)
    pos_dir /= np.linalg.norm(pos_dir)
    plotter.camera.position = focal + pos_dir * dist
    plotter.camera.focal_point = focal
    plotter.camera.up = view_up


def screenshot_vtp(
    vtp_path: str,
    png_path: str,
    camera_angle: str = "isometric",
) -> None:
    """Render a PNG screenshot with a camera framed on the global bounding box."""
    mesh = pv.read(vtp_path)
    plotter = pv.Plotter(off_screen=True, window_size=IMG_SIZE)
    plotter.background_color = BACKGROUND_COLOR
    plotter.add_mesh(mesh, color=MESH_COLOR, show_edges=False)
    _apply_camera(plotter, camera_angle)
    plotter.camera.zoom(1.3)
    plotter.screenshot(png_path)
    plotter.close()


# ---------------------------------------------------------------------------
# Render screenshots and GIFs
# ---------------------------------------------------------------------------

all_vtp_paths = [
    f"{VTPS_FOLDER}/{geom.name.split('.')[0]}_surface.vtp"
    for geom in optimization.list_geometries()
]

png_index: dict[str, list[str]] = {angle: [] for angle in CAMERA_ANGLES}

for vtp_path in all_vtp_paths:
    stem = os.path.splitext(os.path.basename(vtp_path))[0]
    for angle_name in CAMERA_ANGLES:
        png_path = f"{SCREENSHOTS_FOLDER}/{stem}_{angle_name}.png"
        screenshot_vtp(vtp_path, png_path, camera_angle=angle_name)
        png_index[angle_name].append(png_path)
        print(f"  Screenshot → {png_path}")


for angle_name, png_paths in png_index.items():
    if not png_paths:
        continue
    gif_path = f"{GIFS_FOLDER}/{angle_name}.gif"
    frames = [iio.imread(p) for p in png_paths]
    iio.imwrite(gif_path, frames, duration=GIF_FRAME_DURATION_MS, loop=0)
    print(f"  GIF ({len(frames)} frames) → {gif_path}")

print("\nAll screenshots and GIFs saved.")
