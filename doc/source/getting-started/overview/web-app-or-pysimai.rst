:description: Compare the Ansys SimAI web app and PySimAI, the Python SDK: who each one is for, and the tasks that only PySimAI makes possible or practical.

.. TODO: validate the full feature comparison with the product team.

.. _concepts_web_app_or_pysimai:

Choose between the web app and PySimAI
======================================

**Applies to:** SimAI models and GeomAI models

You can use Ansys SimAI in two ways: the web app at https://simai.ansys.com, and PySimAI, the
Python SDK. They give access to almost the same features.

The web app
-----------

The web app is for users who don't write code: simulation and methods engineers who build models
in projects, and simulation experts and designers who run predictions in workspaces. It needs no
programming knowledge. For its documentation, see the
`Ansys SimAI User's guide <https://ansyshelp.ansys.com/public/account/secured?returnURL=%2Fpublic%2FViews%2FSecured%2FSimAI%2Fv000%2Fen%2FSimAI_ug%2Findex.html>`_.

PySimAI
-------

PySimAI is for Python developers who script and automate Ansys SimAI, or who connect it to other
tools of a workflow. Install it with ``pip install ansys-simai-core``.

Tasks that need PySimAI
-----------------------

PySimAI makes these tasks possible or practical:

Assign training data points to subsets by hand
   By default, a model build splits the training data at random between the training subset and
   the test subset. With PySimAI, you choose the subset of each training data point with
   :meth:`TrainingData.assign_subset() <ansys.simai.core.data.training_data.TrainingData.assign_subset>`.
   See :ref:`ref_subset_assignment`.

Upload many simulation folders in parallel
   The web app sends you to PySimAI when you upload more than 50 simulation folders. A script can
   upload many folders in parallel. See :ref:`ref_multiprocess_upload`.

Automate repeated work
   A script can loop over geometries and scalars to run many predictions, and explore the results
   with selections. See :doc:`/user-guide/simai-models/explore-predictions-with-selections`.

More about how to choose between the web app and PySimAI
--------------------------------------------------------

- :doc:`/getting-started/overview/key-concepts`
- :doc:`/getting-started/install`
- :doc:`/getting-started/overview/object-model`
