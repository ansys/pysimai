.. _current_user:

Current user
============

.. py:module:: ansys.simai.core.data.current_user

The current user module provides self-management operations for the authenticated user,
including offline token management.

You access the current user through the :attr:`SimAIClient.me<ansys.simai.core.client.SimAIClient.me>`
property.

Example
-------

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.from_config()

    # List all offline tokens
    tokens = simai_client.me.offline_tokens.list()

    # Generate a new offline token
    token = simai_client.me.offline_tokens.generate()

    # Revoke a specific token
    simai_client.me.offline_tokens.revoke("sdk")

CurrentUser
-----------

.. autoclass:: CurrentUser()
    :members:

OfflineTokenDirectory
---------------------

.. autoclass:: OfflineTokenDirectory()
    :members:

OfflineToken
------------

.. autoclass:: OfflineToken()
    :members:
