.. _workspaces:

Workspaces
==========

.. py:module:: ansys.simai.core.data.workspaces

Workspaces are a set of specific geometries, predictions and post-processings.
Each workspace uses a specific kernel.

To set which workspace the client is configured for, please refer to
:meth:`SimAIClient.set_current_workspace() method<ansys.simai.core.client.SimAIClient.set_current_workspace>`

Directory
---------

.. autoclass:: WorkspaceDirectory()
    :members:

Model
-----

.. autoclass:: Workspace()
    :members:
    :inherited-members:

ModelManifest
-------------

.. autoclass:: ModelManifest()
    :members:
