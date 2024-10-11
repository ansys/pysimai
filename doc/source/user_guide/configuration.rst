.. _configuration:
.. py:module:: ansys.simai.core.utils.configuration

Client configuration
====================

Where to start
--------------

You start by creating a :class:`~ansys.simai.core.client.SimAIClient`
instance:

.. code-block:: python

    import ansys.simai.core

    simai = ansys.simai.core.SimAIClient(organization="my-company")


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

    simai = ansys.simai.core.SimAIClient(
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

It is important to note that login through web browser is turned off and credentials become required when `interactive=false`.
This means that if the credentials are missing, the users won't be prompted to enter them
from the terminal, and an error would be raised instead.
