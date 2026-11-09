.. _projects:

Projects
========

.. py:module:: ansys.simai.core.data.projects

Projects are a selection of training data used to train a model.

Directory
---------

.. autoclass:: ProjectDirectory()
    :members:

Model
-----

.. autoclass:: Project()
    :members:
    :inherited-members:

IsTrainableInfo
---------------

.. autoclass:: IsTrainableInfo()
    :members:
    :exclude-members: is_trainable, reason

.. vale Google.Headings = NO

TrainingCapabilities
--------------------

.. vale Google.Headings = YES

.. autoclass:: TrainingCapabilities()
    :members:

.. vale Google.Headings = NO

ContinuousLearningCapabilities
------------------------------

.. vale Google.Headings = YES

.. autoclass:: ContinuousLearningCapabilities()
    :members:
