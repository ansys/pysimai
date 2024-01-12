.. _workspaces:

Workspaces
==========

.. py:module:: ansys.simai.core.data.workspaces

Workspaces are a set of specific geometries, predictions, and postprocessings.
Each workspace uses a specific kernel.

You use the :meth:`SimAIClient.set_current_workspace()<ansys.simai.core.client.SimAIClient.set_current_workspace>`
method to set the workspace that the client is configured for.

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
