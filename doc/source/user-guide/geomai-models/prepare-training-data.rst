:description: Check that your geometries meet the requirements for GeomAI model training data and decide how many geometries you need.

.. _data_preparation_geomai:

Prepare training data for a GeomAI model
========================================

**Applies to:** GeomAI models

Before you upload geometries as training data for a GeomAI model, check that each file meets the
geometry requirements and that the set of geometries covers the design space you want to explore.

Training data as the design language of a GeomAI model
------------------------------------------------------

The training data you provide defines the design space where the GeomAI model operates. The
GeomAI model learns a compressed representation of your geometries and generates new ones that
share the same design language. As a result:

- If you only provide square-looking shapes, the GeomAI model doesn't generate circles.
- If you only provide two geometries, the GeomAI model can only interpolate between them, without
  learning specific geometric features.
- The more diverse and representative your training data, the richer the :term:`latent space` and the
  more meaningful the generated geometries.

The results of a GeomAI model always fall within the design language that its training data
teaches it.

.. tip::
   A GeomAI model also captures implicit constraints from your training data. For example, if all
   your geometries share a common plane or feature, the GeomAI model learns that feature and
   reproduces it in every generated geometry.

.. _geometry_requirements:

Geometry requirements for GeomAI model training data
----------------------------------------------------

Each geometry used as training data must meet these requirements:

- File format: ``.vtp`` or ``.stl``.
- Watertight: the geometry forms a closed surface with no holes or gaps, that is, no open or
  boundary edges.
- Manifold: every edge is connected to exactly two faces, and each vertex has a well-defined,
  continuous neighborhood without branching or overlaps.
- No self-penetration: no part of the surface passes through another part of the same object.

If a geometry doesn't meet these requirements, its processing fails after upload and Ansys SimAI
marks it as invalid.

Check a geometry with PyVista
-----------------------------

Use `PyVista <https://docs.pyvista.org/>`_ to check whether a geometry is watertight and manifold,
then plot it to inspect problem areas:

.. code-block:: python

   import pyvista as pv

   mesh = pv.read("<path_to_your_geometry>.vtp")

   # A watertight manifold mesh has no open edges and every edge is shared by exactly two faces.
   if mesh.is_manifold and mesh.n_open_edges == 0:
       print("Geometry is manifold and watertight.")
   else:
       print("Geometry has issues. Fix holes, open edges, or non-manifold edges before upload.")

   # Display the mesh with its edges to find the issues.
   mesh.plot(show_edges=True)

This script uses `PyVista <https://docs.pyvista.org/>`_ to check every ``.vtp`` and ``.stl`` file
of a folder before upload. It doesn't connect to Ansys SimAI.

.. code-block:: python

   import os

   import pyvista as pv

   DATASET_PATH = "<path_to_your_geometry_folder>"

   for fname in sorted(os.listdir(DATASET_PATH)):
       if not fname.lower().endswith((".vtp", ".stl")):
           continue
       mesh = pv.read(os.path.join(DATASET_PATH, fname))
       # A watertight manifold mesh has no open edges and every edge is shared by exactly two faces.
       if mesh.is_manifold and mesh.n_open_edges == 0:
           print(f"{fname}: manifold and watertight")
       else:
           print(f"{fname}: fix holes, open edges, or non-manifold edges before upload")

Fix common geometry issues
--------------------------

If a geometry isn't watertight or manifold, try these fixes:

- Open the geometry in a CAD tool such as Ansys SpaceClaim to find and fill holes, remove
  duplicate faces, or fix non-manifold edges.
- Fill small holes with the utilities of a mesh processing library such as PyVista or ``trimesh``.
- Export the geometry again from your CAD software as a clean, closed surface mesh.

.. warning::
   An "invalid geometry" failure during processing means that the geometry isn't compatible with
   GeomAI models. Check that the geometry file is watertight and manifold.

Choose how many geometries to use as training data
--------------------------------------------------

The number of training geometries determines what the GeomAI model can learn:

- Very few geometries (2 to 4): the GeomAI model can only interpolate between these shapes and
  doesn't learn general geometric features. A lower build preset (``short``) often gives better
  interpolations.
- Moderate set (10 to 30): the GeomAI model starts to capture patterns and variations. This is a
  good starting point for most projects. A moderate build preset (``default``) is often
  recommended.
- Large set (50 or more): the GeomAI model can capture complex variations and fine details, which
  gives a richer design space. A higher build preset (``long``) can help capture the full
  complexity of the training data.

For more information on build presets, see :doc:`/user-guide/geomai-models/configure-a-model`.

More about how to prepare training data for a GeomAI model
----------------------------------------------------------

- :doc:`/user-guide/geomai-models/upload-training-data`
- :doc:`/user-guide/geomai-models/configure-a-model`
- :ref:`ref_create_project_upload_data`
