.. _geometries:

Geometries
==========

.. py:module:: ansys.simai.core.data.geometries

Geometries are the core of *SimAI deep learning-powered predictions*.
A geometry is a 3D model and the associated metadata managed by the SimAI platform.

.. _geometry_format:

File format
-----------

The input format for your workspace is described by the model manifest.
You use the :attr:`workspace.model.geometry<ansys.simai.core.data.workspaces.ModelManifest.geometry>`
attribute to access the information for a specific workspace.

If you have a problem converting to the expected format, contact the SimAI team
at `support-simai@ansys.com <mailto:support-simai@ansys.com>`_.

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
