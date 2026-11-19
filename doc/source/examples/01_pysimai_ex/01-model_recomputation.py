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

Rebuild a SimAI model with the latest model configuration
=========================================================

This example starts a new SimAI model build in a project with the latest
model configuration of that same project.

"""

###############################################################################
# Import PySimAI and create the client to rebuild a SimAI model
# -------------------------------------------------------------

import ansys.simai.core as asc

simai_client = asc.from_config()

###############################################################################
# Get the project of the SimAI model to rebuild
# ---------------------------------------------

my_project = simai_client.projects.get(name="old-ps")

###############################################################################
# Get the latest model configuration of the project
# -------------------------------------------------
# Get the latest model configuration of the project.

last_build_config = my_project.last_model_configuration

###############################################################################
# Check that the project is trainable before the SimAI model rebuild
# ------------------------------------------------------------------
# Check that the project meets the requirements for a model build.

is_trainable_check = my_project.is_trainable()

###############################################################################
# If the project meets the requirements, start the model build.
# Otherwise, print the reason why the project does not meet the requirements.
if is_trainable_check:
    new_model = simai_client.models.build(last_build_config)
else:
    print(is_trainable_check.reason)

###############################################################################
# Monitor and evaluate the rebuilt SimAI model
# --------------------------------------------
# For the complete tasks, see :doc:`/user-guide/simai-models/build-a-model` and
# :doc:`/user-guide/simai-models/evaluate-a-model`.
