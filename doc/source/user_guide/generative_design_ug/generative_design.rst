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

The resolution is a list of three integers defining the number of voxels along the X, Y, and Z axes. The default value is [100,100,100].

| The number of voxels must not exceed 900^3, i.e. the three numbers multiplied together must be less than or equal to 900^3. For example, possible values are [900,900,900], [9000,90,900], and so on.
| If you exceed that value an error will occur.

| In most cases, the default resolution can be used.
| However, you may need to use different values, staying below the value of 900^3.

Use higher resolution for complex or precise geometries, and lower resolution for simple shapes or quick previews.
