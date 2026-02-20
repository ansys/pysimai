.. _post_processings:

Postprocessings
===============

.. py:module:: ansys.simai.core.data.post_processings

Directory
---------

.. autoclass:: PostProcessingDirectory
    :members:

Model
-----

.. autoclass:: PostProcessing()
    :members:
    :inherited-members:


.. _pp_methods:

Nested prediction namespace
---------------------------

.. autoclass:: PredictionPostProcessings()
    :members:

.. _available_pp:

Available postprocessings
--------------------------

.. note::
    Depending on the capabilities of your model, some of these objects may not
    be available in your workspace. You can use the
    :meth:`~ansys.simai.core.data.post_processings.PostProcessingDirectory.info` method
    to see which ones are available.

.. autoclass:: GlobalCoefficients()
    :members:
    :inherited-members: PostProcessing


.. autoclass:: SurfaceEvolution()
    :members:
    :inherited-members: PostProcessing


.. autoclass:: Slice()
    :members:


.. autoclass:: SurfaceVTP()
    :members:


.. autoclass:: SurfaceVTPTDLocation()
    :members:


.. autoclass:: VolumeVTU()
    :members:


.. autoclass:: CustomVolumePointCloud()
    :members:


Helpers
-------

.. autoclass:: DownloadableResult()
    :members: