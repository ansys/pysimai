:description: Download the Model Evaluation Report of a GeomAI model, read its chamfer distance metrics, and fix common quality problems of a GeomAI model.

.. _evaluation_workflows_geomai:

Evaluate a GeomAI model
=======================

**Applies to:** GeomAI models

To evaluate a trained GeomAI model, download its Model Evaluation Report (MER) with
:meth:`GeomAIWorkspace.download_model_evaluation_report()<ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace.download_model_evaluation_report>`,
check the reconstruction metrics, and inspect geometries that the GeomAI model generates.

The MER of a GeomAI model differs from the MER of a SimAI model. For the MER of a SimAI model, see
:doc:`/user-guide/simai-models/evaluate-a-model`.

Download the Model Evaluation Report of a GeomAI model
------------------------------------------------------

After the build, Ansys SimAI produces a Model Evaluation Report (MER) for the GeomAI model. Get the
workspace of the GeomAI model and call ``download_model_evaluation_report()``. The method writes a
ZIP file to the path that you pass. Without a path, it returns a binary file object.

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.SimAIClient(organization="<your_organization>")
   geomai_client = simai_client.geomai

   workspace = geomai_client.workspaces.get(name="<your_workspace_name>")

   # Download the Model Evaluation Report as a ZIP file.
   workspace.download_model_evaluation_report("model_evaluation_report.zip")

The MER of a GeomAI model contains:

- Reconstruction metrics: the chamfer distance for each reconstructed training geometry.
- Quality histograms: visual indicators of which geometries are well reconstructed.
- Interpolation examples: interpolations between pairs of training geometries, computed
  automatically.
- Parameter Importance: how much each latent dimension contributes to the variability of the
  training data. Use it to work with a reduced latent space. For more information, see
  :ref:`reduced_latent_space_geomai`.

Read the chamfer distance of a GeomAI model
-------------------------------------------

The chamfer distance measures how close a reconstructed geometry is to the original. A lower value
means a better reconstruction. The MER includes a threshold that shows whether the chamfer
distance of each geometry is in the acceptable range for the GeomAI model.

Inspect the histogram of chamfer distances across all training geometries:

- Most geometries should cluster in a narrow band. A tight distribution means that the GeomAI
  model treats the training data consistently.
- Investigate geometries far outside that distribution. These outliers may have mesh quality
  issues, such as holes or non-manifold edges, or be too different from the rest of the training
  data to be learned reliably.

.. tip::
   If a geometry is an outlier in every new build, consider removing it from the training data and
   check whether its shape belongs to the design space that you want to explore.

Check the training settings of a GeomAI model
---------------------------------------------

The ``model_manifest`` property of the workspace returns a
:class:`~ansys.simai.core.data.geomai.workspaces.GeomAIModelManifest` object with the settings of
the trained GeomAI model: ``build_preset``, ``nb_latent_parameters``, ``nb_epochs`` (epochs
completed), and ``requested_nb_epochs``. The system can reduce the number of epochs to keep
training within 72 hours, so compare ``nb_epochs`` with ``requested_nb_epochs`` when you set
``nb_epochs`` in the configuration.

.. code-block:: python

   # Compare the requested and effective training settings.
   manifest = workspace.model_manifest
   print(f"Build preset: {manifest.build_preset}")
   print(f"Epochs: {manifest.nb_epochs} completed, {manifest.requested_nb_epochs} requested")
   print(f"Latent parameters: {manifest.nb_latent_parameters}")

``model_manifest`` raises :class:`~ansys.simai.core.errors.NotFoundError` for GeomAI models built
before model manifests existed.

Inspect generated geometries of a GeomAI model
----------------------------------------------

The metrics of the MER don't show everything. Before you use a GeomAI model in a workflow, look at
the geometries it generates:

- Generate random geometries to get an overview of what the GeomAI model can produce. See
  :doc:`/user-guide/geomai-models/generate-geometries`.
