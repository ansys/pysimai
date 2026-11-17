:description: Follow the SimAI model workflow in PySimAI, from preparing training data to building, evaluating, predicting, postprocessing, and optimizing designs.

.. _ref_pysimai_guide:

.. _simai_models_index:

SimAI user guide
================

**Applies to:** SimAI models

A SimAI model is the type of AI model that Ansys SimAI trains on simulation data. It predicts
physical fields for new geometries. These pages show how to work with SimAI models from
Python with PySimAI, in the order of the workflow.

Workflow of a SimAI model
-------------------------

A SimAI model project goes through four stages. PySimAI covers the second and third stages, which run
on the Ansys SimAI platform.

#. Prepare the data, outside Ansys SimAI: convert your simulation results to the supported
   formats and optimize them for upload.
#. Upload the training data, configure the model, and build it, on the Ansys SimAI platform.
#. Run predictions on new geometries and generate postprocessings, on the Ansys SimAI platform.
#. Analyze and validate the results inside or outside the Ansys SimAI platform.

In PySimAI, the steps are:

#. :doc:`Prepare the training data </user-guide/simai-models/prepare-training-data>`: one simulation folder
   per simulation case, with a surface file, plus a volume file and a scalar file when needed.
#. :doc:`Upload the training data </user-guide/simai-models/upload-training-data>` to your organization and
   add it to a project.
#. :doc:`Assign the training data points to subsets </user-guide/simai-models/assign-subsets>`, if you don't
   want the default random split between the training subset and the test subset.
#. :doc:`Configure the SimAI model </user-guide/simai-models/configure-a-model>`: model inputs, model outputs,
   global coefficients, Domain of Analysis, and build setting.
#. :doc:`Build the SimAI model </user-guide/simai-models/build-a-model>` and follow the model build.
#. :doc:`Evaluate the SimAI model </user-guide/simai-models/evaluate-a-model>` with its Model Evaluation Report.
#. :doc:`Run predictions </user-guide/simai-models/run-predictions>` on new geometries in the workspace of the
   SimAI model.
#. :doc:`Run postprocessings </user-guide/simai-models/postprocess-predictions>` on the predictions to get
   global coefficients and field files.
#. :doc:`Explore many predictions at once </user-guide/simai-models/explore-predictions-with-selections>`
   with selections.
#. :doc:`Optimize a design </user-guide/simai-models/optimization-overview>` with non-parametric optimization.

Before you start
----------------

Install PySimAI and configure the client first. For more information, see
:doc:`/getting-started/index`. Tasks that apply to both types of AI model, such as waiting for
results, are in :doc:`/user-guide/common-tasks/index`.

The gallery has runnable scripts for the main steps: :ref:`ref_basic_create_project_upload_data`,
:ref:`ref_basic_build_model`, and :ref:`ref_basic_run_predictions`.

.. toctree::
   :maxdepth: 2
   :hidden:

   prepare-training-data
   upload-training-data
   assign-subsets
   build-settings
   configure-a-model
   build-a-model
   evaluate-a-model
   run-predictions
   postprocess-predictions
   explore-predictions-with-selections
   optimization-overview
