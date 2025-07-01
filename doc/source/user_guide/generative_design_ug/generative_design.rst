Generative design
==================================

Learn about the parameters to set to generate a new design based on a trained model.

Latent parameters
---------------------

The latent parameters (``latent_params``) correspond to a list of numbers (floats) that represent the position of the geometry in the latent space.
You define this parameter to generate a geometry with a trained model.

The number of floats must match the ``nb_latent_param`` your model was requested with.
For more information, see Number of latent parameters.


Resolution
-----------

The resolution is a list of three integers defining the number of divisions along the X, Y, and Z axes.

The default value [100, 100, 100] offers a good balance for general use.

Use the default resolution to test your setup.
Since it is an expert parameter, use a different value (than the default one) only if it is needed.
Use higher resolution for complex or precise geometries, and lower resolution for simple shapes or quick previews.
