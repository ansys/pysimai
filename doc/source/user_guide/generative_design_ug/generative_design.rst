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

The resolution parameter corresponds to a list of three integers defining the number of voxels along the X, Y, and Z axes.

By default, this parameter is set automatically based on training data.

How does this auto-resolution system work?

During training, each dataset is assigned a resolution derived from its mesh characteristics, particularly average edge lengths,
so that reconstructed outputs preserve similar geometric fidelity.

At inference, the system finds the nearest training example in the latent space, and reuses its associated resolution.

As a result, the resolution is not fixed per model but varies per inference, it provides you with
a data-driven default to ease user experience. You can still adjust it manually by using
higher resolution for complex or precise geometries, and lower resolution for simple shapes or quick previews.

The total number of voxels must not exceed 900^3, that is x, y, z multiplied together must be less than or equal to 900^3.
If you exceed that value, an error occurs.

For the maximum resolution of 900^3, the prediction takes approximately 10 minutes (approximately 1 microsecond per voxel).
