.. _geomai_projections:

GeomAIProjections
=================

.. py:module:: ansys.simai.core.data.geomai.projections

The ``Projections`` module is in charge of projecting
:py:class:`geometries<ansys.simai.core.data.geomai.geometries.GeomAIGeometry>` onto
the model of your
:py:class:`workspaces<ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace>`,
which yields the latent code of the geometry, that is its coordinates in the latent
space of the model.

Directory
---------

.. autoclass:: GeomAIProjectionDirectory()
    :members:

Model
-----

.. autoclass:: GeomAIProjection()
    :members:
    :inherited-members:
