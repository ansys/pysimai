:description: Interpolate between two geometries in the latent space of a GeomAI model, and project an existing geometry onto the latent space to get its latent parameters.

.. _geomai_models_interpolate_and_project:

Interpolate and project geometries with a GeomAI model
======================================================

**Applies to:** GeomAI models

To interpolate between two geometries, mix their :term:`latent vectors <latent vector>` from
:meth:`workspace.get_latent_parameters()<ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace.get_latent_parameters>`
and generate a geometry for each mix. To get the :term:`latent parameters <latent parameter>` of a
geometry that isn't in the training data, upload it and project it onto the GeomAI model with
:meth:`geomai_client.projections.run()<ansys.simai.core.data.geomai.projections.GeomAIProjectionDirectory.run>`.

Complete script for an interpolation
------------------------------------

This script generates 11 geometries on a straight path between two training geometries.

.. code-block:: python

   import os

   import ansys.simai.core as asc
   from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration
   from ansys.simai.core.errors import ProcessingError

   OUTPUT_DIR = "interpolations"
   NUM_STEPS = 10
   GEOM_A_NAME = "<your_first_geometry_name>"
   GEOM_B_NAME = "<your_second_geometry_name>"


   def interpolate_latents(vec1, vec2, alpha):
       """Linear interpolation between two latent vectors (alpha 0.0 = vec1, 1.0 = vec2)."""
       return [(1 - alpha) * x + alpha * y for x, y in zip(vec1, vec2)]


   simai_client = asc.SimAIClient(organization="<your_organization>")
   geomai_client = simai_client.geomai

   workspace = geomai_client.workspaces.get(name="<your_workspace_name>")
   latent_dict = workspace.get_latent_parameters()

   for name in (GEOM_A_NAME, GEOM_B_NAME):
       if name not in latent_dict:
           raise ValueError(f"Geometry '{name}' not found. Available: {list(latent_dict)}")

   vec_a = latent_dict[GEOM_A_NAME]
   vec_b = latent_dict[GEOM_B_NAME]

   # Interpolate between two geometries with a GeomAI model
   predictions = []
   for i in range(NUM_STEPS + 1):
       latent_params = interpolate_latents(vec_a, vec_b, i / NUM_STEPS)
       config = GeomAIPredictionConfiguration(latent_params=latent_params)
       predictions.append(geomai_client.predictions.run(config, workspace))

   os.makedirs(OUTPUT_DIR, exist_ok=True)
   for i, prediction in enumerate(predictions):
       try:
           if not prediction.wait(timeout=600):
               print(f"Prediction {i} timed out.")
               continue
       except ProcessingError:
           print(f"Prediction {i} failed: {prediction.failure_reason}")
           continue
       out_path = os.path.join(OUTPUT_DIR, f"prediction_{i:02d}_{prediction.id}.vtp")
       prediction.download(out_path)
       print(f"Saved prediction to {out_path}")

Interpolate between two geometries with a GeomAI model
------------------------------------------------------

A linear interpolation creates smooth transitions between two existing designs and blends their
features. It's also a good check of a GeomAI model: the intermediate shapes should change
gradually and have no abrupt jumps or garbled geometries.

#. Get the latent vectors of the training geometries with ``workspace.get_latent_parameters()``.
   The method returns a dictionary that maps each geometry name to its latent vector.
#. Mix the two latent vectors with a factor ``alpha`` from 0.0 (first geometry) to 1.0 (second
   geometry): ``(1 - alpha) * x + alpha * y`` for each latent parameter.
#. Run one prediction for each value of ``alpha`` with
   :meth:`geomai_client.predictions.run()<ansys.simai.core.data.geomai.predictions.GeomAIPredictionDirectory.run>`.

To interpolate in a reduced :term:`latent space`, pass ``n`` to ``get_latent_parameters()``. For more
information, see :ref:`reduced_latent_space_geomai`.

If the interpolation path doesn't look as expected, the training data probably has too few
geometries between the two endpoints. For how to fix it, see
:doc:`/user-guide/geomai-models/evaluate-a-model`.

Complete script for a projection
--------------------------------

This script uploads a geometry, projects it onto the GeomAI model of a workspace, and generates the
geometry again from its latent parameters.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.geomai.predictions import GeomAIPredictionConfiguration
   from ansys.simai.core.errors import ProcessingError

   simai_client = asc.SimAIClient(organization="<your_organization>")
   geomai_client = simai_client.geomai

   workspace = geomai_client.workspaces.get(name="<your_workspace_name>")

   try:
       geometry = geomai_client.geometries.upload("<path_to_your_geometry>.vtp")
       geometry.wait()

       # Project a geometry onto the latent space of a GeomAI model
       projection = geomai_client.projections.run(geometry, workspace)
       projection.wait()
       latent_parameters = projection.get_latent_parameters()
       print(f"Retrieved {len(latent_parameters)} latent parameters")

       # Use projected latent parameters in a workflow
       config = GeomAIPredictionConfiguration(latent_params=latent_parameters)
       prediction = geomai_client.predictions.run(config, workspace)
       prediction.wait()
       prediction.download(f"reconstructed_{prediction.id}.vtp")
       print(f"Saved reconstructed geometry to reconstructed_{prediction.id}.vtp")
   except ProcessingError as error:
       print(f"Processing failed: {error}")