- Interpolate between two training geometries to check that the transitions are smooth, without
  abrupt jumps or garbled intermediate shapes. See :doc:`/user-guide/geomai-models/interpolate-and-project`.

Fix poor reconstruction in a GeomAI model
-----------------------------------------

If training geometries aren't correctly reconstructed:

#. Open the MER and check which geometries the chamfer distance thresholds flag.
#. Inspect the histogram. If the poorly reconstructed geometries are outliers, investigate them
   one by one. If the whole distribution is shifted high, the GeomAI model needs more training.
#. Check that the flagged training geometries meet the mesh requirements: watertight, manifold,
   and no self-penetration. See :ref:`geometry_requirements`.
#. If mesh quality isn't the issue, increase the resolution when you generate geometries. See
   :ref:`ref_geomai_resolution_section`.
#. If neither mesh quality nor resolution is the issue, try a longer build preset so that the
   GeomAI model favors reconstruction.
#. If a geometry is valid but structurally very different from the rest of the training data,
   consider removing it. It may pull the GeomAI model in conflicting directions.

Fix void or garbled geometries from a GeomAI model
--------------------------------------------------

If generated geometries are void or garbled:

- Stay close to known latent parameters. Use the
  :meth:`sample()<ansys.simai.core.data.geomai.predictions.GeomAIPredictionDirectory.sample>`
  method or interpolate between training geometries instead of choosing arbitrary latent
  parameters.
- If you set latent parameters yourself, keep all values within the approximate range of the
  latent parameters of your training data, typically -3 to +3. Values far outside this range fall
  outside the region that the GeomAI model learned.
- If void geometries appear even with ``sample()``, the GeomAI model may have overfit. Try a
  shorter build preset or fewer epochs.

Fix a lack of sharpness or disconnected parts in generated geometries
---------------------------------------------------------------------

- Increase the ``resolution`` parameter. The automatic resolution may be too low for geometries
  with fine details or sharp edges. Try ``(300, 300, 300)`` or higher. See
  :ref:`ref_geomai_resolution_section`.
- Parts that disconnect unexpectedly also often come from a resolution that is too low, not from
  the quality of the GeomAI model.

Fix an interpolation that doesn't follow the expected path
----------------------------------------------------------

A GeomAI model interpolates meaningfully only within the region it learned. A poor path between
two geometries usually means that the training data has too few geometries in that area of the
design space. Add intermediate geometries between the two endpoints to the training data and build
the GeomAI model again. They give the GeomAI model anchor points for the interpolation path.

Fix a GeomAI model that doesn't improve after a new build
---------------------------------------------------------

- Check the diversity of your training data. Very similar geometries limit what the GeomAI model
  can learn, whatever the training duration. Add more varied shapes.
- Remove persistent outliers. If the MER flags the same geometries in every build and these
  geometries aren't critical to your use case, removing them often improves the GeomAI model.
- Compare GeomAI models built with the same build preset. A ``short`` build and a ``default`` build
  give different results.

Expected result when you evaluate a GeomAI model
------------------------------------------------

The code in "Download the Model Evaluation Report of a GeomAI model" writes
``model_evaluation_report.zip`` to the current folder. The code in "Check the training settings of
a GeomAI model" prints the build preset, the number of epochs completed and requested, and the
number of latent parameters, for example ``Latent parameters: 512``.

Errors when you evaluate a GeomAI model
---------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No workspace has the requested name, or the GeomAI model has no model manifest because it
       was built before model manifests existed.
     - Check the workspace name with ``geomai_client.workspaces.list()``.

More about how to evaluate a GeomAI model
-----------------------------------------

- :class:`~ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace`
- :class:`~ansys.simai.core.data.geomai.workspaces.GeomAIModelManifest`
- :doc:`/user-guide/geomai-models/configure-a-model`
- :doc:`/user-guide/geomai-models/generate-geometries`
- :doc:`/user-guide/geomai-models/interpolate-and-project`
