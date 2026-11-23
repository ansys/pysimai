:description: Download the Model Evaluation Report (MER) of a SimAI model as a PDF from its workspace with Workspace.download_model_evaluation_report.

.. _simai_models_evaluate_a_model:

Download the Model Evaluation Report of a SimAI model
=====================================================

**Applies to:** SimAI models

Download the Model Evaluation Report (MER) of a SimAI model as a PDF file with
:meth:`Workspace.download_model_evaluation_report() <ansys.simai.core.data.workspaces.Workspace.download_model_evaluation_report>`.
The report measures the errors of the SimAI model on the test subset.

Where the Model Evaluation Report is
------------------------------------

The last step of a model build, deploying the model, generates the Model Evaluation Report and
creates the workspace of the SimAI model. The report belongs to this workspace, so you download
it from a :class:`~ansys.simai.core.data.workspaces.Workspace` object.

To get the workspace:

- From the project, the workspace of the last model build:
  :meth:`Project.get_last_workspace() <ansys.simai.core.data.projects.Project.get_last_workspace>`.
  It returns ``None`` if the project has no workspace.
- From the project, all its workspaces:
  :meth:`Project.list_workspaces() <ansys.simai.core.data.projects.Project.list_workspaces>`.
- By name: ``simai_client.workspaces.get(name="<your_workspace_name>")``.

The Model Evaluation Report reports errors on the training data points of the test subset. To
choose these data points, see :doc:`/user-guide/simai-models/assign-subsets`.

Download the report to a file or to memory
------------------------------------------

The ``file`` parameter of ``download_model_evaluation_report()`` is a path or a binary
file object:

- With a path or a file object, the method writes the PDF there and returns ``None``.
- With no ``file``, the method returns a binary file object that holds the PDF in memory.

This script gets the last workspace of a project and saves its Model Evaluation Report to a file.

.. code-block:: python

   import ansys.simai.core as asc

   simai_client = asc.SimAIClient(organization="<your_organization>")
   project = simai_client.projects.get(name="<your_project_name>")

   workspace = project.get_last_workspace()
   if workspace is None:
       raise SystemExit("The project has no workspace: no model build has finished yet.")

   workspace.download_model_evaluation_report("model_evaluation_report.pdf")
   print(f"Model Evaluation Report of {workspace.name} saved to model_evaluation_report.pdf")

To hold the PDF in memory, call the method with no ``file``:

.. code-block:: python

   report = workspace.download_model_evaluation_report()
   pdf_bytes = report.read()

Download the data behind the report
-----------------------------------

:meth:`Workspace.download_mer_data() <ansys.simai.core.data.workspaces.Workspace.download_mer_data>`
downloads the names, subsets, and plotting data of the files used in the SimAI model and in the
Model Evaluation Report. It takes the same ``file`` parameter:

.. code-block:: python

   workspace.download_mer_data("<path_to_your_output_file>")

Expected result when you download the Model Evaluation Report of a SimAI model
------------------------------------------------------------------------------

The code in "Download the report to a file or to memory" saves the report to a file. It
writes ``model_evaluation_report.pdf`` in the current folder and prints:

.. code-block:: text

   Model Evaluation Report of <your_workspace_name> saved to model_evaluation_report.pdf

Errors when you download the Model Evaluation Report of a SimAI model
---------------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - No project or workspace has this name or ID.
     - Check the name, or list the workspaces with ``project.list_workspaces()``.

More about how to download the Model Evaluation Report of a SimAI model
-----------------------------------------------------------------------

- :doc:`/user-guide/simai-models/build-a-model`
- :doc:`/user-guide/simai-models/assign-subsets`
- :doc:`/user-guide/simai-models/run-predictions`
- :class:`~ansys.simai.core.data.workspaces.Workspace`
