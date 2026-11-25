:description: PySimAI is the Python SDK for Ansys SimAI: install it, then upload training data, build SimAI models and GeomAI models, run predictions, and generate geometries from Python.

.. _index:

.. _home_index:

PySimAI documentation
=====================

**Applies to:** SimAI models and GeomAI models

Release v\ |version| (:ref:`Changelog <changelog>`)

PySimAI is the Python SDK for :term:`Ansys SimAI`, distributed as the ``ansys-simai-core``
package. It gives Python apps and scripts access to almost all the features of the Ansys SimAI
web app, for both types of :term:`AI model` that the platform trains:

- :term:`SimAI models <SimAI model>` train on simulation data and predict the physical fields of
  new geometries in minutes.
- :term:`GeomAI models <GeomAI model>` train on geometries only and generate new geometries in
  the same design language as their training data.

PySimAI is part of the `PyAnsys <https://docs.pyansys.com>`_ ecosystem, so you can combine it
with other PyAnsys libraries and any Python library.

Who PySimAI is for
------------------

PySimAI is for Python developers who script and automate Ansys SimAI, or who connect it to
other tools of a workflow. You need an account in an Ansys SimAI :term:`organization`. Users who
don't write code use the web app at https://simai.ansys.com instead. To compare the two, and to
see the tasks that only PySimAI makes practical, such as uploading many simulation folders in
parallel, see :doc:`/getting-started/overview/web-app-or-pysimai`.

What you can do with PySimAI
----------------------------

With SimAI models, PySimAI lets you:

- Create projects and upload simulation folders as training data.
- Configure and build SimAI models.
- Upload geometries to a workspace and run predictions on them.
- Compute global coefficients and other postprocessings, and download the results.
- Run design optimizations.

With GeomAI models, PySimAI lets you:

- Create projects and upload geometry files as training data.
- Configure and build GeomAI models.
- Generate new geometries from :term:`latent parameters <latent parameter>`, and project existing
  geometries onto the :term:`latent space` of a model.

For both types of AI model, PySimAI lets you download the Model Evaluation Report, wait for
objects, handle errors, and list, rename, or delete resources.

Each type of AI model has its own client and its own data in PySimAI. For details, see
:doc:`/getting-started/overview/architecture`.

Where to start
--------------

- To understand the platform and choose the type of AI model, read :doc:`/getting-started/overview/key-concepts`.
- To install PySimAI and run a first script, go to :doc:`/getting-started/index`.

For the web app, see the `Ansys SimAI User's guide <https://ansyshelp.ansys.com/public/account/secured?returnURL=%2Fpublic%2FViews%2FSecured%2FSimAI%2Fv000%2Fen%2FSimAI_ug%2Findex.html>`_.

What do you want to do?
-----------------------

.. grid:: 1 2 3 3
    :gutter: 3

    .. grid-item-card:: :octicon:`download` Install and configure PySimAI
        :link: /getting-started/install
        :link-type: doc

        Install the ``ansys-simai-core`` package, then configure and authenticate the client.

    .. grid-item-card:: :octicon:`play` Browse the example scripts
        :link: /_examples/index
        :link-type: doc

        Copy and adapt complete scripts for SimAI models and GeomAI models.

    .. grid-item-card:: :octicon:`file-code` Look up a class or method
        :link: /api_reference
        :link-type: doc

        Find the parameters, return values, and exceptions of the public API.

    .. grid-item-card:: :octicon:`rocket` Build a first SimAI model
        :link: /getting-started/quickstart-simai-model
        :link-type: doc

        Run one script that uploads training data, builds a SimAI model, and runs a prediction.

    .. grid-item-card:: :octicon:`graph` Run predictions with a SimAI model
        :link: /user-guide/simai-models/run-predictions
        :link-type: doc

        Upload a geometry to a workspace and predict its physical fields.

    .. grid-item-card:: :octicon:`zap` Optimize a design with a SimAI model
        :link: /user-guide/simai-models/optimize-a-design
        :link-type: doc

        Run a non-parametric optimization that deforms a baseline geometry to improve a global coefficient.

    .. grid-item-card:: :octicon:`beaker` Build a first GeomAI model
        :link: /getting-started/quickstart-geomai-model
        :link-type: doc

        Run one script that uploads geometries, builds a GeomAI model, and generates new geometries.

    .. grid-item-card:: :octicon:`package` Generate geometries with a GeomAI model
        :link: /user-guide/geomai-models/generate-geometries
        :link-type: doc

        Generate new geometries from the latent space of a trained GeomAI model.

    .. grid-item-card:: :octicon:`git-compare` Interpolate and project geometries
        :link: /user-guide/geomai-models/interpolate-and-project
        :link-type: doc

        Interpolate between two geometries in the latent space, or project a geometry onto it.

.. toctree::
   :maxdepth: 1
   :hidden:

   getting-started/index
   user-guide/index
   api_reference
   _examples/index
   changelog
