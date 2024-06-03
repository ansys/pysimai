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
# Example of a training_data_id associated with a project_id

training_data_id = "k4z77qzq"
project_id = "k9756vw0"

###############################################################################
# Get subset assignment
# ---------------------
# Get the current subset assigned for this training_data_id.

simai.training_data.get(id=training_data_id).get_subset(project=project_id)

###############################################################################
# Assign a new subset (two options)
# ---------------------------------
# Manually assign a new subset to the training data.

simai.training_data.get(id=training_data_id).assign_subset(project=project_id, subset="Validation")

###############################################################################
# Use SubsetEnum to assign a valid enum value to the training data.

from ansys.simai.core.data.types import SubsetEnum
simai.training_data.get(id=training_data_id).assign_subset(project=project_id, subset=SubsetEnum.VALIDATION)