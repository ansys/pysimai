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

""".. _ref_project_geometries:

Projecting Geometries onto a Model
=================================

This example demonstrates how to project a geometry onto a trained GeomAI model
and retrieve its latent parameters.

Before you begin
----------------

- Complete ":ref:`ref_build_model`" to train a GeomAI model.
- Ensure that the model training has completed successfully and that its workspace is available.
- Prepare a geometry file in ``VTP``, ``ZIP``, ``STL``, or ``CGNS`` format.

"""


###############################################################################
# Import necessary libraries
# ---------------------------

import os
from typing import List

import ansys.simai.core as asc

###############################################################################
# Configure your settings
# -----------------------
# Update these variables with your specific settings:

ORGANIZATION = "my_organization"  # Replace with your organization name
WORKSPACE_NAME = "new-bracket-project #1"  # Replace with your trained model workspace
GEOMETRY_FILE = "./td/bracket_264.vtp"  # VTP, ZIP, STL, or CGNS file to project

###############################################################################
# Initialize the client and get the workspace
# -------------------------------------------

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai
workspace = geomai_client.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")

###############################################################################
# Upload a geometry
# -----------------

print("Uploading geometry...")
geometry = geomai_client.geometries.upload(GEOMETRY_FILE)
geometry.wait()
print(f"Uploaded {geometry.name} with id {geometry.id}")

###############################################################################
# Project the geometry onto the workspace model
# ----------------------------------------------
# The projection operation is idempotent: if this geometry has already been
# projected onto the model, the existing projection is returned.

print("Running projection...")
projection = geometry.run_projection(workspace)
projection.wait()

latent_parameters = projection.get_latent_parameters()
print(f"Projection {projection.id} on model {projection.workspace_id}")
print(f"Retrieved {len(latent_parameters)} latent parameters")
print(f"First three parameters: {projection.get_latent_parameters(n=min(3, len(latent_parameters)))}")

###############################################################################
# Look up an existing projection
# ------------------------------
# Retrieve a projection without starting a new computation. The result is
# ``None`` if the geometry has not been projected onto this workspace's model.

print("\nLooking up an existing projection...")
existing_projection = geometry.get_projection(workspace)
if existing_projection is None:
    print("Geometry has not yet been projected onto this workspace's model.")
else:
    print(f"Existing projection: {existing_projection.id}")

###############################################################################
# List projections in the workspace
# ---------------------------------

projections = workspace.list_projections()
print(f"\n{len(projections)} projections in {workspace.name}")

print("\nProjections for the uploaded geometry:")
geometry_projections = geomai_client.projections.list(workspace=workspace, geometry=geometry)
for geometry_projection in geometry_projections:
    print(f"Projection {geometry_projection.id}: {geometry_projection.get_latent_parameters()}")

###############################################################################
# Count geometries projected in this workspace
# ---------------------------------------------

all_geometries = geomai_client.geometries.list()
projected_geometry_ids = {projection.geometry_id for projection in projections}
print(f"{len(projected_geometry_ids)}/{len(all_geometries)} geometries projected here")

###############################################################################
# Use the latent parameters for a prediction
# ------------------------------------------
# The parameters can be passed to a prediction to reconstruct the geometry:
#
prediction = geomai_client.predictions.run(
    {"latent_params": latent_parameters}, workspace
)
prediction.wait()
geomai_client.predictions.download(prediction.id, f"reconstructed_{geometry.name}.vtp")

###############################################################################
# Next steps
# ----------
# To explore the model further, you can:
#
# - Generate geometries from latent parameters.
# - Interpolate between geometries: :ref:`ref_interpolate_geometries`.