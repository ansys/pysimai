Generative design
==================================

Learn about the parameters to set to generate a new design based on a trained model.

Latent parameters
---------------------

The latent parameters (``latent_params``) correspond to a list of numbers (floats) that represent the position of the geometry in the latent space.
You define this parameter to generate a geometry with a trained model.

The number of floats can be less than or equal to the ``nb_latent_param`` your model was requested with.
For more information, see Number of latent parameters.

Working with reduced latent spaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GeomAI expresses its latent space in a basis where dimensions are ordered by importance: the first
dimensions capture the largest sources of variation in the training data, while later dimensions
capture increasingly finer details. This means that for many workflows (exploration, interpolation,
optimization), you can work with a small subset of the most informative dimensions rather than the
full latent vector.

Choosing the right number of dimensions
""""""""""""""""""""""""""""""""""""""""

The Model Evaluation Report (MER) has a **Parameter Importance** section that shows how much each
latent dimension contributes to the variability of the training data. Use this to decide how many
dimensions to keep: if the first 10 dimensions account for most of the variance, working with
``n=10`` gives you a compact space with minimal loss of geometric fidelity.

Retrieving reduced latent codes
""""""""""""""""""""""""""""""""

The ``workspace.get_latent_parameters()`` method accepts an optional ``n`` parameter that truncates
each latent vector to its first ``n`` elements. The value of ``n`` must not exceed the number of
latent parameters the model was trained with.

.. code-block:: python

   # Full latent codes
   full = workspace.get_latent_parameters()

   # Only the 10 most important dimensions
   reduced = workspace.get_latent_parameters(n=10)

When ``n`` is omitted, the full vectors are returned as before.

Generating geometries from reduced codes
"""""""""""""""""""""""""""""""""""""""""

Reduced latent vectors can be passed directly to ``GeomAIPredictionConfiguration``. The remaining
dimensions are automatically discarded, so no additional handling is required.

.. code-block:: python

   from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration

   vec = list(reduced.values())[0]  # 10-element vector

   config = GeomAIPredictionConfiguration(latent_params=vec)
   prediction = client.geomai.predictions.run(config, workspace)

This is particularly useful for integration with optimization tools, where working in a
lower-dimensional space reduces the search space and speeds up convergence.

.. note::

   Reducing the number of latent dimensions discards the information carried by the removed
   dimensions. Geometries reconstructed from reduced codes are close approximations of the
   originals, not exact replicas. The fewer dimensions retained, the coarser the approximation.


Resolution
-----------

The resolution parameter is a list of three integers defining the number of voxels along the X, Y, and Z axes.

Use higher resolution for complex or precise geometries, and lower resolution for simple shapes or quick previews.

The total number of voxels must not exceed 900^3, that is `x`, `y`, `z` multiplied together must be less than or equal to 900^3.
If you exceed that value, an error occurs.

Defaults to ``[100,100,100]``, if ``None`` is provided.

For the maximum resolution of 900^3, the prediction takes approximately 10 minutes (approximately 1 microsecond per voxel).
