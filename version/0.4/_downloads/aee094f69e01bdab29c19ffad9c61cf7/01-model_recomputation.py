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
.. _ref_model_recomputation:

Model recomputation
===================

This example demonstrates how to relaunch a model build using the latest
model configuration in a same project.

"""

###############################################################################
# Import necessary libraries
# --------------------------

import ansys.simai.core as asc

simai_client = asc.from_config()

###############################################################################
# Get the project from the server
# -------------------------------

my_project = simai_client.projects.get(name="old-ps")

###############################################################################
# Get the model configuration
# ---------------------------
# Get the latest model configuration of the project.

last_build_config = my_project.last_model_configuration

###############################################################################
# Verify the project requirements
# -------------------------------
# Verify that the project meets the requirements for training (model building).

is_trainable_check = my_project.is_trainable()

###############################################################################
# If the project met the requirements, launch a model build.
# Otherwise, print the reasons the project does not meet the requirements.
if is_trainable_check:
    new_model = simai_client.models.build(last_build_config)
else:
    print(is_trainable_check.reason)
