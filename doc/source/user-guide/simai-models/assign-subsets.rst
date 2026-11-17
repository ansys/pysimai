:description: Assign the training data points of a project to the training subset or the test subset with TrainingData.assign_subset, instead of the default random 90% and 10% split.

.. _simai_models_assign_subsets:

Assign training data points to the training subset or the test subset
=====================================================================

**Applies to:** SimAI models

Choose which training data points of a project train the SimAI model and which ones test it,
with :meth:`TrainingData.assign_subset() <ansys.simai.core.data.training_data.TrainingData.assign_subset>`.
By default, each model build splits the training data at random: 90% in the training subset and
10% in the test subset.

Training subset and test subset
-------------------------------

The training subset trains the SimAI model. The test subset isn't learned by the SimAI model:
the Model Evaluation Report uses it to measure the errors of the model. For more information,
see :doc:`/user-guide/simai-models/evaluate-a-model`.

When you assign subsets by hand:

- Each subset needs at least one training data point.
- The recommended test subset is about 10% of the training data, and no more than 1,000
  training data points.

A training data point added to a project has no subset. Training data points with no subset are
allocated at random to one of the two subsets at each model build request.

The subset of a training data point is set in relation to one project. The same training data
point can be in the training subset of one project and in the test subset of another.

Assign a subset to a training data point
----------------------------------------

Call :meth:`~ansys.simai.core.data.training_data.TrainingData.assign_subset` with the project,
as an object or an ID, and the subset. The subset is a
:class:`~ansys.simai.core.data.types.SubsetEnum` value or its string value:

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.types import SubsetEnum

   simai_client = asc.SimAIClient(organization="<your_organization>")
   project = simai_client.projects.get(name="<your_project_name>")

   training_data = simai_client.training_data.get(name="<your_training_data_name>")

   training_data.assign_subset(project, SubsetEnum.TEST)
   # Equivalent:
   training_data.assign_subset(project, "Test")

The accepted values are ``SubsetEnum.TRAINING`` or ``"Training"``, and ``SubsetEnum.TEST`` or
``"Test"``. Any other value raises :class:`~ansys.simai.core.errors.InvalidArguments`.

This script puts the training data points listed in ``TEST_LIST`` in the test subset and all the
other training data points of the project in the training subset.

.. code-block:: python

   import ansys.simai.core as asc

   TEST_LIST = ["<your_test_training_data_name_1>", "<your_test_training_data_name_2>"]

   simai_client = asc.SimAIClient(organization="<your_organization>")
   project = simai_client.projects.get(name="<your_project_name>")

   for training_data in project.list_training_data():
       if training_data.name in TEST_LIST:
           training_data.assign_subset(project, "Test")
       else:
           training_data.assign_subset(project, "Training")
       print(training_data.name, training_data.get_subset(project))

Read the subset of a training data point
----------------------------------------

Call :meth:`~ansys.simai.core.data.training_data.TrainingData.get_subset` with the project. The
method returns a :class:`~ansys.simai.core.data.types.SubsetEnum` value, or ``None`` if the
training data point has no subset in this project:

.. code-block:: python

   subset = training_data.get_subset(project)
   print(subset)

Reset the subset of a training data point
-----------------------------------------

To go back to the random allocation for a training data point, assign ``None``:

.. code-block:: python

   training_data.assign_subset(project, None)

Expected result when you assign training data points to the training subset or the test subset
----------------------------------------------------------------------------------------------

The ``TEST_LIST`` loop in "Assign a subset to a training data point" prints the name and the
subset of each training data point of the project:

.. code-block:: text

   <your_test_training_data_name_1> SubsetEnum.TEST
   case_003 SubsetEnum.TRAINING

Errors when you assign training data points to the training subset or the test subset
-------------------------------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The subset isn't ``None``, ``"Training"``, ``"Test"``, or a
       :class:`~ansys.simai.core.data.types.SubsetEnum` value.
     - Use one of the accepted values. The strings are case-sensitive.
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No project or training data point has this name or ID.
     - Check the name or the ID.

More about how to assign training data points to the training subset or the test subset
---------------------------------------------------------------------------------------

- :ref:`ref_subset_assignment`
- :ref:`ref_list_based_subset_assignment`
- :doc:`/user-guide/simai-models/build-a-model`
- :meth:`TrainingData.assign_subset() <ansys.simai.core.data.training_data.TrainingData.assign_subset>`
- :class:`~ansys.simai.core.data.types.SubsetEnum`
