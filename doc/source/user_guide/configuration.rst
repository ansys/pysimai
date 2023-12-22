.. _configuration:
.. py:module:: ansys.simai.core.utils.configuration

Client Configuration
====================

Where to start
--------------

You can start by creating an `SimAIClient`, you will
be prompted for any missing parameter (see :ref:`getting started<index>`).

You can then start configuring the :class:`~ansys.simai.core.client.SimAIClient`
by passing the required parameters on client creation, like so:

.. code-block:: python

    import ansys.simai.core

    simai = ansys.simai.core.SimAIClient(organization="my-company")

Once you understand how this works, we recommend looking into the SimAI
:ref:`configuration file<config_file>`.


Available options
-----------------

All of the configuration variables for :class:`~ansys.simai.core.client.SimAIClient`
are documented in the following class:

.. autopydantic_model:: ClientConfig
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-json: False
  :model-show-field-summary: False


Credentials
+++++++++++

To use SimAI API your SDK needs to be authenticated.

By default, :class:`~ansys.simai.core.client.SimAIClient` will prompt you to log in
via your web browser.

You can also pass your credentials as parameters on client creation, like so:

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
