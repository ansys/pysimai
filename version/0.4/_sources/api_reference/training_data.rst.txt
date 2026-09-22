.. _training_data:

TrainingData
============

.. py:module:: ansys.simai.core.data.training_data

A :class:`TrainingData<ansys.simai.core.data.training_data.TrainingData>` instance is a
collection of :class:`TrainingDataPart<ansys.simai.core.data.training_data_parts.TrainingDataPart>`
instances representing a simulation that can be used as input for the training of models.

.. note::

    For standard workflows, the :meth:`upload_folder()<TrainingDataDirectory.upload_folder>` feature is recommended
    as it simplifies the process and automatically handles data extraction.

Directory
---------

.. autoclass:: TrainingDataDirectory()
    :members:

Model
-----

.. autoclass:: TrainingData()
    :members:
    :inherited-members:
