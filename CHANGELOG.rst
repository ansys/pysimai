Changelog
---------

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
