.. _evaluation_workflows_geomai:

Evaluation and workflow integration
====================================

Learn how to evaluate your trained model, interpret results, improve your design space,
and integrate GeomAI predictions into broader engineering workflows.


Evaluate your model with the Model Evaluation Report
-----------------------------------------------------

After training, GeomAI produces a Model Evaluation Report (MER) that helps you assess the quality
of your model. Download it with:

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.SimAIClient(organization="my_organization")
   geomai_client = simai_client.geomai

   workspace = geomai_client.workspaces.get(name="my-workspace")
   workspace.download_model_evaluation_report("model_report.zip")

The MER contains:

- **Reconstruction metrics**: chamfer distance values for each reconstructed training geometry.
- **Quality histograms**: visual indicators showing which geometries are well-reconstructed.
- **Interpolation examples**: interpolations between pairs of training geometries performed automatically.
- **Parameter Importance**: how much each latent dimension contributes to the variability of the
  training data. Useful when working with reduced latent spaces (see :ref:`reduced_latent_spaces_geomai`).


Understanding the chamfer distance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The chamfer distance measures how close a reconstructed geometry is to the original. A lower value
means better reconstruction.

The MER includes a threshold that indicate whether each geometry's chamfer distance falls
in the acceptable range for your model.

Inspect the **histogram** of chamfer distances across all training geometries:

- Most geometries should cluster in a narrow band. A tight distribution indicates the model treats
  the dataset consistently.
- Geometries that fall significantly outside that distribution (outliers) are worth investigating:
  they may have mesh quality issues (holes, non-manifold edges) or be genuinely too different from
  the rest of the dataset to be learned reliably.

.. tip::
   If a geometry consistently appears as an outlier across rebuilds, consider removing it from the
   dataset and assessing whether its shape is representative of the design space you want to explore.


Qualitative evaluation with sampling
--------------------------------------

Beyond the metrics in the MER, it is important to qualitatively check what your model produces.
You can visually inspect the generated geometries to confirm the model behaves as expected 
before integrating it into any workflow.

Generate random samples
^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``sample`` method to generate random geometries from the learned design space.
Under the hood, this method picks random latent parameters using a smart sampling strategy that
stays within the bounds of the training data. This makes it the simplest way to get an overview 
of what your model can produce.

For a complete example, see :ref:`ref_generate_random_geometries`.

.. warning::
   The ``sample`` method is in beta. It will likely be recast or retired by July 2026.
   Testing and feedback are encouraged, but it is advised not to include it in a production workflow.

Generate linear interpolations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To check how the model transitions between known geometries, perform linear interpolations
between two latent vectors. This lets you verify that the model produces smooth, meaningful
transitions rather than abrupt jumps or garbled intermediate shapes.

For a complete example showing how to interpolate between geometries step by step,
see :ref:`ref_interpolate_geometries`.

Generate custom geometries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For more control, you can specify latent parameters and resolution directly.
Each geometry in your training set has a corresponding latent code, and new geometries are generated
by specifying new positions in the latent space.

- The number of floats must match the ``nb_latent_param`` the model was configured with (default: 512).
- Latent parameters typically range between -3 and +3 for meaningful results. Values too far from
  known training codes may produce garbled or void geometries.
- You can retrieve the latent codes of all training geometries with ``workspace.get_latent_parameters()``.
  These serve as reference points for interpolation and exploration. Pass an optional ``n`` argument
  to truncate each vector to its first ``n`` (most important) dimensions — see
  :ref:`reduced_latent_spaces_geomai`.

The resolution parameter is a tuple of three integers ``(x, y, z)`` defining the number of voxels
along each axis:

- **Low resolution** (for example ``(50, 50, 50)``): fast generation, suitable for quick previews.
- **Medium resolution** (for example ``(100, 100, 100)``): good balance for most use cases.
- **High resolution** (for example ``(200, 200, 200)`` or above): captures fine details and sharp edges.

The total number of voxels must not exceed 900\ :sup:`3` (that is, ``x * y * z <= 729,000,000``).
For the maximum resolution, prediction takes approximately 10 minutes.

.. tip::
   If your generated geometries look correct in shape but lack sharpness or show an unexpected
   number of disconnected parts, increasing the resolution is often the solution.


.. _reduced_latent_spaces_geomai:

Working with reduced latent spaces
------------------------------------

GeomAI orders latent dimensions by importance: the first dimensions capture the largest sources of
variation in the training data, while later dimensions capture increasingly finer details.
For many workflows — exploration, interpolation, optimization — you can work with a small subset of
the most informative dimensions rather than the full latent vector.

Choosing the right number of dimensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The MER includes a **Parameter Importance** section showing how much each latent dimension
contributes to the variability of the training data. Use it to decide how many dimensions to keep:
if the first 10 dimensions account for most of the variance, working with ``n=10`` gives a compact
space with minimal loss of geometric fidelity.

Retrieving reduced latent codes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``workspace.get_latent_parameters()`` accepts an optional ``n`` parameter that truncates each
latent vector to its first ``n`` elements. ``n`` must not exceed the number of latent parameters
the model was trained with.

.. code-block:: python

   # Full latent codes
   full = workspace.get_latent_parameters()

   # Only the 10 most important dimensions
   reduced = workspace.get_latent_parameters(n=10)

When ``n`` is omitted, the full vectors are returned.

Generating geometries from reduced codes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Reduced latent vectors can be passed directly to :class:`GeomAIPredictionConfiguration
<ansys.simai.core.data.geomai.predictions.GeomAIPredictionConfiguration>`.
The remaining dimensions are automatically discarded — no additional handling is required.

.. code-block:: python

   from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration

   vec = list(reduced.values())[0]  # 10-element vector

   config = GeomAIPredictionConfiguration(latent_params=vec)
   prediction = geomai_client.predictions.run(config, workspace)

This is particularly useful when integrating with optimization tools: working in a lower-dimensional
space reduces the search space and speeds up convergence.

.. note::
   Reducing the number of latent dimensions discards the information carried by the removed
   dimensions. Geometries reconstructed from reduced codes are close approximations of the originals,
   not exact replicas. The fewer dimensions retained, the coarser the approximation.


Troubleshooting and improving your model
-----------------------------------------

Use this section when your model does not produce satisfactory results. For each symptom,
you will find both a diagnostic step and corrective actions.

Geometries are not correctly reconstructed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Open the MER and check which geometries are flagged by the chamfer distance thresholds.
2. Inspect the histogram: are poorly-reconstructed geometries outliers, or is the whole
   distribution shifted high? A shifted distribution suggests the model needs more training time.
3. Verify that the flagged training geometries meet the mesh requirements (watertight, manifold,
   no self-penetration). See :ref:`data_preparation_geomai`.
4. If mesh quality is not the issue, try a longer build preset.
5. If the geometry is valid but structurally very different from the rest of the dataset,
   consider whether it should be included — it may be pulling the model in conflicting directions.

Generated geometries are void or garbled
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Stay close to known latent codes. Use the ``sample`` method or construct interpolations between
  training geometries rather than specifying arbitrary latent parameters.
- If you are specifying latent parameters manually, check that all values stay within the
  approximate range of your training codes (typically -3 to +3). Values far outside this range
  land outside the region the model has learned.
- If void geometries appear even with the ``sample`` method, the model may have overfit. Try
  reducing the build preset or the number of epochs.

Lack of sharpness or explosion of parts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Increase the resolution parameter. The default ``(100, 100, 100)`` may be insufficient for
  geometries with fine details or sharp edges. Try ``(150, 150, 150)`` or higher.
- If parts are disconnecting unexpectedly, this is also often a resolution issue rather than a
  model quality problem.

Interpolation does not follow the expected path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- The model can only interpolate meaningfully within the region it has learned. If the path between
  two geometries is poor, it usually means there are not enough training geometries in that area of
  the design space.
- Add intermediate geometries as training data between the two endpoints and rebuild. This gives the
  model concrete anchor points to learn a meaningful interpolation path.

Model results do not improve after rebuilding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Check the diversity of your training data. A dataset of very similar geometries limits what the
  model can learn regardless of training time. Add more varied shapes to enrich the latent space.
- Remove persistent outliers: if the MER consistently flags the same geometries across builds,
  and those geometries are not critical to your use case, removing them often improves overall
  model quality.
- Verify you are comparing builds of the same preset. Comparing a ``short`` build against a
  previous ``default`` build will naturally show different results.


Workflow integration
---------------------

Using GeomAI with optimization tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GeomAI can be integrated into optimization workflows (for example with optiSLang) by using the
latent parameters as design variables. Working in a reduced latent space — keeping only the most
important dimensions — lowers the dimensionality of the optimization problem and speeds up
convergence. See :ref:`reduced_latent_spaces_geomai` for how to retrieve reduced latent codes and
use them as design variables.

The key trade-off is:

- Fewer dimensions make optimization easier and faster to converge, but capture less geometric detail.
- More dimensions allow finer control over the geometry, but increase the dimensionality of the
  optimization problem.

Use the **Parameter Importance** section of the MER to decide how many dimensions capture enough
geometric variation for your use case.
