"""
.. _ref_list_based_subset_assignment:

List-based subset assignment
============================

This example demonstrates how to distribute your dataset between Test,
Validation and Training subsets using lists.

"""

###############################################################################
# Import necessary libraries
# --------------------------
# Import SimAI core library and a logging module.

import logging

import ansys.simai.core

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

###############################################################################
# Create lists
# ------------
# List the data to be used for test and validation.

# CAUTION:
# All training data that are not included into the following lists will be
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
