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

The resolution parameter is a list of three integers defining the number of voxels along the X, Y, and Z axes.

Use higher resolution for complex or precise geometries, and lower resolution for simple shapes or quick previews.

The total number of voxels must not exceed 900^3, i.e. the three numbers multiplied together must be less than or equal to 900^3.
If you exceed that value an error will occur.

Defaults to ``[100,100,100]``, if ``None`` is provided.
