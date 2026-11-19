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

"""
.. _ref_subset_assignment:

Assign a subset to a SimAI model training data point
====================================================

This example assigns the Test or Training subset to one training data point
of a SimAI model project.

"""

###############################################################################
# Import PySimAI and create the client to assign a subset
# -------------------------------------------------------

import ansys.simai.core as asc

simai_client = asc.from_config()

###############################################################################
# Set the IDs of the training data point and its project
# ------------------------------------------------------
# Replace these example IDs with the ID of a training data point and the ID
# of a project that contains it.

training_data_id = "k4z77qzq"
project_id = "k9756vw0"

###############################################################################
# Get the current subset of the training data point
# -------------------------------------------------
# Get and print the subset assigned to the training data point in the project.

current_subset = simai_client.training_data.get(id=training_data_id).get_subset(project=project_id)
print(current_subset)

###############################################################################
# Assign a new subset to the training data point
# ----------------------------------------------
# Assign the subset by its name, as a string:

simai_client.training_data.get(id=training_data_id).assign_subset(project=project_id, subset="Test")

###############################################################################
# Alternatively, assign the subset with a ``SubsetEnum`` value:

from ansys.simai.core.data.types import SubsetEnum

simai_client.training_data.get(id=training_data_id).assign_subset(
    project=project_id, subset=SubsetEnum.TEST
)

###############################################################################
# Assign subsets to many SimAI model training data points
# -------------------------------------------------------
# To assign subsets from a list of names, see :ref:`ref_list_based_subset_assignment`.
#
# For the complete task, see :doc:`/user-guide/simai-models/assign-subsets`.
