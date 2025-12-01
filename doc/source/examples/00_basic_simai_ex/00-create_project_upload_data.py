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

""".. _ref_basic_create_project_upload_data:

Creating a SimAI Project and Uploading Training Data
=======================================================

This example demonstrates how to connect to SimAI, create a new project, and upload training data folders.

Before you begin
-------------------

Make sure you have:

- Valid SimAI credentials and organization access.
- A dataset folder containing subdirectories with your training data.
- The ansys-simai-core library installed.

"""

###############################################################################
# Import necessary libraries
# ----------------------------------

import os

import ansys.simai.core as asc
from ansys.simai.core.data.training_data import TrainingData
from ansys.simai.core.errors import NotFoundError

###############################################################################
# Configure your settings
# ----------------------------------
# Update these variables with your specific settings:

ORGANIZATION_NAME = "<your_organization>"  # Replace with your organization name
PROJECT_NAME = "<your_project_name>"  # Your desired project name
DATASET_PATH = "<PATH_TO_YOUR_DATASET>"  # Directory containing subdirectories with training data

###############################################################################
# Initialize the SimAI client
# ----------------------------------
# Create a client to connect to the SimAI platform:

simai_client = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Set up the project
# ----------------------------------
# Try to get an existing project by name, or create it if it doesn't exist:

try:
    project = simai_client.projects.get(name=PROJECT_NAME)
    print(f"Using existing project: {PROJECT_NAME}")
except NotFoundError:
    project = simai_client.projects.create(PROJECT_NAME)
    print(f"Created new project: {PROJECT_NAME}")

###############################################################################
# Set as the current working project
# ----------------------------------
# Setting the current project allows subsequent operations to default to this project:

simai_client.set_current_project(PROJECT_NAME)
print(f"Current project: {simai_client.current_project}")

###############################################################################
# Upload training data
# ----------------------------------
# Upload all directories from the dataset path as training data.
# Each subdirectory should contain the files for one training data sample.


available_tds = simai_client.training_data.list()

print("\nUploading training data files:")
successful_uploads = 0
failed_uploads = 0

for dir in os.listdir(DATASET_PATH):
    complete_path = os.path.join(DATASET_PATH, dir)
    print(f"Uploading {dir}")

    existing_tds = [td for td in available_tds if td.name == dir]
    if existing_tds:
        print(f"Training data '{dir}' already exists in the datalake. Skipping upload.")
        td = existing_tds[0]
        try:
            td.add_to_project(project)
            print(f"✓ Added existing '{dir}' to project '{project.name}'")
            successful_uploads += 1
        except Exception as e:
            print(f"✗ Failed to add existing '{dir}' to project: {e}")
            failed_uploads += 1
        continue
    else:
        try:
            td: TrainingData = simai_client.training_data.create(dir)
            td.upload_folder(complete_path)
            print(f"Uploaded {dir} successfully.")
        except Exception as e:
            print(f"Failed to upload {dir}: {e}")
            failed_uploads += 1
            continue


print(f"\nUpload summary: {successful_uploads} successful, {failed_uploads} failed")

###############################################################################
# Check and wait for data processing
# -------------------------------------
# After uploading, SimAI needs to process the training data.
# Get all data in the current project and wait for them to be ready.

project_data = project.data

print("\nWaiting for data processing to complete...")
for data in project_data:
    print(f"Processing {data.name}...")
    data.wait()
    print(f"Data '{data.name}' is ready")

###############################################################################
# Display project status summary
# -------------------------------------
# Show a summary of the project's data processing status:

print("\nProject Summary")
print("=" * 50)

ready_data = [data for data in project_data if data.is_ready]
not_ready_data = [data for data in project_data if not data.is_ready]

print(f"Total data in project: {len(project_data)}")
print(f"Ready data: {len(ready_data)} of {len(project_data)}")
print(f"Not ready data: {len(not_ready_data)} of {len(project_data)}")

if not_ready_data:
    print("\nFailed data processing details:")
    for data in not_ready_data:
        print(f"- {data.name}: {data.failure_reason}")

###############################################################################
# Next steps
# ----------------------------------
# Once all data are ready, you can proceed to configure and build a model.
# See the next tutorial: :ref:`ref_basic_build_model`
