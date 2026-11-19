:description: Install PySimAI, configure and authenticate the PySimAI client, and run a first end-to-end script for a SimAI model or a GeomAI model.

.. _ref_configuration_guide:

Getting started
===============

Start here to learn the concepts of Ansys SimAI and PySimAI, then install PySimAI, connect it to your
:term:`organization`, and run a first complete script.

Overview
--------

- :doc:`/getting-started/overview/key-concepts`: the Ansys SimAI platform and its two types of AI model.
- :doc:`/getting-started/overview/architecture`: one client and separate data for each type of AI model.
- :doc:`/getting-started/overview/object-model`: the objects of PySimAI and how to reach them.
- :doc:`/getting-started/overview/web-app-or-pysimai`: when to use the web app and when to use PySimAI.
- :doc:`/getting-started/overview/glossary`: the terms of Ansys SimAI and PySimAI.

Getting started
---------------

#. :doc:`/getting-started/install`
#. :doc:`/getting-started/configure-the-client`, either in your script or in a
   :doc:`configuration file </getting-started/use-a-configuration-file>`.
   If your network uses a proxy, see :doc:`/getting-started/work-behind-a-proxy`.
#. :doc:`/getting-started/authenticate`, through the web browser, with credentials, or with a
   token for scripts that run without a user.
#. Run a quickstart for the type of AI model you need. To choose, see
   :doc:`/getting-started/overview/key-concepts`.

   - :doc:`/getting-started/quickstart-simai-model` predicts physical fields on new geometries.
   - :doc:`/getting-started/quickstart-geomai-model` generates new geometries.

.. toctree::
   :caption: Overview
   :maxdepth: 1
   :hidden:

   overview/key-concepts
   overview/architecture
   overview/object-model
   overview/web-app-or-pysimai
   overview/glossary

.. toctree::
   :caption: Getting started
   :maxdepth: 1
   :hidden:

   install
   configure-the-client
   authenticate
   use-a-configuration-file
   work-behind-a-proxy
   quickstart-simai-model
   quickstart-geomai-model
