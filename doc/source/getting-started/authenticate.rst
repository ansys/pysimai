:description: Authenticate the PySimAI client with Ansys SimAI: sign in through the browser, with credentials, an offline token or an access token, turn off interactive mode, and manage consents.

.. _getting_started_authenticate:
.. py:currentmodule:: ansys.simai.core.utils.configuration

Authenticate with Ansys SimAI
=============================

**Applies to:** SimAI models and GeomAI models

The :class:`~ansys.simai.core.client.SimAIClient` instance must be authenticated before it can
access your Ansys SimAI organization. You can sign in through the web browser, pass
credentials, or use a token for scripts that run without prompts. The GeomAI client, ``simai_client.geomai``, uses the authentication of the PySimAI client: you
authenticate once for both types of AI model.

To create and configure the client, see :doc:`/getting-started/configure-the-client`.

Choose an authentication method
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Method
     - Use it when
   * - Web browser (default)
     - You run a script yourself. The client opens your web browser so that you can sign in.
   * - :ref:`Credentials <anchor-credentials>`
     - You run a script yourself and don't want to sign in through the browser.
   * - :ref:`Offline token <offline_tokens>`
     - A script runs without a user, for example on a server or in an automated workflow.
   * - :ref:`Access token <access_tokens>`
     - A CI pipeline already obtained a short-lived token through OIDC.

Pass only one of ``credentials``, ``offline_token``, and ``access_token``.

.. _anchor-credentials:

Authenticate with your credentials
----------------------------------

The :class:`~ansys.simai.core.client.SimAIClient` instance must be authenticated. By default,
it prompts you to sign in through your web browser. You can also pass your credentials when
you create the client:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="<your_organization>",
        credentials={
            # If one of these keys is missing, the client prompts you for it
            "username": "<your_email>",
            "password": "<your_password>",
        },
    )

Don't write a password in a script that you share or commit. For scripts that run without a
user, use an :ref:`offline token <offline_tokens>` or an :ref:`access token <access_tokens>`.

The ``credentials`` parameter accepts these options:

.. autopydantic_model:: Credentials
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-validator-members: False
  :model-show-json: False
  :field-list-validators: False

.. _Interactive mode:

Turn off interactive mode
-------------------------

The ``interactive`` parameter controls prompts. Its default value is ``True``: the client
prompts you for every missing parameter.

With ``interactive=False``, the client never prompts. It raises an error when a parameter is
missing, and it can't open the web browser to sign you in. You must then pass
``credentials``, ``offline_token``, or ``access_token``.

.. _offline_tokens:

Authenticate with an offline token
----------------------------------

An offline token is a long-lived authentication token for non-interactive authentication.
Unlike session tokens, it doesn't expire with the session, so it suits server-side scripts and
automated workflows. For CI pipelines that obtain a short-lived token through OIDC (for
example, GitHub Actions federated with Keycloak), use an :ref:`access token <access_tokens>`
instead.

Generate an offline token
^^^^^^^^^^^^^^^^^^^^^^^^^

Generate the token with an authenticated client:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    token = simai_client.me.generate_offline_token()
    print(f"Store this token securely: {token}")

.. warning::

    An offline token gives full access to your account. Store it as securely as a password.

Use an offline token
^^^^^^^^^^^^^^^^^^^^

Pass the token when you create the client:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="<your_organization>",
        offline_token="<your_offline_token>",
        interactive=False,
    )

You can also store it in a configuration file:

.. code-block:: toml

    [default]
    organization = "<your_organization>"
    offline_token = "<your_offline_token>"
    interactive = false

For more about configuration files, see :doc:`/getting-started/use-a-configuration-file`.

.. _getting_started_manage_consents:

Manage consents
---------------

A consent is the authorization record that lets a client, such as PySimAI, use offline tokens.
It's the offline access authorization that the :ref:`offline tokens <offline_tokens>` of this
client depend on. List and revoke consents through the client:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(organization="<your_organization>")

    # List all consents
    consents = simai_client.me.consents.list()
    for consent in consents:
        print(f"Client: {consent.client_id}, Created: {consent.created_date}")

    # Revoke a consent: this invalidates the offline tokens associated with it
    simai_client.me.consents.revoke("sdk")

.. _access_tokens:

Authenticate with an access token
---------------------------------

An access token is a short-lived OIDC bearer token issued before the script runs. It suits
CI/CD pipelines where an earlier step already obtained a token, for example GitHub Actions
OIDC exchanged with Keycloak. PySimAI doesn't refresh access tokens: when the token expires,
get a new one from your CI login step.

Pass the token when you create the client:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="<your_organization>",
        access_token="<your_access_token>",
        interactive=False,
    )

In CI, you can set the ``SIMAI_ACCESS_TOKEN`` environment variable instead. The client reads it
when you don't pass ``access_token``:

.. code-block:: python

    import ansys.simai.core as asc

    simai_client = asc.SimAIClient(
        organization="<your_organization>",
        interactive=False,
    )

.. warning::

    Don't commit access tokens to source control or to configuration files. Store them in CI
    secrets or in environment variables of the job.

Expected result when you authenticate with Ansys SimAI
------------------------------------------------------

The client is created without an error and can access your organization. With
``interactive=False``, it never prompts and never opens the web browser.

Errors when you authenticate with Ansys SimAI
---------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.InvalidConfigurationError`
     - You combined ``credentials``, ``offline_token``, and ``access_token``, or no
       authentication method is set with ``interactive=False``.
     - Pass exactly one authentication method.
   * - ``RuntimeError``
     - The access token is invalid or expired, or the offline token can't authenticate you.
     - Get a new token.

For all the exceptions, see :doc:`/user-guide/common-tasks/handle-errors`.

More about how to authenticate with Ansys SimAI
-----------------------------------------------

- :doc:`/getting-started/configure-the-client`
- :doc:`/getting-started/use-a-configuration-file`
- :class:`~ansys.simai.core.client.SimAIClient`
- :doc:`/api_reference/current_user`
