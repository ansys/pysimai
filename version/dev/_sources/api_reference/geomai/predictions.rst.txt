.. _geomai_predictions:

GeomAIPredictions
=================

.. py:module:: ansys.simai.core.data.geomai.predictions

The ``Prediction`` module is in charge of running the *GeomAI-powered
predictions* in your :py:class:`workspaces<ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace>`.

Directory
---------

.. autoclass:: GeomAIPredictionDirectory()
    :members:

Model
-----

.. autoclass:: GeomAIPrediction()
    :members:
    :inherited-members:

Configuration
-------------

.. autopydantic_model:: GeomAIPredictionConfiguration
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-json: False
  :model-show-field-summary: False
  :model-show-validator-members: False
  :field-list-validators: False
  :field-show-constraints: False
