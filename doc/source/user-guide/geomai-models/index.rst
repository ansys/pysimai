:description: Learn what a GeomAI model is and follow the steps to prepare geometries, build a GeomAI model, and generate new geometries with PySimAI.

.. _ref_generative_design_guide:

GeomAI user guide
=================

**Applies to:** GeomAI models

A GeomAI model is an AI model trained on geometries only. It learns a compressed representation of
your training geometries, called the :term:`latent space`, and generates new geometries that share the
same design language. With PySimAI, you access GeomAI models through
``geomai_client = simai_client.geomai``, an instance of
:class:`~ansys.simai.core.data.geomai.client.GeomAIClient`.

A GeomAI model doesn't use physical response data such as forces, flow fields, or pressure, and it
can't predict them. To predict physical fields from a geometry, use a SimAI model. For more
information, see :doc:`/user-guide/simai-models/index`.

How a GeomAI model works
------------------------

A GeomAI model goes through three stages:

#. You provide a set of geometries as training data.
#. The model build trains the GeomAI model to represent each training geometry as a position in
   the latent space.
#. The trained GeomAI model generates new geometries from new positions in the latent space.

PySimAI organizes this work in two objects:

- A project, :class:`~ansys.simai.core.data.geomai.projects.GeomAIProject`, holds your training
  data, the set of geometries the GeomAI model learns from.
- A workspace, :class:`~ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace`, holds a trained
  GeomAI model and its predictions. One project can have several workspaces, one for each model
  build.

Steps to build and use a GeomAI model
-------------------------------------

Follow these pages in order:

#. :doc:`/user-guide/geomai-models/prepare-training-data`: check that your geometries meet the requirements
   and decide how many you need.
#. :doc:`/user-guide/geomai-models/upload-training-data`: create a project and upload your geometries.
#. :doc:`/user-guide/geomai-models/configure-a-model`: choose a build preset or a number of epochs and the
   number of latent parameters.
#. :doc:`/user-guide/geomai-models/build-a-model`: start the model build, follow it, and cancel it if needed.
#. :doc:`/user-guide/geomai-models/evaluate-a-model`: download the Model Evaluation Report (MER) and check
   the quality of the GeomAI model.
#. :doc:`/user-guide/geomai-models/generate-geometries`: generate random geometries or geometries from
   chosen latent parameters.
#. :doc:`/user-guide/geomai-models/interpolate-and-project`: interpolate between two geometries and project
   an existing geometry onto the latent space.

For complete scripts that you can run, see the GeomAI model examples, starting with
:ref:`ref_create_project_upload_data`.

.. toctree::
   :maxdepth: 1
   :hidden:

   prepare-training-data
   upload-training-data
   configure-a-model
   build-a-model
   evaluate-a-model
   generate-geometries
   interpolate-and-project

More about GeomAI models
------------------------

- :doc:`/user-guide/simai-models/index`
- :doc:`/getting-started/overview/glossary`
- :doc:`/api_reference`
