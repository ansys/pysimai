.. _configuration:
.. py:module:: ansys.simai.core.utils.configuration

Client configuration
====================

Where to start
--------------

You start by creating a :class:`~ansys.simai.core.client.SimAIClient`
instance:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="my-company")


As demonstrated in the preceding code, you configure the instance by
passing the required parameters on client creation. You are prompted
for any missing parameters.

Once you understand how creating an instance works, you can look into using a
:ref:`configuration file<config_file>` for creating a client instance.

Configuration options
---------------------

Descriptions follow of all configuration options for the :class:`~ansys.simai.core.client.SimAIClient`
class:

.. autopydantic_model:: ClientConfig
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-json: False
  :model-show-field-summary: False
  :model-show-validator-members: False
  :field-list-validators: False


.. _anchor-credentials:

Credentials
-----------

To use the SimAI API, your :class:`~ansys.simai.core.client.SimAIClient`
instance must be authenticated. By default, you are prompted to log in
via your web browser. However, you can pass your credentials as parameters
on client creation:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="company",
        credentials={
            # neither of these are required, but if they are missing you will be
            # prompted to input them
            "username": "user@company.com",
            "password": "hunter12",
        },
    )

Credential options
------------------

Descriptions follow of all credential options for the :class:`~ansys.simai.core.client.SimAIClient`
class:

.. autopydantic_model:: Credentials
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-validator-members: False
  :model-show-json: False
  :field-list-validators: False

.. _Interactive mode:

Interactive mode
------------------

When the property `interactive` is set to `true`, the users are prompted for the missing configuration
properties.
When the property is `false`, the interactive mode is turned off, and errors would be raised
in case of missing configuration properties.
Default behavior is `interactive=true`.

It is important to note that login through web browser is turned off when `interactive=false`.
This means that either ``credentials`` or ``offline_token`` must be provided, otherwise
an error would be raised.

.. _offline_tokens:

Offline tokens
--------------

Offline tokens are long-lived authentication tokens that can be used for non-interactive
authentication. Unlike regular session tokens, offline tokens don't expire based on session
timeouts, making them ideal for server-side scripts, CI/CD pipelines, and automated workflows.

Generating an offline token
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can generate an offline token using an authenticated client:

.. code-block:: python

    import ansys.simai.core as asc

    # First, authenticate interactively
    simai_client = asc.SimAIClient(organization="my-company")

    # Generate an offline token
    token = simai_client.me.generate_offline_token()
    print(f"Store this token securely: {token}")

.. warning::

    Store your offline token securely. It provides full access to your account
    and should be treated like a password.

Using an offline token
^^^^^^^^^^^^^^^^^^^^^^

Once you have an offline token, you can use it for non-interactive authentication:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="my-company",
        offline_token="your-offline-token-here",
        interactive=False,
    )

Or in a configuration file:

.. code-block:: toml

    [default]
    organization = "my-company"
    offline_token = "your-offline-token-here"
    interactive = false

Managing consents
^^^^^^^^^^^^^^^^^

Consents are the authorization records that grant a client (like the SDK) permission
to use offline tokens. You can list and revoke consents through the client:

.. code-block:: python

    # List all consents
    consents = simai_client.me.consents.list()
    for consent in consents:
        print(f"Client: {consent.client_id}, Created: {consent.created_date}")

    # Revoke a specific consent (invalidates associated offline tokens)
    simai_client.me.consents.revoke("sdk")

.. note::

    You cannot use both ``credentials`` and ``offline_token`` at the same time.
    Choose one authentication method.
