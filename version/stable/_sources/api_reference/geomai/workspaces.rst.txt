.. _geomai_workspaces:

GeomAIWorkspaces
================

.. py:module:: ansys.simai.core.data.geomai.workspaces

Workspaces are a set of specific predictions.
Each workspace uses a specific model.

You use the :meth:`GeomAIClient.set_current_workspace()<ansys.simai.core.data.geomai.client.GeomAIClient.set_current_workspace>`
method to set the workspace that the client is configured for.

Directory
---------

.. autoclass:: GeomAIWorkspaceDirectory()
    :members:

Model
-----

.. autoclass:: GeomAIWorkspace()
    :members:
    :inherited-members:
