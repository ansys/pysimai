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

Create a project and upload training data for a SimAI model
===========================================================

This example creates a project in Ansys SimAI, uploads simulation folders as training data
for a SimAI model, and waits for Ansys SimAI to process the training data.

Prerequisites to upload training data for a SimAI model
-------------------------------------------------------

Make sure you have:

- Valid Ansys SimAI credentials and access to an organization.
- A dataset folder that contains one simulation folder per training data point.
- The ``ansys-simai-core`` library installed.

"""

###############################################################################
# Import the modules to upload SimAI model training data
# ------------------------------------------------------

import os

import ansys.simai.core as asc
from ansys.simai.core.errors import ProcessingError
from ansys.simai.core.errors import NotFoundError

###############################################################################
# Set the project and dataset path for the SimAI model training data
# ------------------------------------------------------------------
# Replace these values with your own:

ORGANIZATION_NAME = "your_organization"  # Replace with your organization name
PROJECT_NAME = "your_project_name"  # Your project name
DATASET_PATH = "path/to/your/data/folder"  # Directory containing subdirectories with training data

###############################################################################
# Create the PySimAI client to upload SimAI model training data
# -------------------------------------------------------------
# Create a client that connects to Ansys SimAI:

simai_client = asc.SimAIClient(organization=ORGANIZATION_NAME)

###############################################################################
# Get or create the project for the SimAI model
# ---------------------------------------------
# Try to get an existing project by name, or create it if it does not exist:

try:
    project = simai_client.projects.get(name=PROJECT_NAME)
    print(f"Using existing project: {PROJECT_NAME}")
except NotFoundError:
    project = simai_client.projects.create(PROJECT_NAME)
    print(f"Created new project: {PROJECT_NAME}")

###############################################################################
# Upload the simulation folders as SimAI model training data
# ----------------------------------------------------------
# Upload all subdirectories of the dataset path as training data.
# Each subdirectory is a simulation folder that contains the files of one
# training data point.
#
# .. note::
#    If training data with the same name already exists, the API raises an error.
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
# Wait for Ansys SimAI to process the SimAI model training data
# -------------------------------------------------------------
# After the upload, Ansys SimAI processes the training data.
# Wait for all training data points in the project to be ready.

project_data = project.list_training_data()

print("\nWaiting for data processing to complete...")
for data in project_data:
    print(f"  Processing '{data.name}'...")
    # wait() raises ProcessingError if the processing of the data fails.
    try:
        data.wait()
        print(f"  '{data.name}' is ready.")
    except ProcessingError:
        print(f"  '{data.name}' failed: {data.failure_reason}")

###############################################################################
# Print how many SimAI model training data points are ready
# ---------------------------------------------------------

ready_count = sum(1 for d in project_data if d.is_ready)
print(f"\nProject '{PROJECT_NAME}': {ready_count}/{len(project_data)} training data ready.")

###############################################################################
# Build a SimAI model from the uploaded training data
# ---------------------------------------------------
# When all training data points are ready, configure and build a SimAI model:
# :ref:`ref_basic_build_model`.
#
# For the complete task, see :doc:`/user-guide/simai-models/upload-training-data`.
