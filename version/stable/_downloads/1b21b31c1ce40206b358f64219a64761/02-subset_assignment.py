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

"""
.. _ref_subset_assignment:

Subset assignment
=================

This example demonstrates how to assign a subset
to a training data.

"""

###############################################################################
# Import necessary libraries
# --------------------------

import ansys.simai.core as asc

simai = asc.from_config()

###############################################################################
# Select a training data
# ----------------------
# Example of a training_data_id associated with a project_id.

training_data_id = "k4z77qzq"
project_id = "k9756vw0"

###############################################################################
# Get subset assignment
# ---------------------
# Get and print the current subset assigned for this training_data_id.

current_subset = simai.training_data.get(id=training_data_id).get_subset(project=project_id)
print(current_subset)

###############################################################################
# Assign a new subset (two options)
# ---------------------------------
# Manually assign a new subset to the training data.

simai.training_data.get(id=training_data_id).assign_subset(project=project_id, subset="Test")

###############################################################################
# Alternatively, use SubsetEnum to assign a valid enum value to the training data.

from ansys.simai.core.data.types import SubsetEnum

simai.training_data.get(id=training_data_id).assign_subset(
    project=project_id, subset=SubsetEnum.TEST
)
