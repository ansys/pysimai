Changelog
---------

0.3.3 (2025-07-02)
******************

Fixes:

- Replace `verify_gc_formula` with `process_gc_formula`.

0.3.2 (2025-07-02)
******************

Changes:

- General GeomAI improvements, including docs

0.3.1 (2025-06-24)
******************

New:

- Add ``max_displacement`` parameter to non-parametric optimization

Changes:

- Add checks on build on top
- Boundary conditions are optional on optimization runs
- Use new way to process global coefficients formula that uses a cache
- Improved checks for parametric and non parametric optimizations
- Switch to uv
- Docs improvements

0.3.0 (2025-05-14)
******************

New:

- Retry sending requests on HTTP 5xx error (#135)

Changes:

- Include python version in user_agent (#143)
- SSE: Don't expect record from jobs with pending status (#141)

0.2.7 (2025-03-26)
******************

New:

- Add :py:meth:`TrainingDataDirectory.iter<ansys.simai.core.data.training_data.TrainingDataDirectory.iter>` as a more efficient alternative to listing training data.

Fixes:

- Stop using deprecated endpoints
- Deleting PointCloud now cleanses the CustomVolumePointCloud post-processing cache

0.2.6 (2025-01-23)
******************

New:

- Add options for using custom TLS CA bundles in :py:class:`ClientConfig<ansys.simai.core.utils.configuration.ClientConfig>`
- Check if :py:class:`Project<ansys.simai.core.data.projects.Project>` is trainable before build
- Reintroduce surface evolution post-processing as :py:class:`SurfaceEvolution<ansys.simai.core.data.post_processings.SurfaceEvolution>`
- Raise an error when a variable is not found in the reference sample
- Support post processing predict as learnt and predict on cells for surface variables by introducing :py:class:`SurfaceVTPTDLocation<ansys.simai.core.data.post_processings.SurfaceVTPTDLocation>`, together with the methods :py:meth:`PredictionPostProcessings.surface_vtp_td_location()<ansys.simai.core.data.post_processings.PredictionPostProcessings.surface_vtp_td_location>` and :py:meth:`SelectionPostProcessingsMethods.surface_vtp_td_location()<ansys.simai.core.data.selection_post_processings.SelectionPostProcessingsMethods.surface_vtp_td_location>`

Changes:

- Remove `ModelManifest.version` property from :py:class:`ModelManifest<ansys.simai.core.data.workspaces.ModelManifest>`

Fixes:

- Type hints on ``SimAIClient`` off by one
- Fix pysimai version check

0.2.5 (2024-11-05)
******************

New:

- Allow users to cancel build with :py:meth:`Project.cancel_build()<ansys.simai.core.data.projects.Project.cancel_build>`
- Filter training data in :py:meth:`simai.training_data.list()<ansys.simai.core.data.training_data.TrainingDataDirectory.list>`
- Added experimental :py:meth:`Optimization.run_non_parametric()<ansys.simai.core.data.optimizations.OptimizationDirectory.run_non_parametric>`
- Added an example section to the documentation

Changes:

- `Optimization.run()` is now :py:meth:`Optimization.run()<ansys.simai.core.data.optimizations.OptimizationDirectory.run_parametric>` and checks that the generation function has a suitable signature
- Remove deprecated design of experiments feature
- Resolution steps are now printed upon error if any

Fixes:

- Correct payload for surface post-processing inputs on model build

0.2.4 (2024-09-23)
******************

New:

- Auth tokens are now cached in file system and get re-authenticated in a parallel fashion.
- Invalid refresh token now triggers a reauth instead of crashing.
- `build_preset` option in :py:class:`ModelConfiguration<ansys.simai.core.data.model_configuration.ModelConfiguration>` can now be one of `debug`, `1_day`, `2_days`, `7_days`.
- Model Evaluation Report data (csv file) can now be downloaded with :py:meth:`download_mer_data<ansys.simai.core.data.workspaces.Workspace.download_mer_data>`.
- Typing improvements; introducing `JSON` type is introduced and `APIResponse` type is updated to include `JSON` type.
- New property :py:meth:`Prediction.raw_confidence_score<ansys.simai.core.data.predictions.Prediction.raw_confidence_score>` is added to :py:class:`Prediction<ansys.simai.core.data.predictions.Prediction>`, which returns the raw confidence score.

Fix:

- Fixed the error where :py:meth:`data<ansys.simai.core.data.post_processings.GlobalCoefficients.data>` was not in coordinance with the BE response. :py:meth:`data<ansys.simai.core.data.post_processings.GlobalCoefficients.data>` now runs without errors.

0.2.3 (2024-08-21)
******************

New:

- Added :py:class:`PostProcessInput<ansys.simai.core.data.model_configuration.PostProcessInput>` class to define post processing input fields.
- Added support for NaN and Inf for Global Coefficients and Post Processings.

Fixes:

- Removed compute argument from :py:meth:`TrainingData.upload_folder()<ansys.simai.core.data.training_data.TrainingData.upload_folder>`
- Fixed Model Configuration to raise a ProcessingError when volume field is missing from a sample specifying volume output.
- Removed wakepy error mode success (deprecated) during optimization.
- Renamed TrainingData method compute() to :py:meth:`TrainingData.extract_data()<ansys.simai.core.data.training_data.TrainingData.extract_data>`.
- Updated documentation of :py:meth:`GeometryDirectory.upload()<ansys.simai.core.data.geometries.GeometryDirectory.upload>`: the ``workspace_id`` argument was moved to ``workspace`` but never updated.

0.2.2 (2024-07-17)
******************

New:

- Added support for the postprocessing of custom volume of point cloud. Use :py:meth:`Geometry.upload_point_cloud<ansys.simai.core.data.geometries.Geometry.upload_point_cloud>` to upload a point cloud file on a geometry and run the post processing through :py:meth:`Prediction.post.custom_volume_point_cloud<ansys.simai.core.data.post_processings.PredictionPostProcessings.custom_volume_point_cloud>` to run the postprocessing.

Fix:

- Remove internal uses of deprecated `workspace.model`

0.2.1 (2024-06-28)
******************

Fixes:

- Fixed bug that was crashing method :py:meth:`ModelConfiguration.compute_global_coefficient()<ansys.simai.core.data.model_configuration.ModelConfiguration.compute_global_coefficient>`. The result of the Global Coefficient formula can now be retrieved.

0.2.0 (2024-06-28)
******************

New:

- Model configuration can now be created from scratch and be used in training requests.
- Training-data subsets can now be assigned to `None`. Options `Ignored` and `Validation` are retired.

Fixes:

- Fixed bug when uploading large files. Large files can now be uploaded.
- Fixed bug when listing prediction without current_workspace being set.

0.1.7 (2024-04-30)
******************

New:

- Added :py:class:`DomainOfAnalysis<ansys.simai.core.data.model_configuration.DomainOfAnalysis>` class to
  help set the domain of analysis on a new model.
- Add `workspace` option where we previously relied only on the global workspace
- Add prediction.post.list()

Fixes:

- Reestablish python 3.9 compatibility.
- Bump wakepy lib to fix errors when not able to prevent sleep during optimization.

0.1.6 (2024-04-25)
******************

New:

- Added new method :py:meth:`TrainingData.assign_subset()<ansys.simai.core.data.training_data.TrainingData.assign_subset>` that allows you to assign a Train, Validation, or Test subset to your data.


Fixes:

- The method `Optimization.run()<ansys.simai.core.data.optimizations.OptimizationDirectory.run>` now raises an exception if no workspace is provided and none is configured.
- Fix RecursionError on authentication refresh

0.1.5 (2024-04-15)
******************

- Training can now be launched using the most recent model configuration from a project.
- Enabled non-interactive mode capability, allowing for automation or operations without manual inputs.
- Added new validation :py:meth:`Project.is_trainable()<ansys.simai.core.data.projects.Project.is_trainable>` to verify if the project meets all minimum requirements for training.
- Added new method :py:meth:`Project.get_variables()<ansys.simai.core.data.projects.Project.get_variables>` to get all available variables used for a model's inputs and outputs.
- Fixed bug where a subset of training data could not be pulled. A subset of training data is now correctly retrieved.
- Fixed erroneous call to a private function during the optimization run.

0.1.4 (2024-02-26)
******************

- Less verbose sse disconnects
- Fix client config vars being described two times
- Fix type/KeyError in workspace.model.post_processings
- Fix monitor_callback interface not respected in upload_file_with_presigned_post
- Fix README indentation

0.1.3 (2024-02-02)
******************

Fix config args not taken into account if a config file is not found

0.1.2 (2024-01-24)
******************

Fix training data upload_folder method

0.1.1 (2024-01-19)
******************

Fix badges

0.1.0 (2024-01-19)
******************

Initial release
