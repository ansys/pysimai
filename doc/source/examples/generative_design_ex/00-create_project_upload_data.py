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
PROJECT_NAME = "new-bracket-project"  # Your project name

###############################################################################
# Create the client
# -------------------------------------------
# Create a client to use the PySimAI library. This client will be the
# entrypoint for all Generative Design objects.

simai_client = asc.SimAIClient(organization=ORGANIZATION)
geomai_client = simai_client.geomai


###############################################################################
# List all available training data:

print("\nAvailable training data:")
available_tds = geomai_client.training_data.list()

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

print(f"Current project: {project.name}")

###############################################################################
# Upload training data to the project
# -------------------------------------------
# Loop through all geometry files in your dataset folder and upload them.
# The script handles duplicates by checking if the data already exist.

print("\nUploading training data files:")
successful_uploads = 0
failed_uploads = 0

for fname in os.listdir(DATASET_PATH):
    td_name = os.path.splitext(fname)[0]
    fpath = os.path.join(DATASET_PATH, fname)

    # Skip non-geometry files
    if not fname.lower().endswith((".vtp", ".stl")):
        print(f"Skipping non-geometry file: {fname}")
        continue

    # Check if training data already exist
    existing_tds = [td for td in available_tds if td.name == td_name]
    if existing_tds:
        print(f"Training data '{fname}' already exists in the datalake. Skipping upload.")
        td = existing_tds[0]
        try:
            td.add_to_project(project)
            print(f"✓ Added existing '{fname}' to project '{project.name}'")
            successful_uploads += 1
        except Exception as e:
            print(f"✗ Failed to add existing '{fname}' to project: {e}")
            failed_uploads += 1
        continue

    # Upload new training data
    try:
        training_data = geomai_client.training_data.create_from_file(file=fpath, project=project)
        print(f"✓ Uploaded '{fname}' -> ID: {training_data.id}")
        successful_uploads += 1
    except Exception as e:
        print(f"✗ Failed to upload '{fname}': {e}")
        failed_uploads += 1

print(f"\nUpload summary: {successful_uploads} successful, {failed_uploads} failed")

###############################################################################
# Check and wait for data processing
# -------------------------------------------
# After uploading, the instance needs to process the geometries. This script
# displays the progress of the data processing.

project_data = project.data()


print("\nWaiting for data processing to complete...")
for data in project_data:
    print(f"Processing '{data.name}'...")
    data.wait()
    if data.is_ready:
        print(f"✓ Data '{data.name}' is ready")
    else:
        print(f"✗ Data '{data.name}' failed: {data.failure_reason}")

###############################################################################
# Display project status summary
# -------------------------------------------
# Show a summary of the project's data processing status:

project_data = project.data()

print("\nProject Summary")
print("=" * 50)
ready_data = [data for data in project_data if data.is_ready]
not_ready_data = [data for data in project_data if not data.is_ready]

print(f"Total data in project: {len(project_data)}")
print(f"Ready data: {len(ready_data)} of {len(project_data)}")
print(f"Not ready data: {len(not_ready_data)} of {len(project_data)}")

if not_ready_data:
    print(
        "\nFailed data processing details:\n"
        "Having an 'invalid geometry' means that the geometry is not compatible with Generative Design. "
        "Please check the geometry file for errors or issues (watertightness and manifold).\n"
    )
    for data in not_ready_data:
        print(f"- {data.name}: {data.failure_reason}")

###############################################################################
# Next steps
# -------------------------------------------
# Once all data is ready, you can proceed to build a model.
# See the next example: :ref:`ref_build_model`.
