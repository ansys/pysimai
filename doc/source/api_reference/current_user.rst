.. _current_user:

Current user
============

.. py:module:: ansys.simai.core.data.current_user

The current user module provides self-management operations for the authenticated user,
including offline token generation and consent management.

You access the current user through the :attr:`SimAIClient.me<ansys.simai.core.client.SimAIClient.me>`
property.

Example
-------

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.from_config()

    # Generate an offline token
    token = simai_client.me.generate_offline_token()

    # List all consents
    consents = simai_client.me.consents.list()

    # Revoke a specific consent
    simai_client.me.consents.revoke("sdk")

CurrentUser
-----------

.. autoclass:: CurrentUser()
    :members:

ConsentDirectory
----------------

.. autoclass:: ConsentDirectory()
    :members:

Consent
-------

.. autoclass:: Consent()
    :members:
