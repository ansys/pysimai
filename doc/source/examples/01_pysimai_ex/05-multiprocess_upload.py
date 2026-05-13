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

""".. _ref_multiprocess_upload:

Multiprocess training data upload
==================================

**When to use**: uploading a large dataset (hundreds of folders)
where sequential uploads are too slow. By spawning several worker processes,
each with its own SimAI connection, transfers run in parallel and overall
upload time scales down with the number of workers.

For standard datasets, you can refer to :ref:`ref_basic_create_project_upload_data`.

The script compares the local folder list against what is already in the project
and only uploads the missing items, so it is safe to re-run after an interruption
without creating duplicates.

Before you begin
--------------------------------

Make sure you have:

- Valid SimAI credentials and organization access.
- A dataset folder where each subdirectory is one training data sample
  (the layout expected by :meth:`upload_folder()<ansys.simai.core.data.training_data.TrainingDataDirectory.upload_folder>`).
- The ``ansys-simai-core`` library installed.

"""

###############################################################################
# Configure your settings
# --------------------------------
# Update these variables before running the script:

import os
from multiprocessing import Pool

import ansys.simai.core as asc

ORGANIZATION_NAME = "<your_organization_name>"
PROJECT_NAME = "<your_project_name>"
DATASET_PATH = "<path_to_your_dataset_folder>"

# Maximum number of parallel upload workers
MAX_PROCESSES = 2
# Number of items dispatched to each worker at a time
MAX_CHUNK = 2

###############################################################################
# Initialize the SimAI client and get the project
# ----------------------------------------------------

simai = asc.SimAIClient(organization=ORGANIZATION_NAME)
project = simai.projects.get(name=PROJECT_NAME)

###############################################################################
# Build the list of items to upload
# ----------------------------------
# Compare the local folder contents against what is already in the project
# and keep only the items that are missing.

all_items = os.listdir(DATASET_PATH)
existing_names = {td.name for td in project.data}
items_to_upload = [item for item in all_items if item not in existing_names]

print(f"Dataset size   : {len(all_items)}")
print(f"Already present: {len(all_items) - len(items_to_upload)}")
print(f"To upload      : {len(items_to_upload)}")

###############################################################################
# Define upload functions for multiprocessing
# ------------------------------------------------------
# Each worker process receives its own SimAI client so that connections are
# not shared across processes.
# A module-level dict is used to store per-worker state.

_worker: dict = {}


def _initializer(organization: str, dataset_path: str, project_name: str) -> None:
    """Set up per-worker state used by every worker in the pool."""
    _worker["simai"] = asc.SimAIClient(organization=organization)
    _worker["project"] = _worker["simai"].projects.get(name=project_name)
    _worker["dataset_path"] = dataset_path


def _upload_one(item_name: str) -> str:
    """Create a training-data entry and upload the matching local folder."""
    simai = _worker["simai"]
    project = _worker["project"]
    dataset_path = _worker["dataset_path"]
    training_data = simai.training_data.create(item_name, project)
    simai.training_data.upload_folder(
        training_data, folder_path=os.path.join(dataset_path, item_name)
    )
    return item_name


###############################################################################
# Run the parallel upload
# --------------------------------

if items_to_upload:
    with Pool(
        processes=MAX_PROCESSES,
        initializer=_initializer,
        initargs=(ORGANIZATION_NAME, DATASET_PATH, PROJECT_NAME),
    ) as pool:
        for completed in pool.imap(_upload_one, items_to_upload, chunksize=MAX_CHUNK):
            print(f"Uploaded: {completed}")
else:
    print("Nothing to upload — project is already up to date.")

print("Upload complete.")
