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

Project a geometry onto a GeomAI model
======================================

This example projects a geometry onto a built GeomAI model, gets its latent parameters,
and regenerates the geometry from them.

Prerequisites to project a geometry onto a GeomAI model
-------------------------------------------------------

- Complete ":ref:`ref_build_model`" to build a GeomAI model.
- Make sure that the model build completed successfully and that its workspace is available.
- A geometry file in ``VTP`` or ``STL`` format.

"""


###############################################################################
# Import the classes to project a geometry onto a GeomAI model
# ------------------------------------------------------------

import ansys.simai.core as asc
from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration

###############################################################################
# Set the workspace and the geometry file to project
# --------------------------------------------------
# Replace these values with your own:

ORGANIZATION = "my_organization"  # Replace with your organization name
WORKSPACE_NAME = "new-bracket-project #1"  # Replace with the workspace of your GeomAI model
GEOMETRY_FILE = "./td/bracket_264.vtp"  # VTP or STL file to project

###############################################################################
# Get the workspace of the GeomAI model
# -------------------------------------

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai
workspace = geomai_client.workspaces.get(name=WORKSPACE_NAME)
print(f"Using workspace: {workspace.name}")

###############################################################################
# Upload the geometry to project
# ------------------------------

print("Uploading geometry...")
geometry = geomai_client.geometries.upload(GEOMETRY_FILE)
geometry.wait()
print(f"Uploaded {geometry.name} with id {geometry.id}")

###############################################################################
# Project the geometry onto the GeomAI model
# ------------------------------------------
# The projection operation is idempotent: if this geometry is already
# projected onto the GeomAI model, the existing projection is returned.

print("Running projection...")
projection = geometry.run_projection(workspace)
projection.wait()

latent_parameters = projection.get_latent_parameters()
print(f"Projection {projection.id} on model {projection.workspace_id}")
print(f"Retrieved {len(latent_parameters)} latent parameters")

###############################################################################
# Regenerate the geometry from its latent parameters
# --------------------------------------------------
# Pass the latent parameters to a prediction configuration to regenerate
# the geometry with the GeomAI model.

config = GeomAIPredictionConfiguration(
    latent_params=latent_parameters,
)
prediction = geomai_client.predictions.run(config, workspace)
print(f"Prediction {prediction.id} started...")
prediction.wait()

output_path = f"reconstructed_{prediction.id}.vtp"
geomai_client.predictions.download(prediction.id, output_path)
print(f"Saved reconstructed geometry to {output_path}")


###############################################################################
# Get an existing projection of the geometry
# ------------------------------------------
# Get a projection without starting a new computation. The result is
# ``None`` if the geometry is not projected onto the GeomAI model of this workspace.

print("\nLooking up an existing projection...")
existing_projection = geometry.get_projection(workspace)
if existing_projection is None:
    print("Geometry has not yet been projected onto this workspace's model.")
else:
    print(f"Existing projection: {existing_projection.id}")
    print(f"First three parameters: {existing_projection.get_latent_parameters(n=3)}")

###############################################################################
# List the projections in the GeomAI model workspace
# --------------------------------------------------

projections = workspace.list_projections()
print(f"\n{len(projections)} projections in {workspace.name}")
for proj in projections:
    print(f"- {proj.id}")

###############################################################################
# Generate geometries from the projected latent parameters
# --------------------------------------------------------
# To explore the GeomAI model further, you can:
#
# - Generate geometries from latent parameters: :ref:`ref_generate_random_geometries`.
# - Interpolate between geometries: :ref:`ref_interpolate_geometries`.
#
# For the complete task, see :doc:`/user-guide/geomai-models/interpolate-and-project`.
