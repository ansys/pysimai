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

""".. _ref_basic_create_project_upload_data:

Creating a SimAI Project and Uploading Training Data
=======================================================

This example demonstrates how to connect to SimAI, create a new project, and upload training data folders.

Before you begin
-------------------

Make sure you have:

- Valid SimAI credentials and organization access.
- A dataset folder containing subdirectories with your training data.
- The ``ansys-simai-core`` library installed.

"""

###############################################################################
# Import necessary libraries
# ----------------------------------

import os

import ansys.simai.core as asc
from ansys.simai.core.errors import NotFoundError

###############################################################################
# Configure your settings
# ----------------------------------
# Update these variables with your specific settings:

ORGANIZATION_NAME = "your_organization"  # Replace with your organization name
PROJECT_NAME = "your_project_name"  # Your project name
DATASET_PATH = "path/to/your/data/folder"  # Directory containing subdirectories with training data

###############################################################################
# Initialize the SimAI client
# ----------------------------------
# Create a client to connect to the SimAI platform:

simai_client = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Set up the project
# ----------------------------------
# Try to get an existing project by name, or create it if it does not exist:

try:
    project = simai_client.projects.get(name=PROJECT_NAME)
    print(f"Using existing project: {PROJECT_NAME}")
except NotFoundError:
    project = simai_client.projects.create(PROJECT_NAME)
    print(f"Created new project: {PROJECT_NAME}")

###############################################################################
# Set as the current working project
# ----------------------------------
# Setting the current project allows subsequent operations to use this project by default:

simai_client.set_current_project(PROJECT_NAME)
print(f"Current project: {simai_client.current_project}")

###############################################################################
# Upload training data
# ----------------------------------
# Upload all directories from the dataset path as training data.
# Each subdirectory should contain the files for one training data sample.

print("\nUploading training data files:")
successful_uploads = 0
failed_uploads = 0

for dir_name in os.listdir(DATASET_PATH):
    complete_path = os.path.join(DATASET_PATH, dir_name)
    if not os.path.isdir(complete_path):
        continue

    print(f"\nProcessing '{dir_name}'...")

    # Check if training data with this name already exists
    try:
        existing_td = simai_client.training_data.get(name=dir_name)
    except NotFoundError:
        existing_td = None

    if existing_td:
        # Data already exists on the platform, add it to the project.
        print(f"  Training data '{dir_name}' already exists. Adding to project.")
        try:
            existing_td.add_to_project(project)
            successful_uploads += 1
        except Exception as e:
            print(f"  Failed to add '{dir_name}' to project: {e}")
            failed_uploads += 1
        continue
        # Alternative actions for existing data:
        #   - Skip entirely:  continue
        #   - Delete and re-upload:  existing_td.delete()  (then let it fall through)

    # Upload new training data
    try:
        td = simai_client.training_data.create(dir_name, project=project)
        td.upload_folder(complete_path)
        successful_uploads += 1
        print(f"  Uploaded '{dir_name}' successfully.")
    except Exception as e:
        print(f"  Failed to upload '{dir_name}': {e}")
        failed_uploads += 1


print(f"\nUpload summary: {successful_uploads} successful, {failed_uploads} failed")

###############################################################################
# Check and wait for data processing
# -------------------------------------
# After uploading, SimAI needs to process the training data.
# Get all data in the current project and wait for them to be ready.

project_data = project.list_training_data()

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
