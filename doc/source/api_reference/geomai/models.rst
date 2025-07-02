.. _geomai_models:

GeomAIModels
============

.. py:module:: ansys.simai.core.data.geomai.models

To build a GeomAI model, use :py:meth:`GeomAIProject.build_model<ansys.simai.core.data.geomai.projects.GeomAIProject.build_model>`.


Directory
---------

.. autoclass:: GeomAIModelDirectory()
    :members:
    :exclude-members: get


Model
-----

.. autoclass:: GeomAIModel()
    :members:
    :inherited-members:


GeomAIModelConfiguration
------------------------

.. autopydantic_model:: GeomAIModelConfiguration
  :model-show-config-summary: False
  :model-show-validator-summary: False
  :model-show-json: False
  :model-show-field-summary: False
  :model-show-validator-members: False
  :field-list-validators: False
  :field-show-constraints: False
