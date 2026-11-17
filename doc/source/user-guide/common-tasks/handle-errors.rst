:description: Catch and fix the exceptions raised by PySimAI (ProcessingError, NotFoundError, InvalidArguments, ConfigurationError and the others): when each one is raised, its cause, and its fix.

.. _common_tasks_handle_errors:

Handle PySimAI errors
=====================

**Applies to:** SimAI models and GeomAI models

PySimAI raises the exceptions of the :mod:`ansys.simai.core.errors` module. This page lists when
each exception is raised, its cause, and its fix, and shows how to catch them.

Import the exceptions
---------------------

Import the module and prefix each exception with ``errors.``:

.. code-block:: python

    from ansys.simai.core import errors

The module defines its own ``ConnectionError``, which hides the Python built-in exception of the
same name if you import it directly. Writing ``errors.ConnectionError`` avoids the confusion.

Catch the exceptions in the right order
---------------------------------------

All PySimAI exceptions derive from :class:`~ansys.simai.core.errors.SimAIError`. Catch
``SimAIError`` to catch any error that PySimAI expects. Some exceptions derive from others, so
catch the most specific ones first:

.. code-block:: text

   SimAIError
   ├── ApiClientError (also httpx.HTTPError)
   │   └── NotFoundError
   ├── ConnectionError (also httpx.RequestError)
   ├── ConfigurationError
   │   ├── ConfigurationNotFoundError
   │   └── InvalidConfigurationError (also ValueError)
   ├── ProcessingError
   ├── InvalidArguments (also ValueError)
   ├── InvalidClientStateError
   ├── InvalidServerStateError
   ├── InvalidOperationError
   ├── MultipleErrors
   └── DeprecationError

This example catches the most specific exceptions first and ``SimAIError`` last:

.. code-block:: python

    import ansys.simai.core as asc
    from ansys.simai.core import errors

    try:
        simai_client = asc.SimAIClient(organization="<your_organization>")
    except errors.ConfigurationError as error:
        raise SystemExit(f"Invalid client configuration: {error}")

    try:
        workspace = simai_client.workspaces.get(name="<your_workspace_name>")
        geometry = simai_client.geometries.upload(
            "<path/to/your/geometry.vtp>", workspace=workspace
        )
        geometry.wait()
        prediction = geometry.run_prediction(scalars={"<your_scalar_name>": 10.0})
        prediction.wait()
        print(f"Prediction {prediction.id} is ready.")
    except errors.NotFoundError as error:
        print(f"Not found on the server: {error}")
    except errors.ProcessingError as error:
        print(f"The server failed to process the data: {error}")
    except errors.InvalidArguments as error:
        print(f"Invalid argument: {error}")
    except errors.ApiClientError as error:
        print(f"The API returned HTTP {error.status_code}: {error}")
    except errors.ConnectionError as error:
        print(f"Can't reach the Ansys SimAI server: {error}")
    except errors.SimAIError as error:
        print(f"PySimAI error: {error}")