Project a geometry onto the latent space of a GeomAI model
----------------------------------------------------------

A projection finds the latent parameters that represent an existing geometry in the latent space
of a trained GeomAI model. The geometry doesn't need to be part of the training data.

#. Upload the geometry with
   :meth:`geomai_client.geometries.upload()<ansys.simai.core.data.geomai.geometries.GeomAIGeometryDirectory.upload>`
   and wait for its processing. To reuse a geometry that you already uploaded, use
   ``geomai_client.geometries.get(name="<your_geometry_name>")``.
#. Run the projection with ``geomai_client.projections.run(geometry, workspace)``, or with
   :meth:`geometry.run_projection(workspace)<ansys.simai.core.data.geomai.geometries.GeomAIGeometry.run_projection>`.
   If you don't pass ``workspace``, the projection uses the current workspace of the client.
#. Wait for the projection, then call
   :meth:`projection.get_latent_parameters()<ansys.simai.core.data.geomai.projections.GeomAIProjection.get_latent_parameters>`.
   The method returns ``None`` until the projection has finished successfully.

.. code-block:: python

   projection = geomai_client.projections.run(geometry, workspace)
   projection.wait()
   latent_parameters = projection.get_latent_parameters()

A geometry uploaded for projection must meet the same requirements as training data: a ``.vtp`` or
``.stl`` file with a watertight, manifold surface and no self-intersections. For more information,
see :ref:`geometry_requirements`. If the geometry is invalid, its processing fails and Ansys SimAI
marks it as invalid.

Get a reduced latent vector from a projection
---------------------------------------------

Pass ``n`` to ``projection.get_latent_parameters()`` to get only the first ``n`` latent parameters.
Latent parameters are ordered by importance, so the most influential dimensions come first.
Without ``n``, the method returns all latent parameters. ``n`` must not exceed the number of latent
parameters of the GeomAI model.

.. code-block:: python

   latent_parameters = projection.get_latent_parameters(n=10)

For more information, see :ref:`reduced_latent_space_geomai`.

Reuse an existing projection
----------------------------

A projection is cached for each geometry and GeomAI model. If the geometry is already projected
onto the GeomAI model of the workspace, ``projections.run()`` returns the existing projection
without computing it again.

To look up a projection without starting a computation, call
:meth:`geometry.get_projection(workspace)<ansys.simai.core.data.geomai.geometries.GeomAIGeometry.get_projection>`.
It returns ``None`` if the geometry isn't projected onto the GeomAI model of this workspace yet:

.. code-block:: python

   existing_projection = geometry.get_projection(workspace)
   if existing_projection is None:
       print("Geometry has not yet been projected onto this workspace's model.")

To list all projections of a workspace, use
:meth:`workspace.list_projections()<ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace.list_projections>`
or ``geomai_client.projections.list(workspace=workspace)``.

Use projected latent parameters in a workflow
---------------------------------------------

The latent parameters of a projected geometry are useful in optimization, design exploration,
sensitivity analysis, and parameter studies:

- Start an optimization from an existing design: use the latent parameters of the projected design
  as the starting point instead of a randomly generated geometry. This gives a meaningful baseline
  and can help the optimization converge faster.
- Parametrize a non-parametric geometry: represent the geometry as a compact set of latent
  parameters that other models can take as inputs, for example to predict performance or classify
  shapes.

For more information on optimization workflows, see :doc:`/user-guide/geomai-models/generate-geometries`.

Expected result when you interpolate and project geometries with a GeomAI model
-------------------------------------------------------------------------------

The interpolation script creates the ``interpolations`` folder and prints one
``Saved prediction to ...`` line for each of the 11 geometries. The projection script prints the
number of latent parameters, for example ``Retrieved 512 latent parameters``, and the path of the
reconstructed geometry.

Errors when you interpolate and project geometries with a GeomAI model
----------------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The processing of the geometry, the projection, or the prediction failed, for example
       because the geometry is invalid.
     - Read ``failure_reason`` on the failed object. Check the geometry against
       :ref:`geometry_requirements`.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The file extension isn't ``.vtp`` or ``.stl``, or ``n`` is larger than the number of latent
       parameters of the GeomAI model.
     - Use a supported file, or a lower value of ``n``.
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No workspace or geometry has the requested name.
     - Check the name with ``geomai_client.workspaces.list()`` or ``geomai_client.geometries.list()``.

More about how to interpolate and project geometries with a GeomAI model
------------------------------------------------------------------------

- :class:`~ansys.simai.core.data.geomai.projections.GeomAIProjectionDirectory`
- :class:`~ansys.simai.core.data.geomai.projections.GeomAIProjection`
- :class:`~ansys.simai.core.data.geomai.geometries.GeomAIGeometryDirectory`
- :doc:`/api_reference/geomai/projections`
- :doc:`/user-guide/geomai-models/generate-geometries`
- :ref:`ref_interpolate_geometries`
- :ref:`ref_project_geometries`
