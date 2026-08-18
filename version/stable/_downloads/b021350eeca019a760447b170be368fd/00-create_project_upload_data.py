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
# Upload training data
# ----------------------------------
# Upload all directories from the dataset path as training data.
# Each subdirectory should contain the files for one training data sample.
#
# .. note::
#    If training data with the same name already exists, the API will raise an error.
#    You can use ``simai_client.training_data.get(name=dir_name)`` to check beforehand.

print("\nUploading training data files:")

for dir_name in os.listdir(DATASET_PATH):
    complete_path = os.path.join(DATASET_PATH, dir_name)
    if not os.path.isdir(complete_path):
        continue

    # Skip if already uploaded
    try:
        existing_td = simai_client.training_data.get(name=dir_name)
        print(f"  '{dir_name}' already exists, adding to project.")
        existing_td.add_to_project(project)
        continue
    except NotFoundError:
        pass

    print(f"  Uploading '{dir_name}'...")
    td = simai_client.training_data.create(dir_name, project=project)
    td.upload_folder(complete_path)
    print(f"  '{dir_name}' uploaded successfully.")

print("\nAll training data uploaded.")

###############################################################################
# Wait for data processing
# -------------------------------------
# After uploading, SimAI processes the training data.
# Wait for all data in the project to be ready.

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
# -------------------------------------

ready_count = sum(1 for d in project_data if d.is_ready)
print(f"\nProject '{PROJECT_NAME}': {ready_count}/{len(project_data)} training data ready.")

###############################################################################
# Next steps
# ----------------------------------
# Once all data are ready, you can proceed to configure and build a model.
# See the next tutorial: :ref:`ref_basic_build_model`
