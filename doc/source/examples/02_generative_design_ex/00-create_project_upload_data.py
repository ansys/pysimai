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

""".. _ref_create_project_upload_data:

Creating a GeomAI Project and Uploading Training Data
===========================================================

This example demonstrates how to connect to the instance, create a new project, and upload geometry files as training data.

Before you begin
-------------------------------------------

Make sure you have:

- Valid SimAI credentials and organization access.
- A folder containing geometry files (.vtp or .stl format).
- The ``ansys-simai-core`` library installed.

"""

###############################################################################
# Import necessary libraries
# -------------------------------------------

import os

import ansys.simai.core as asc
from ansys.simai.core.errors import NotFoundError

###############################################################################
# Configure your settings
# -------------------------------------------
# Update these variables with your specific settings:
ORGANIZATION = "my_organization"  # Replace with your organization name
DATASET_PATH = "path/to/your/data/folder"  # Folder with .vtp or .stl files
PROJECT_NAME = "your_project_name"  # Replace with your project name

###############################################################################
# Create the client
# -------------------------------------------
# Create a client to use the PySimAI library. This client will be the
# entrypoint for all Generative Design objects.

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai

###############################################################################
# Create or retrieve a project
# -------------------------------------------
# Try to get an existing project by name, or create it if it does not exist:

try:
    project = geomai_client.projects.get(name=PROJECT_NAME)
    print(f"Using existing project: {PROJECT_NAME}")
except NotFoundError:
    project = geomai_client.projects.create(PROJECT_NAME)
    print(f"Created new project: {PROJECT_NAME}")

###############################################################################
# Upload training data to the project
# -------------------------------------------
# Loop through all geometry files in your dataset folder and upload them.
# Each file should be a .vtp or .stl geometry.
#
# .. note::
#    If training data with the same name already exists, it is added to the
#    project without re-uploading.

print("\nUploading training data files:")

for fname in os.listdir(DATASET_PATH):
    td_name = os.path.splitext(fname)[0]
    fpath = os.path.join(DATASET_PATH, fname)

    # Skip non-geometry files
    if not fname.lower().endswith((".vtp", ".stl")):
        continue

    # Skip if already uploaded
    try:
        existing_td = geomai_client.training_data.get(name=td_name)
        print(f"  '{fname}' already exists, adding to project.")
        existing_td.add_to_project(project)
        continue
    except NotFoundError:
        pass

    print(f"  Uploading '{fname}'...")
    training_data = geomai_client.training_data.create_from_file(file=fpath, project=project)
    print(f"  '{fname}' uploaded (ID: {training_data.id}).")

print("\nAll training data uploaded.")

###############################################################################
# Wait for data processing
# -------------------------------------------
# After uploading, the instance processes the geometries.
# Wait for all data in the project to be ready.
#
# .. note::
#    An "invalid geometry" failure means the geometry is not compatible with
#    Generative Design. Check the file for watertightness and manifold issues.

project_data = project.list_training_data()

print("\nWaiting for data processing to complete...")
for data in project_data:
    print(f"  Processing '{data.name}'...")
    data.wait()

    if data.is_ready:
        print(f"  '{data.name}' is ready.")
    else:
        print(f"  '{data.name}' failed: {data.failure_reason}")

###############################################################################
# Display project summary
# -------------------------------------------

ready_count = sum(1 for d in project_data if d.is_ready)
print(f"\nProject '{PROJECT_NAME}': {ready_count}/{len(project_data)} training data ready.")

###############################################################################
# Next steps
# -------------------------------------------
# Once all data is ready, you can proceed to build a model.
# See the next example: :ref:`ref_build_model`.
