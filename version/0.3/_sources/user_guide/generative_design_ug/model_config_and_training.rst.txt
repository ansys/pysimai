Model configuration and training
==================================

Learn about the parameters to set when configuring and training your AI model.

Build presets
-------------

Use the ``build_preset`` parameter to configure the training duration for building your model.

Durations available are:

- ``debug``: 4 minutes + 15 sec per geometry.
- ``short``: 45 minutes + 15 sec per geometry.
- ``default``: 3 hours + 15 sec per geometry.
- ``long``: 15 hours + 15 sec per geometry.

To select the right build preset, consider the size of the training dataset and the complexity of the geometries.
In this context, the number of polygons in a mesh is a rough estimate of the complexity of the geometry it represents:
simple geometries can be modeled with few polygons, while complex ones need more polygons.

For small datasets with simple geometries (low polygon count), use ``short`` preset.

For large datasets or geometries with high polygon count, use longer presets (``default`` or ``long``).

Number of epochs
^^^^^^^^^^^^^^^^

You can also configure the number of training iterations for building your model through the ``nb_epochs`` parameter.
``nb_epochs`` corresponds to the number of times each training data is seen by the model during the training, between 1 and 1000.

``nb_epochs`` should only be used by expert users.
While it enables finer customization, it requires prior knowledge on the model's performance.
A good approach is to start with ``build_preset`` and switch to ``nb_epochs`` when further customization is needed.


Number of latent parameters
--------------------------------

The number of latent parameters (``nb_latent_param``) defines the dimension of the latent space.
It also determines the length of the code, where the code is a set of parameters that represents the geometry within the latent space.

Unless your use case has specific constraints with respect to the latent dimension, **it is strongly recommended to rely on the default value (512)**.

Increasing the number of latent parameters allows the model to encode more complex variations and fine geometric details,
improving its ability to fit the training data. However, this also raises the risk of overfitting,
where the model memorizes the training geometries instead of learning general patterns.
Overfitting can lead to poor performance on new, unseen geometries.

If the number of latent parameters is too small, the model may underfit, failing to capture the necessary complexity of the data.
