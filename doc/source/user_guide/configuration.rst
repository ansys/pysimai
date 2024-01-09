.. _configuration:
.. py:module:: ansys.simai.core.utils.configuration

Client configuration
====================

Where to start
--------------

You start by creating a :class:`~ansys.simai.core.client.SimAIClient`
instance. As indicated in :ref:`getting started`, you are prompted for any missing parameters.

You configure this instance by passing the required parameters on client creation:

.. code-block:: python

    import ansys.simai.core

    simai = ansys.simai.core.SimAIClient(organization="my-company")

Once you understand how this works, you can look into using a
:ref:`configuration file<config_file>` to start a client instance.


Available options
-----------------

All configuration variables for :class:`~ansys.simai.core.client.SimAIClient`
are documented in the following class:

.. autopydantic_model:: ClientConfig
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-json: False
  :model-show-field-summary: False


Credentials
+++++++++++

To use SimAI API, your :class:`~ansys.simai.core.client.SimAIClient`
instance must be authenticated. By default, you are prompted to log in
via your web browser.

However, you can pass your credentials as parameters on client creation:

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

.. autopydantic_model:: Credentials
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-json: False