Exceptions, causes, and fixes
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: 24 40 36

   * - Exception
     - When PySimAI raises it
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - ``wait()`` on an object whose computation failed: training data point, model build,
       geometry, prediction, or postprocessing. Also ``cancel_build()`` when no build is running,
       and :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration` when a variable
       doesn't exist in the reference sample or a global coefficient has the same name as a
       scalar.
     - Read ``failure_reason`` on the object. For a model configuration, use the names returned
       by ``project.get_variables()``.
   * - :class:`~ansys.simai.core.errors.NotFoundError`
     - The server returns HTTP 404, for example when ``get(name=...)`` or ``get(id=...)`` finds
       no project, training data point, geometry, or prediction with this name or ID.
     - Check the name or ID. List the existing objects with ``list()``.
   * - :class:`~ansys.simai.core.errors.ApiClientError`
     - The server returns another HTTP error (4xx or 5xx). For example, removing the reference
       sample from its project, or removing training data from a project during a build. The
       ``status_code`` attribute gives the HTTP status.
     - Read the message: it contains the reason returned by the server.
   * - :class:`~ansys.simai.core.errors.ConnectionError`
     - The client can't communicate with the server, or can't connect to its event stream.
     - Check your network connection and proxy. See :doc:`/getting-started/work-behind-a-proxy`.
   * - :class:`~ansys.simai.core.errors.ConfigurationError`
     - The client can't be configured, for example with ``tls_ca_bundle="system"`` on Python
       earlier than 3.10.
     - Fix the configuration. Its subclasses give more details.
   * - :class:`~ansys.simai.core.errors.ConfigurationNotFoundError`
     - ``from_config()`` finds no configuration file at the given path or in the default
       locations.
     - Create the file, or pass its path. See :doc:`/getting-started/use-a-configuration-file`.
   * - :class:`~ansys.simai.core.errors.InvalidConfigurationError`
     - A client parameter is invalid; a required parameter is missing with
       ``interactive=False``; ``credentials``, ``offline_token``, and ``access_token`` are
       combined; the configuration file isn't valid TOML or has no section for the profile; or
       the project or workspace set in the configuration doesn't exist.
     - Fix the parameter as the message describes. See :doc:`/getting-started/configure-the-client`.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - A method receives invalid arguments. For example: ``get()`` with both a name and an ID or
       with neither; ``upload_folder()`` with a path that isn't a folder; a geometry file with an
       unsupported extension; ``models.build()`` on a project that isn't ready for a build; an
       invalid ``build_preset``; an incomplete Domain of Analysis; an invalid GeomAI model or
       prediction configuration.
     - Fix the argument as the message describes. For a build, the message gives the reason
       returned by ``project.is_trainable()``.
   * - :class:`~ansys.simai.core.errors.InvalidClientStateError`
     - You read ``current_workspace`` or ``current_project`` of the client before setting it.
     - Call ``set_current_workspace()`` or ``set_current_project()``, or pass the workspace or
       project to the method.
   * - :class:`~ansys.simai.core.errors.InvalidServerStateError`
     - The server returns several postprocessings where only one is expected.
     - Report the problem with the postprocessing IDs listed in the message.
   * - :class:`~ansys.simai.core.errors.InvalidOperationError`
     - The operation isn't possible in the current state, for example
       ``custom_volume_point_cloud()`` on a geometry with no point cloud, or
       ``delete_point_cloud()`` when there's no point cloud to delete.
     - Upload a point cloud first with ``geometry.upload_point_cloud()``.
   * - :class:`~ansys.simai.core.errors.MultipleErrors`
     - Several operations failed, for example during ``SimAIClient.wait()`` or when you wait for
       the predictions of a selection.
     - Read each error in the ``exceptions`` attribute.
   * - :class:`~ansys.simai.core.errors.DeprecationError`
     - You called a decommissioned method:
       ``GeomAIWorkspace.download_latent_parameters_json()``.
     - Use ``GeomAIWorkspace.get_latent_parameters()`` instead.

Handle failures of wait()
-------------------------

``wait()`` raises :class:`~ansys.simai.core.errors.ProcessingError` when a computation fails.
With a ``timeout``, it returns ``False`` when the timeout expires before the end of the
computation. Handle failures with ``try`` and ``except``, and use the return value only to know
whether the computation is finished:

.. code-block:: python

    import ansys.simai.core as asc
    from ansys.simai.core import errors

    simai_client = asc.SimAIClient(organization="<your_organization>")
    training_data = simai_client.training_data.get(name="<your_training_data_name>")

    try:
        if training_data.wait(timeout=300):
            print("The training data point is ready.")
        else:
            print("The extraction is still running after 5 minutes.")
    except errors.ProcessingError:
        print(f"The extraction failed: {training_data.failure_reason}")

For more information, see :doc:`/user-guide/common-tasks/work-asynchronously`.

Errors that aren't PySimAI exceptions
-------------------------------------

A few methods raise Python built-in exceptions:

- ``simai_client.workspaces.get()`` and ``simai_client.geomai.workspaces.get()`` raise
  ``ValueError`` when you pass both a name and an ID, or neither. ``InvalidArguments`` also
  derives from ``ValueError``, so ``except ValueError`` catches both.
- Authentication with tokens raises ``RuntimeError`` when the access token is invalid or
  expired, or when the offline token can't authenticate you. Get a new token.
- ``simai_client.models.get()`` and ``simai_client.geomai.models.get()`` aren't implemented
  and raise ``NotImplementedError``.

PySimAI also emits ``PySimAIDepreciationWarning``, a ``UserWarning``, when you pass a deprecated
parameter such as ``boundary_conditions``. Use ``scalars`` instead.

Expected result when you handle PySimAI errors
----------------------------------------------

The code in "Catch the exceptions in the right order" prints ``Prediction <id> is ready.``, or
one message that names the exception and its cause.

More about how to handle PySimAI errors
---------------------------------------

- :mod:`ansys.simai.core.errors`
- :doc:`/user-guide/common-tasks/work-asynchronously`
- :doc:`/getting-started/configure-the-client`
