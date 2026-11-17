:description: Replace deprecated PySimAI features with their replacements, and check planned changes and removed features, with the versions that changed them.

.. _reference_deprecations:

.. _common_tasks_migrate_from_deprecated_features:

Migrate from deprecated features
================================

**Applies to:** SimAI models and GeomAI models

This page lists the deprecated features of PySimAI, what to use instead, and the version of
``ansys-simai-core`` that deprecated them, as stated in the changelog. It also lists the planned changes
and the removed features. Don't use deprecated features in new code.

When you use a deprecated feature, PySimAI emits a
:class:`~ansys.simai.core.errors.PySimAIDepreciationWarning` warning. A decommissioned feature raises a
:class:`~ansys.simai.core.errors.DeprecationError` exception.

Deprecated features
-------------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 15 15

   * - Deprecated element
     - Replacement
     - Applies to
     - Deprecated since
   * - ``build_on_top`` parameter and attribute of
       :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`
     - None. Build a new model with
       :meth:`~ansys.simai.core.data.models.ModelDirectory.build`.
     - SimAI models
     - 0.3.6
   * - ``boundary_conditions`` parameters of
       :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`,
       :class:`~ansys.simai.core.data.model_configuration.ModelInput`,
       :meth:`PredictionDirectory.run() <ansys.simai.core.data.predictions.PredictionDirectory.run>`,
       :meth:`Geometry.run_prediction() <ansys.simai.core.data.geometries.Geometry.run_prediction>`,
       :class:`~ansys.simai.core.data.selections.Point`,
       :meth:`Point.run_prediction() <ansys.simai.core.data.selections.Point.run_prediction>`,
       :class:`~ansys.simai.core.data.selections.Selection`, and the ``run_non_parametric()`` methods
       of optimizations
     - ``scalars`` parameter
     - SimAI models
     - 0.3.7
   * - ``boundary_conditions`` properties of
       :class:`~ansys.simai.core.data.predictions.Prediction`,
       :class:`~ansys.simai.core.data.predictions.PredictionDirectory`,
       :class:`~ansys.simai.core.data.workspaces.ModelManifest`,
       :class:`~ansys.simai.core.data.selections.Point`, and
       :class:`~ansys.simai.core.data.selections.Selection`
     - ``scalars`` property
     - SimAI models
     - 0.3.7
   * - ``BoundaryConditions`` type and the ``build_boundary_conditions()``,
       ``is_boundary_conditions()``, and ``are_boundary_conditions_equal()`` functions of
       ``ansys.simai.core.data.types``
     - ``Scalars`` type and the ``build_scalars()``, ``is_scalars()``, and ``are_scalars_equal()``
       functions
     - SimAI models
     - Not stated
   * - ``workspace.model`` property of :class:`~ansys.simai.core.data.workspaces.Workspace`
     - :attr:`workspace.model_manifest <ansys.simai.core.data.workspaces.Workspace.model_manifest>`
     - SimAI models
     - Not stated
   * - ``project.data`` property of :class:`~ansys.simai.core.data.projects.Project`
     - :meth:`project.list_training_data() <ansys.simai.core.data.projects.Project.list_training_data>`
     - SimAI models
     - Not stated
   * - ``data()`` and ``workspaces()`` methods of
       :class:`~ansys.simai.core.data.geomai.projects.GeomAIProject`
     - :meth:`~ansys.simai.core.data.geomai.projects.GeomAIProject.list_training_data` and
       :meth:`~ansys.simai.core.data.geomai.projects.GeomAIProject.list_workspaces`
     - GeomAI models
     - Not stated
   * - ``optimization_id`` parameter of
       :meth:`OptimizationDirectory.get() <ansys.simai.core.data.optimizations.OptimizationDirectory.get>`
       and :meth:`LegacyOptimizationDirectory.get() <ansys.simai.core.data.optimizations.LegacyOptimizationDirectory.get>`
     - ``id`` parameter
     - SimAI models
     - 0.4.6
   * - ``"csv"`` format of
       :meth:`ExportablePPList.export() <ansys.simai.core.data.lists.ExportablePPList.export>`
     - ``"csv.zip"`` format
     - SimAI models
     - Not stated
   * - :meth:`GeomAIWorkspace.download_latent_parameters_json() <ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace.download_latent_parameters_json>`.
       Decommissioned since 0.4.7: it raises a :class:`~ansys.simai.core.errors.DeprecationError` exception.
     - :meth:`~ansys.simai.core.data.geomai.workspaces.GeomAIWorkspace.get_latent_parameters`
     - GeomAI models
     - 0.4.4

Planned changes
---------------

The following features are still supported, but the code or the changelog announces a change or a removal
in a future release.

.. list-table::
   :header-rows: 1
   :widths: 35 35 15 15

   * - Element
     - Planned change
     - Applies to
     - Stated in
   * - :attr:`Optimization.optimization <ansys.simai.core.data.optimizations.Optimization.optimization>`
       property, :class:`~ansys.simai.core.data.optimizations.LegacyOptimization`, and
       :class:`~ansys.simai.core.data.optimizations.LegacyOptimizationDirectory`
     - Removal in a future release. No replacement is stated for the legacy classes.
     - SimAI models
     - 0.4.6
   * - :meth:`GeomAIPredictionDirectory.sample() <ansys.simai.core.data.geomai.predictions.GeomAIPredictionDirectory.sample>`
     - Beta feature, likely to be recast or retired by December 2026. Don't use it in a
       production workflow.
     - GeomAI models
     - 0.4.9

.. TODO: confirm the removal date of sample() with the product team.

Removed features
----------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 15 15

   * - Removed element
     - Replacement
     - Applies to
     - Removed in
   * - ``Optimization.run_parametric()`` method
     - :meth:`OptimizationDirectory.run_non_parametric() <ansys.simai.core.data.optimizations.OptimizationDirectory.run_non_parametric>`
     - SimAI models
     - 0.3.7
   * - ``margin`` field of
       :class:`~ansys.simai.core.data.geomai.predictions.GeomAIPredictionConfiguration`,
       deprecated in 0.3.6
     - None
     - GeomAI models
     - 0.3.10
