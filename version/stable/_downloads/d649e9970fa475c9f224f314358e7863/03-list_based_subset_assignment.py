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
.. _ref_list_based_subset_assignment:

List-based subset assignment
============================

This example demonstrates how to distribute your dataset between Test
and Training subsets using lists.

"""

###############################################################################
# Import necessary libraries
# --------------------------

import ansys.simai.core

###############################################################################
# Create lists
# ------------
# List the data to be used for the test set.

# CAUTION:
# All training data that are not included into the following list will be
# assigned the training subset
TEST_LIST = ["My_td_1", "My_td_2"]

###############################################################################
# Connect to the platform
# ------------------------
# Connect to the SimAI platform. Refer to the :ref:`anchor-credentials`
# section of the documentation to adapt the connection type.

simai = ansys.simai.core.SimAIClient(organization="My_organization_name")
project = simai.projects.get(name="My_project_name")

###############################################################################
# Assign subsets
# --------------
# Assign a subset to each dataset (list) you created.

td_list = project.data
for td in td_list:
    if td.name in TEST_LIST:
        td.assign_subset(project, "Test")
    else:
        td.assign_subset(project, "Training")
