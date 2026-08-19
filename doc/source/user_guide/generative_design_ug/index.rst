.. _ref_generative_design_guide:

Generate new designs
========================================================

With SimAI, you generate new geometries based on existing ones using Generative Design (GeomAI).

.. note::
   GeomAI is designed to **generate geometries**. It does not use physical response data (forces,
   flow fields, pressure, etc.) and cannot predict them. If your goal is to predict physical
   responses from geometries, use SimAI instead.

The principle is that:

- Given a dataset of geometries provided by you,
- The AI model is trained to find a compressed representation of those geometries (the latent space).
- Once the representation is computed, the model can generate new geometries by working in this
  compressed representation space.

**Key concepts**

A **project** holds your training data — the set of geometries the model learns from.
A **workspace** holds a trained model and its predictions. One project can have multiple workspaces,
each corresponding to a different build configuration.

The steps to follow are:

1. Prepare and validate your geometries
#. Upload them as training data and assign them to a project
#. Configure and build your AI model
#. Evaluate the model quality
#. Generate new designs and integrate them into your workflow

.. tip::
   Start with a small number of training geometries and the ``short`` build preset to quickly check
   if the model can learn and if the generated designs are meaningful.
   This helps detect issues early and saves time.

   If the model performs well on the small set, you can scale up with the ``default`` or ``long``
   build presets, depending on the complexity of the geometries used as training data.

For practical examples and scripts to execute yourself, see :ref:`ref_examples`.

.. toctree::
   :maxdepth: 2

   data_preparation
   model_setup_and_goals
   evaluation_and_workflows