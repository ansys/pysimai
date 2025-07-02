""".. _ref_design_generation_reuse:

Script 2 - Generating new designs with the model
================================================

This example demonstrates how to generate new designs.

Before you begin
----------------

- Make sure you performed ":ref:`ref_generative_design_model_build_reuse`".

or

- | Make sure you:
  | 1. instantiated a client with GeomAI objects,
  | 2. created a project and added training data to it,
  | 3. created a model configuration and built a model.

"""

###############################################################################
# Import necessary libraries
# --------------------------

import ansys.simai.core
from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration

###############################################################################
# Create the client
# -----------------
# Create a client to use the PySimAI library. This client will be the
# entrypoint of all "SimAI" and "GeomAI" objects.

simai = ansys.simai.core.SimAIClient(organization="my_organization")
client = simai.geomai


###############################################################################
# Retrieve your workspace
# -----------------------
# Find the workspace your model has been saved to and set it as a
# current workspace:
#

###############################################################################
# Step 1. Set the current project:

client.set_current_project("new-bracket-project")

###############################################################################
# Step 2. Retrieve all the workspaces of the current project:

print(client.current_project.workspaces())

###############################################################################
# Step 3. Setting the current workspace:

client.set_current_workspace("new-bracket-project #1")
workspace = client.current_workspace
print(workspace)


###############################################################################
# Set up the parameters and run your prediction
# ---------------------------------------------

###############################################################################
# Configure the prediction:

configuration = GeomAIPredictionConfiguration(latent_params=[1, 1], resolution=(100, 100, 100))

###############################################################################
# Run the prediction:

prediction = client.predictions.run(configuration, workspace)

###############################################################################
# Check the status of your prediction:

if prediction.is_ready:
    print("✅ Prediction is ready!")
else:
    print("⏳ Prediction is not ready yet.")

print(prediction)


###############################################################################
# Download your prediction for further analysis and visualization
# ---------------------------------------------------------------
# To download your file, please indicate the ID of the prediction
# and the path to the desired storage location.
#

print(client.predictions.list(client.workspaces.list()[0]))

client.predictions.download("your_prediction_id", r"path/to/your/predictions/folder/output1.vtp")

###############################################################################
# The downloaded geometry can be now used as a SimAI training data or
# as an input for the SimAI prediction!
