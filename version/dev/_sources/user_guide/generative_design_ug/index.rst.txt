.. _ref_generative_design_guide:

Generate new designs
========================================================

With GeomAI, you generate new geometries based on existing ones. The principle is that:

1. You provide a dataset of geometries.
2. The AI model is trained to find a compressed representation of those geometries (the latent space).
3. Once the representation is computed, the model can generate new geometries by working in this
   compressed representation space.

.. note::
   GeomAI is designed to **generate geometries**. It does not use physical response data (forces,
   flow fields, pressure, etc.) and cannot predict them. If your goal is to predict physical
   responses from geometries, use SimAI instead.

**Key concepts**

- A **project** holds your training data. The set of geometries the model learns from.
- A **workspace** holds a trained model and its predictions. One project can have multiple workspaces,
  each corresponding to a different build configuration.

The steps to follow are:

1. Prepare and validate your geometries.
#. Upload them as training data and assign them to a project.
#. Configure and train your AI model.
#. Evaluate the model quality.
#. Generate new designs and integrate them into your workflow.

For practical examples and scripts to execute yourself, see :ref:`ref_examples`.
Follow the user guide to have more explanation on each step.

.. toctree::
   :maxdepth: 2

   data_preparation
   model_setup_and_goals
   evaluation_and_workflows