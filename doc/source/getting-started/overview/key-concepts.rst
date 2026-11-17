:description: Key concepts of Ansys SimAI: the platform, its two types of AI model, SimAI models, which predict physical fields, and GeomAI models, which generate geometries, and how to choose between them.

.. _concepts_platform:

Key concepts of Ansys SimAI
===========================

**Applies to:** SimAI models and GeomAI models

Ansys SimAI is a SaaS platform for building and using AI models in industrial design. You use
it from the web app at https://simai.ansys.com, or from Python with PySimAI. Ansys SimAI trains
two types of :term:`AI model`, SimAI models and GeomAI models, which have separate data. For how
the two types are kept apart, see :doc:`/getting-started/overview/architecture`.

The Ansys SimAI platform
------------------------

All the users of one company belong to an :term:`organization`. In an organization, you upload
:term:`training data`, gather it in a :term:`project` with a :term:`model configuration`, and
start a :term:`model build`. Each successful model build creates a :term:`workspace`, where you
use the trained AI model. For how these objects relate in PySimAI, see
:doc:`/getting-started/overview/object-model`.

SimAI models
------------

A :term:`SimAI model` trains on simulation data: each training data point is one simulation
case, with its geometry, its surface and volume fields, and its scalars. Once built, a SimAI
model predicts the physical fields of a new geometry in minutes, for the scalars you choose.
After a prediction, you compute global coefficients and other postprocessings.

In PySimAI, you work with SimAI models directly through the client:
``simai_client.projects``, ``simai_client.training_data``, ``simai_client.workspaces``, and so
on.

GeomAI models
-------------

A :term:`GeomAI model` trains on geometries only, with no simulation data. It learns a compressed
representation of the geometries, the latent space, and generates new geometries in the same
design language as its training data. A GeomAI model doesn't predict physical fields.

In PySimAI, you work with GeomAI models through their own client,
:class:`~ansys.simai.core.data.geomai.client.GeomAIClient`, that you get with
``simai_client.geomai``: ``simai_client.geomai.projects``,
``simai_client.geomai.training_data``, and so on. GeomAI models are a type of AI model of the
same platform, not a separate product: they use the same organization and the same
authentication as SimAI models.

Choose the type of AI model
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - What you need
     - Type of AI model
     - Start with
   * - Predict physical fields, such as pressure or velocity, or global coefficients, such as
       drag or lift, for a new geometry
     - SimAI model
     - :doc:`/getting-started/quickstart-simai-model`
   * - Generate new geometries similar to existing ones, or explore variations of a design
     - GeomAI model
     - :doc:`/getting-started/quickstart-geomai-model`

The choice depends on your data too. A SimAI model needs simulation results for every training
data point. A GeomAI model needs only geometry files. Training data uploaded for one type of AI
model can't train the other type.

More about the key concepts of Ansys SimAI
------------------------------------------

- :doc:`/getting-started/overview/architecture`
- :doc:`/getting-started/overview/object-model`
- :doc:`/getting-started/overview/glossary`
- :doc:`/getting-started/overview/web-app-or-pysimai`
- :doc:`/user-guide/simai-models/index`
- :doc:`/user-guide/geomai-models/index`
