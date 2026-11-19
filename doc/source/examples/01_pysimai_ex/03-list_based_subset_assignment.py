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
.. _ref_list_based_subset_assignment:

Assign subsets from a list of training data points for a SimAI model
====================================================================

This example splits the training data of a SimAI model project between the Test
and Training subsets with a list of the training data points to test.

"""

###############################################################################
# Import PySimAI to assign subsets from a list
# --------------------------------------------

import ansys.simai.core as asc

###############################################################################
# List the training data points of the Test subset
# ------------------------------------------------
# List the names of the training data points to assign to the Test subset.

# CAUTION:
# Every training data point that is not in the following list is
# assigned to the Training subset.
TEST_LIST = ["My_td_1", "My_td_2"]

###############################################################################
# Connect to Ansys SimAI and get the SimAI model project
# ------------------------------------------------------
# Connect to Ansys SimAI. To change how the client authenticates,
# see :ref:`anchor-credentials`.

simai_client = asc.SimAIClient(organization="My_organization_name")
project = simai_client.projects.get(name="My_project_name")
###############################################################################
# Assign the Test or Training subset to each training data point
# --------------------------------------------------------------
# Assign the Test subset to the training data points in the list and the
# Training subset to all other training data points.

td_list = project.list_training_data()
for td in td_list:
    if td.name in TEST_LIST:
        td.assign_subset(project, "Test")
    else:
        td.assign_subset(project, "Training")

###############################################################################
# Learn more about subsets of SimAI model training data
# -----------------------------------------------------
# For the complete task, see :doc:`/user-guide/simai-models/assign-subsets`.
