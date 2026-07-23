.. _model_setup_geomai:

Model setup and training goals
==============================

Learn how to configure your model depending on the goal you want to achieve, and understand
the balance between reconstruction quality and interpolation quality.


Understanding reconstruction vs. interpolation
-----------------------------------------------

When training a GeomAI model, there is a fundamental trade-off between two objectives:

- **Reconstruction**: how well the model reproduces the exact training geometries.
- **Interpolation**: how well the model generates meaningful new geometries between known designs.

A model that perfectly reconstructs training data may overfit and produce poor interpolations.
Conversely, a model tuned for smooth interpolation may not perfectly reproduce every detail of your
original geometries.

Your choice of build preset directly influences where the model falls on this spectrum.


Build presets
-------------

Use the ``build_preset`` parameter to configure the training duration for building your model.

Available presets:

- ``debug``: 4 minutes + 15 seconds per geometry.
- ``short``: 45 minutes + 15 seconds per geometry.
- ``default``: 3 hours + 15 seconds per geometry.
- ``long``: 15 hours + 15 seconds per geometry.

Choosing the right preset
^^^^^^^^^^^^^^^^^^^^^^^^^^

The right preset depends on your dataset and your goal:

- **Small datasets (2-10 geometries) focused on interpolation**: use a lower build preset
  (``short``). Longer training on few geometries tends to overfit, which degrades
  interpolation quality.
- **Moderate datasets with simple geometries**: use ``short`` or ``default``. Simple geometries
  (low polygon count) are easier to learn, and longer training may not bring additional benefit.
- **Large datasets or complex geometries**: use ``default`` or ``long``. Complex geometries
  (high polygon count) require more training iterations so the model truly learns the
  geometric structure rather than approximating it.

.. note::
   Some datasets are inherently easy to reconstruct. For those, even a ``short`` preset can achieve
   good reconstruction. However, for datasets of similar size but higher geometric complexity, you
   may need a longer preset so the model fully captures the geometry.

.. tip::
   If you observe that generated geometries are too smooth or lack detail, try a longer preset.
   If you observe void volumes or garbled shapes during interpolation, try reducing the preset.


Number of epochs
----------------

You can also configure the number of training iterations directly through the ``nb_epochs`` parameter.
``nb_epochs`` corresponds to the number of times each training geometry is seen by the model, between 1 and 1000.

``nb_epochs`` should only be used by experienced users.
While it enables finer customization, it requires prior knowledge of the model's behavior on your data.
A good approach is to start with ``build_preset`` and switch to ``nb_epochs`` only when further tuning is needed.

- **Poor reconstruction quality**: try increasing the number of epochs to give the model more time to learn.


Number of latent parameters
----------------------------

The number of latent parameters (``nb_latent_param``) defines the dimension of the latent space.
It determines the length of the code that represents each geometry.

Unless your use case has specific constraints, **it is strongly recommended to rely on the default value (512)**.

Increasing the number of latent parameters allows the model to encode more complex variations and
fine geometric details, but raises the risk of overfitting. If the number is too small, the model may
underfit and fail to capture the necessary complexity.


Know your use case
-------------------

Before configuring your model, consider what you are trying to achieve:

- **Design exploration**: you want to generate many diverse geometries. Focus on providing diverse
  training data and use a moderate build preset to prioritize interpolation quality.
- **Optimization**: you want to use GeomAI within an optimization loop (for example with optiSLang).
  Provide training data that covers the region of interest and prioritize smooth interpolations.
  See :ref:`evaluation_workflows_geomai` for guidance on workflow integration.
- **Capturing complex geometric features**: your geometries have fine details or intricate shapes
  that must be faithfully reproduced. Provide enough training data to represent those features
  and use a longer build preset to focus on reconstruction quality.

.. tip::
   The model captures implicit constraints from your data. If all your training geometries share a
   common feature (such as a symmetry plane), the model will enforce that constraint across all
   generated designs. Use this to your advantage by curating your training data intentionally.


Configuration example
---------------------

For a complete example showing how to configure and build a model, see :ref:`ref_build_model`.
