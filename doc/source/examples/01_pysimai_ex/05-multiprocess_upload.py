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

This example demonstrates how to upload training data to a SimAI project using
multiple parallel processes. It skips items that are already present in the
project, so it is safe to run repeatedly without creating duplicates.

Before you begin
----------------

Make sure you have:

- Valid SimAI credentials and organization access.
- A dataset folder where each subdirectory is one training data sample.
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
# Define upload functions for multiprocessing
# --------------------------------------------
# ``_worker`` holds per-worker state (one SimAI client per process).
# The initializer sets up the SimAI client and project for each worker process.
# The upload function uploads one item and returns any error message instead of
# raising exceptions, so that one failure does not abort the whole batch.

_worker: dict = {}


def _initializer(organization: str, dataset_path: str, project_name: str) -> None:
    """Set up per-worker state. Called once per worker process at pool start."""
    _worker["simai"] = asc.SimAIClient(organization=organization)
    _worker["project"] = _worker["simai"].projects.get(name=project_name)
    _worker["dataset_path"] = dataset_path


def _upload_one(item_name: str) -> tuple[str, str | None]:
    """Upload one training-data folder.

    Returns a ``(item_name, error_message)`` tuple so that a single failed
    upload does not abort the rest of the batch.
    """
    try:
        simai = _worker["simai"]
        project = _worker["project"]
        dataset_path = _worker["dataset_path"]
        training_data = simai.training_data.create(item_name, project)
        simai.training_data.upload_folder(
            training_data, folder_path=os.path.join(dataset_path, item_name)
        )
        return item_name, None
    except Exception as exc:  # noqa: BLE001
        return item_name, str(exc)


###############################################################################
# Main entry point
# ----------------
# All SimAI calls and pool creation are inside ``main()`` and guarded by
# ``if __name__ == "__main__"``.  This prevents worker processes from
# re-executing the setup logic when they import this module on Windows/macOS.


def main() -> None:
    """Run the parallel upload."""
    simai = asc.SimAIClient(organization=ORGANIZATION_NAME)
    project = simai.projects.get(name=PROJECT_NAME)

    # Compare the local folder contents against what is already in the project
    # and keep only the items that are missing.
    all_items = os.listdir(DATASET_PATH)
    existing_names = {td.name for td in project.list_training_data()}
    items_to_upload = [item for item in all_items if item not in existing_names]

    print(f"Dataset size   : {len(all_items)}")
    print(f"Already present: {len(all_items) - len(items_to_upload)}")
    print(f"To upload      : {len(items_to_upload)}")

    if not items_to_upload:
        print("Nothing to upload — project is already up to date.")
        return

    failed: list[str] = []

    with Pool(
        processes=MAX_PROCESSES,
        initializer=_initializer,
        initargs=(ORGANIZATION_NAME, DATASET_PATH, PROJECT_NAME),
    ) as pool:
        for item_name, error in pool.imap(_upload_one, items_to_upload, chunksize=MAX_CHUNK):
            if error is None:
                print(f"  Uploaded : {item_name}")
            else:
                print(f"  Failed   : {item_name} — {error}")
                failed.append(item_name)

    if failed:
        print(f"\n{len(failed)} item(s) failed: {failed}")
    else:
        print("\nUpload complete — all items uploaded successfully.")


if __name__ == "__main__":
    main()
