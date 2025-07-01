.. _ref_generative_design_guide:

How to generate new designs using AI models
========================================================

With SimAI, you generate new geometries based on existing ones.

The steps to follow are:

1. Upload geometries to be used as trained data by your AI model
#. Assign those data to your project
#. Configure your AI model according to the data
#. Build your AI model
#. Generate new designs with previously built AI models
#. Export those geometries to check if they correspond to your expectations

.. tip::
   | Start with a small number of training geometries and the debug build preset to quickly check if the model can learn and if the generated designs are meaningful.
   | This helps detect issues early and saves time.

   If the model performs well on the small set, you can try the other build presets:
   short, default, long, depending on the complexity of the geometries used as training data.

.. toctree::
   :maxdepth: 2

   best_practices
   model_config_and_training
   generative_design