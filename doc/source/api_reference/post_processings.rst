.. _post_processings:

Post-Processings
================

.. py:module:: ansys.simai.core.data.post_processings

Directory
---------

.. autoclass:: PostProcessingDirectory
    :members:

Model
-----

.. autoclass:: PostProcessing()
    :members:


.. _pp_methods:

Nested Prediction Namespace
---------------------------

.. autoclass:: PredictionPostProcessings()
    :members:

.. _available_pp:

Available post-processings
--------------------------

.. note:: Depending on the capabilities of your model, some of these may not be available in your workspace.
          You can check which ones are available through the :meth:`~ansys.simai.core.data.post_processings.PostProcessingDirectory.info` method

.. autoclass:: GlobalCoefficients()
    :members:
    :inherited-members: PostProcessing


.. autoclass:: SurfaceEvol()
    :members:
    :inherited-members: PostProcessing


.. autoclass:: Slice()
    :members:


.. autoclass:: SurfaceVTP()
    :members:


.. autoclass:: VolumeVTU()
    :members:


Helpers
-------

.. autoclass:: DownloadableResult()
    :members:
