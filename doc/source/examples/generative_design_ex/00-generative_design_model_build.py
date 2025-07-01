""".. _ref_generative_design_model_build_reuse:

Script 1 - Building a model to generate new designs
===================================================

This example demonstrates how to configure, train and build a model that will generate new designs.

"""

###############################################################################
# Import necessary libraries
# --------------------------

import os

import ansys.simai.core
from ansys.simai.core.data.geomai.models import GeomAIModelConfiguration
from ansys.simai.core.errors import NotFoundError

###############################################################################
# Create the client
# -----------------
# Create a client to use the PySimAI library. This client will be the
# entrypoint of all "SimAI" and "GeomAI" objects.

simai = ansys.simai.core.SimAIClient(organization="my_organization")

###############################################################################
# Configure the client
# --------------------
# Generative design objects are not part of a separate client to instantiate
# — they are exposed via the `geomai` property of a configured SimAIClient.

client = simai.geomai


###############################################################################
# Find or create a "GeomAI" Project
# ---------------------------------
# List all the projects available in the client instance:

print(client.projects.list())


###############################################################################
# Retrieve your project by its name or create it if it does not exist:

my_dataset_path = "path/to/your/data/folder"
my_project_name = "new-bracket-project"

try:
    project = client.projects.get(name=my_project_name)
except NotFoundError:
    project = client.projects.create(my_project_name)


###############################################################################
# Set the retrieved project as the current project:

client.set_current_project(my_project_name)
print(client.current_project)


###############################################################################
# Add the training data to the current project
# --------------------------------------------
# Display the number of data in the current project and list them all:

print(len(project.data()))
print(project.data())


###############################################################################
# To add the training data to the current project:
#
# - | If the training data has never been uploaded to the server,
#   | use the following script:

for geometry_data_name in os.listdir(my_dataset_path):
    geometry_data_file = os.path.join(my_dataset_path, geometry_data_name)
    try:
        td = client.training_data.create_from_file(file=geometry_data_file, project=project)
        print(f"Uploaded {geometry_data_name} -> ID: {td.id}")
    except Exception as e:
        print(f"Failed to upload {geometry_data_name}: {e}")

for data in project.data():
    print(data.name)


###############################################################################
# - If the training data already exists on the server, do as follows:
#
# Step 1. Get the project by name:

project_with_TD = client.projects.get(name="bracket-project")

###############################################################################
# Step 2. Get all training data in that project:

data_items = project_with_TD.data()

###############################################################################
# Step 3. Print the desired number of training data to add:
# (5 in this example)

for td in data_items[:5]:
    print(f"{td.id}: {td.name}")

training_data_list = data_items[:5]

###############################################################################
# Step 4. Add each data item to the current project:

for td in training_data_list:
    try:
        td.add_to_project(project)
        print(f"✅ Added {f'{td.id}: {td.name}'} to current project.")
    except Exception as e:
        print(f"❌ Failed to add {f'{td.id}: {td.name}'}: {e}")


###############################################################################
# Remove data from the project
# ----------------------------
# Use the script below to remove data from the project:

for data in project.data():
    try:
        data.remove_from_project(project)
        print(f"Removed: {data.name}")
    except Exception as e:
        print(f"Could not remove {data.name}: {e}")


###############################################################################
# Check the result of the removal by displaying the number of data in the
# current project and listing them all:

print(len(project.data()))
print(project.data())


###############################################################################
# Set a model configuration for the newly created project and build the model
# ---------------------------------------------------------------------------


###############################################################################
# Create a model configuration:

configuration = GeomAIModelConfiguration(
    nb_epochs=2,
    # or build_preset: 'debug', 'short', 'default' or 'long'
    nb_latent_param=2,  # Required: Must be between 2 and 256
)

###############################################################################
# Build the model:

model = simai.geomai.models.build(project, configuration)

###############################################################################
# Print the result:

print(f"Model started: {model.id} in project {project.name}")
