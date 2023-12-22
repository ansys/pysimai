.. _geometries:

Geometries
==========

.. py:module:: ansys.simai.core.data.geometries

Geometries are the core of *SimAI Deep Learning powered predictions*.
A geometry is a 3D model and associated metadata managed by the SimAI platform.

.. _geometry_format:

File format
-----------

The input format for your workspace is described by the model manifest.
You can access that information for a specific workspace through :attr:`workspace.model.geometry<ansys.simai.core.data.workspaces.ModelManifest.geometry>`

If you have a problem converting to the expected format, please contact us for more information at support-simai@ansys.com

Directory
---------

.. autoclass:: GeometryDirectory()
    :members:

Model
-----

.. autoclass:: Geometry()
    :members:
    :inherited-members:


Filtering
---------

.. autoclass:: Range()
