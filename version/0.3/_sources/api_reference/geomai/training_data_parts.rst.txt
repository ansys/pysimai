.. _geomai_training_data_parts:

GeomAITrainingDataParts
=======================

.. py:module:: ansys.simai.core.data.geomai.training_data_parts

A :class:`GeomAITrainingDataPart<ansys.simai.core.data.geomai.training_data_parts.GeomAITrainingDataPart>` instance
is a singular file that is part of a :class:`~ansys.simai.core.data.geomai.training_data.GeomAITrainingData`
instance.

.. warning::
   It is strongly recommended to use
   :meth:`GeomAITrainingData.create_file<ansys.simai.core.data.geomai.training_data.GeomAITrainingDataDirectory.create_from_file>`
   instead of interacting with parts directly.

Directory
---------

.. autoclass:: GeomAITrainingDataPartDirectory()
    :members:

Model
-----

.. autoclass:: GeomAITrainingDataPart()
    :members:
    :inherited-members:
