:description: Organize simulation results into simulation folders with a surface file, a volume file, and a scalar file before you upload them as training data for a SimAI model.

.. _simai_models_prepare_training_data:

Prepare the training data of a SimAI model
==========================================

**Applies to:** SimAI models

Before you upload training data with PySimAI, put the files of each simulation case in its
own simulation folder. After upload, each simulation folder becomes one training data point,
represented in PySimAI by a :class:`~ansys.simai.core.data.training_data.TrainingData` object.

Structure of a simulation folder
--------------------------------

A simulation folder holds the files of one simulation case. Each file type appears at most
once in a simulation folder.

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - File
     - Format
     - Required
     - Content and naming rule
   * - Surface file
     - ``.vtp``
     - Yes
     - The geometry and the surface fields. The filename contains ``surface``.
   * - Volume file
     - ``.vtu``
     - No
     - The volume fields. Add it only if the SimAI model must predict volume fields.
       The filename contains ``volume``.
   * - Scalar file
     - ``.json``
     - No
     - The scalars of the case, as name and value pairs without units. The filename
       contains ``scalar`` or ``boundary``.

Example of a dataset with two simulation folders:

.. code-block:: text

   dataset/
   ├── case_001/
   │   ├── surface.vtp
   │   ├── volume.vtu
   │   └── scalars.json
   └── case_002/
       ├── surface.vtp
       ├── volume.vtu
       └── scalars.json

Content of a scalar file
------------------------

The scalar file lists the scalars of one simulation case, such as an inlet velocity or a
fluid temperature. Each scalar is a name and a value, with no unit:

.. code-block:: json

   {
       "Vx": 12.4,
       "Temperature": 293.15
   }

The scalars you choose as model inputs must exist in every training data point of the
project.

How the files of a simulation folder become a training data point
-----------------------------------------------------------------

When you upload a simulation folder, PySimAI uploads each file as a
:class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart` object of the
training data point. Each part has a name, the filename, and a size in bytes.

Ansys SimAI extracts the data from the training data point once all its parts are
uploaded. The :meth:`~ansys.simai.core.data.training_data.TrainingData.upload_folder`
method requests this extraction for you. If you upload files one by one, call
:meth:`~ansys.simai.core.data.training_data.TrainingData.extract_data` after the last file.
For more information, see :doc:`/user-guide/simai-models/upload-training-data`.

More about how to prepare the training data of a SimAI model
------------------------------------------------------------

- :doc:`/user-guide/simai-models/upload-training-data`
- :ref:`ref_basic_create_project_upload_data`
- :class:`~ansys.simai.core.data.training_data.TrainingData`
- :class:`~ansys.simai.core.data.training_data_parts.TrainingDataPart`
