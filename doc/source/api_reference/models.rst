.. _models:

Build Model
==============

.. py:module:: ansys.simai.core.data.models

A collection for classes for launching a build of a SimAI model.
Launing a build requires a configuration
(:py:class:`ModelConfiguration<ansys.simai.core.data.models.ModelConfiguration>`)
with defines the model  properties, such as its inputs and outputs,
the Global Coefficients and the Domain of Analysis, and its project id. The
:py:class:`ModelConfiguration<ansys.simai.core.data.models.ModelConfiguration>`
object is, then, parsed to :py:meth:`models.build()<ModelDirectory.build>` for
launching a build.


ModelConfiguration
------------------

.. autoclass:: ModelConfiguration()
    :members:


Directory
---------

.. autoclass:: ModelDirectory()
    :members:
    :exclude-members: get


Model
---------

.. autoclass:: Model()
    :members:
