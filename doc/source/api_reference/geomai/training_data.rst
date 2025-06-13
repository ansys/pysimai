.. _geomai_training_data:

GeomAITrainingData
==================

.. py:module:: ansys.simai.core.data.geomai.training_data

A :class:`GeomAITrainingData<ansys.simai.core.data.geomai.training_data.GeomAITrainingData>` instance is a
collection of :class:`GeomAITrainingDataPart<ansys.simai.core.data.geomai.training_data_parts.GeomAITrainingDataPart>`
instances representing a geometry that can be used as input for the training of models.
In most cases it will contain a single part: the geometry to train on.

Directory
---------

.. autoclass:: GeomAITrainingDataDirectory()
    :members:

Model
-----

.. autoclass:: GeomAITrainingData()
    :members:
    :inherited-members:
