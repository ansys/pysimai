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


Understanding the chamfer distance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The chamfer distance measures how close a reconstructed geometry is to the original. A lower value
means better reconstruction.

In the MER, you can find:

- Per-geometry chamfer distance values.
- A histogram that helps you identify outliers: geometries that are significantly harder to reconstruct.

Use this information to spot potential issues. If some geometries have a much higher chamfer distance
than others, inspect them for quality issues (holes, non-manifold edges) or consider that they may be
too different from the rest of your dataset.


Qualitative evaluation with sampling
--------------------------------------

Beyond the metrics in the MER, it is important to qualitatively check what your model produces.
This is the first thing to do after training: visually inspect the generated geometries to confirm
the model behaves as expected before integrating it into any workflow.

Generate random samples
^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``sample`` method to generate random geometries from the learned design space.
Under the hood, this method picks random latent parameters using a smart sampling strategy that
stays within the bounds of the training data, producing valid geometries without errors.
This makes it the simplest way to get an overview of what your model can produce.

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
  These serve as reference points for interpolation and exploration.

The resolution parameter is a tuple of three integers ``(x, y, z)`` defining the number of voxels
along each axis:

- **Low resolution** (for example ``(50, 50, 50)``): fast generation, suitable for quick previews.
- **Medium resolution** (for example ``(100, 100, 100)``): the default. Good balance for most use cases.
- **High resolution** (for example ``(200, 200, 200)`` or above): captures fine details and sharp edges.

The total number of voxels must not exceed 900\ :sup:`3` (that is, ``x * y * z <= 729,000,000``).
For the maximum resolution, prediction takes approximately 10 minutes.

.. tip::
   If your generated geometries look correct in shape but lack sharpness or show an unexpected
   number of disconnected parts, increasing the resolution is often the solution.


Troubleshooting common issues
-------------------------------

Geometries are not correctly reconstructed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Check the MER for reconstruction metrics and identify outlier geometries.
2. Verify that the problematic training geometries meet the requirements (watertight, manifold).
3. Consider using a longer build preset to give the model more training time.

Generated geometries are void or garbled
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Explore around known points instead of sampling far from the
  training data. Use the ``sample`` method or interpolations close to known latent codes.

Lack of sharpness or explosion of parts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Try increasing the resolution parameter. The default resolution may be
insufficient for geometries with fine details.

Interpolation does not follow the expected path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the generated geometries along an interpolation are geometrically correct but do not match
the transition you expect, consider adding intermediate training geometries in the "gaps"
of your design space. This gives the model more anchor points to learn a meaningful interpolation path.


Improve your design space
---------------------------

If your model does not produce satisfactory results, consider the following strategies:

- **Add more diverse training data**: a richer dataset helps the model learn a more expressive
  latent space.
- **Add geometries in gaps**: if interpolation between two geometries is poor, add intermediate
  geometries as training data to guide the model.
- **Remove outliers**: if the MER shows that certain geometries are poorly reconstructed and they
  are not critical to your use case, consider removing them and rebuilding.
- **Adjust the build preset**: see :ref:`model_setup_geomai` for guidance on choosing the right
  preset for your scenario.


Workflow integration
---------------------

Using GeomAI with optimization tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GeomAI can be integrated into optimization workflows (for example with optiSLang) by using the
latent parameters as design variables.

The key question is: **how many reduced parameters should you use?**

- Fewer reduced parameters make optimization easier and faster to converge, but capture less
  geometric detail.
- More reduced parameters allow finer control over the geometry, but increase the dimensionality
  of the optimization problem.

You need to find an equilibrium that balances optimization efficiency with geometric expressiveness.
Use the explained variance from dimension reduction (available in the MER) to decide how many
parameters capture enough of the geometric variation for your use case.


Using GeomAI for geometry description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GeomAI can also be used as a tool to describe geometries through their latent representations.
Potential applications include:

- **Design space visualization**: project geometries into a lower-dimensional space to understand
  how designs relate to each other.
- **Non-parametric outlier detection**: identify geometries that fall far from the rest in
  latent space.
- **Feature extraction**: use latent parameters as input features for downstream models.

.. warning::
   If your goal is to predict physical responses (forces, flow fields, etc.) from geometries,
   SimAI is the appropriate tool. GeomAI is designed to generate geometries without using response
   data during training. Chaining GeomAI with a separate prediction model is not recommended
   compared to using SimAI directly, which trains on both geometry and response data simultaneously.
