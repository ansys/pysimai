Model configuration and training
==================================

Learn about the parameters to set when configuring and training your AI model.

Number of latent parameters
--------------------------------

The number of latent parameters (``nb_latent_param``) defines the dimensions of the latent space.
It also defines the length of the code, where the code is a set of latent parameters that represent a geometry in the latent space.

It must be defined according to the complexity and the diversity of the geometries you use as training data.

Increasing the number of latent parameters allows the model to encode more complex variations and fine geometric details,
improving its ability to fit the training data. However, this also raises the risk of overfitting,
where the model memorizes the training geometries instead of learning general patterns.
Overfitting can lead to poor performance on new, unseen geometries.

If the number of latent parameters is too small, the model may underfit, failing to capture the necessary complexity of the data.
Predictions on new geometries then lack detail and appear too generic.

The goal is to find an optimal balance: enough latent parameters to capture the essential complexity of the training geometries,
but not so many that the model overfits.

In most cases, if the training data are small or simple, use fewer latent parameters.
If the training data are large and highly variable, a larger number can be used,
but it is important to monitor generalization carefully.


Build preset and number of epochs
---------------------------------

Use either of these two parameters to set the training duration or the number of training iterations for building your model:

* | The ``build_preset`` parameter is used for configuring the model training duration between:
  |
  | - ``debug``: 4 minutes + 15 sec per geometry
  | - ``short``: 45 minutes + 15 sec per geometry
  | - ``default``: 3 hours + 15 sec per geometry
  | - ``long``: 15 hours + 15 sec per geometry

* | The ``nb_epochs`` parameter is the number of times each training data is seen by the model during the training, between 1 and 1000.
  |
  | ``nb_epochs`` should only be used by advanced users. While it enables finer customization, it requires prior knowledge on the model's performance. A good approach is to start with ``build_preset`` and switch to ``nb_epochs`` when further customization is needed. In most cases, if ``nb_latent_param`` is well chosen, 100 epochs give satisfying results.

To select the right build preset or number of epochs, consider the size of the training dataset and the complexity of the geometries.
In this context, the number of polygons in a mesh is a rough estimate of the complexity of the geometry it represents:
simple geometries can be modeled with few polygons, while complex ones need more polygons.

For small datasets with simple geometries (low polygon count), use fewer epochs or ``short`` preset.

For large datasets or geometries with high polygon count, use more epochs or longer presets (``default`` or ``long``).
