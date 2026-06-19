.. _data_preparation_geomai:

Data preparation
================

Learn how to prepare and validate your geometries before uploading them as training data for GeomAI.


Training data as design language
----------------------------------

The training data you provide defines the design space where GeomAI operates. The model learns a compressed
representation of your geometries and generates new ones that share the same design language.

This means that:

- If you only provide square-looking shapes, the model will not generate circles.
- If you only provide two geometries, GeomAI can only interpolate between them without truly understanding
  specific geometric features.
- The more diverse and representative your dataset is, the richer the latent space becomes, and the more
  meaningful the generated geometries will be.

Think of your training data as the vocabulary the model will use. The results it produces will always
fall within the design language you have taught it.

.. tip::
   The model also captures implicit constraints from your data. For example, if all your training geometries
   share a common plane or feature, the model will reproduce that feature across all generated designs.


Geometry requirements
---------------------

The geometries used as training data must comply with the following requirements to be correctly processed:

- **File formats**: ``.vtp`` or ``.stl``.
- **Watertight**: the geometry must form a completely closed surface with no holes or gaps.
  Each edge must be shared by exactly two faces.
- **Manifold**: every edge must be connected to exactly two faces, and each vertex must have
  a well-defined, continuous neighborhood without branching or overlaps.
- **No self-penetration**: no part of the surface should pass through another part of the same object.

If your geometry does not meet these requirements, the processing step will fail and the geometry
will be marked as invalid.


How to check and fix your geometries
-------------------------------------

Before uploading, validate your geometries to avoid processing failures.

Check watertightness with PyVista
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use `PyVista <https://docs.pyvista.org/>`_ to check if your geometry is watertight:

.. code-block:: python

   import pyvista as pv

   mesh = pv.read("my_geometry.vtp")

   # Check if the mesh is watertight
   if mesh.is_manifold:
       print("Geometry is manifold (watertight).")
   else:
       print("Geometry is NOT manifold. Please fix holes or gaps before uploading.")

   # Visualize the mesh to inspect for issues
   mesh.plot(show_edges=True)

Fix common issues
^^^^^^^^^^^^^^^^^

If your geometry is not watertight or manifold, you can:

- **Use a CAD tool**: open your geometry in a tool like SpaceClaim or Meshmixer to identify and
  fill holes, remove duplicate faces, or fix non-manifold edges.
- **Fill holes programmatically**: some mesh processing libraries (such as PyVista or trimesh)
  provide utilities to fill small holes automatically.
- **Re-export**: ensure your CAD software exports a clean, closed surface mesh.

.. warning::
   An "invalid geometry" error during processing means the geometry is not compatible with
   Generative Design. Check the geometry file for watertightness and manifold issues.


How much training data do you need?
------------------------------------

The number of training geometries directly impacts what the model can learn:

- **Very few geometries (2-4)**: the model can only interpolate between these shapes. It will not learn
  general geometric features. In this case, using a lower build preset (``short``) often
  produces better interpolations.
- **Moderate dataset (10-30)**: the model begins to capture patterns and variations. This is a good
  starting point for most projects.
- **Large dataset (50+)**: the model can capture complex variations and fine details, producing a
  richer and more expressive design space.

.. tip::
   Start with a small number of geometries and the ``debug`` build preset to quickly verify
   that the model can learn from your data and that the generated designs are meaningful.
   This helps detect data issues early and saves time.
