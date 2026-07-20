.. _model_configuration:

Model configuration
===================

.. py:module:: ansys.simai.core.data.model_configuration

This module contains a collection of classes for creating a model configuration.
The model configuration defines the model's inputs, outputs, Global Coefficients,
build duration and project. The resulting
(:py:class:`ModelConfiguration<ansys.simai.core.data.model_configuration.ModelConfiguration>`)
object is subsequently used to train a model.


GlobalCoefficientDefinition
---------------------------

.. autoclass:: GlobalCoefficientDefinition()
    :members:


DomainAxisDefinition
--------------------

.. autoclass:: DomainAxisDefinition()


DomainOfAnalysis
--------------------

.. autoclass:: DomainOfAnalysis()


ModelInput
----------

.. autoclass:: ModelInput()
    :members:

ModelOutput
-----------

.. autoclass:: ModelOutput()
    :members:

ModelConfiguration
------------------

.. autoclass:: ModelConfiguration()
    :members:

PostProcessInput
-----------------

.. autoclass:: PostProcessInput()
    :members:
