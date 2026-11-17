:description: Define the model configuration of a SimAI model in PySimAI (model inputs, model outputs, global coefficients, Domain of Analysis, and build setting), check global coefficient formulas, and reuse the last model configuration.

.. _simai_models_configure_a_model:

Configure a SimAI model
=======================

**Applies to:** SimAI models

Define what a SimAI model learns and how it's built with a
:class:`~ansys.simai.core.data.model_configuration.ModelConfiguration` object: its model inputs
(:class:`~ansys.simai.core.data.model_configuration.ModelInput`), model outputs
(:class:`~ansys.simai.core.data.model_configuration.ModelOutput`), global coefficients, Domain of
Analysis (:class:`~ansys.simai.core.data.model_configuration.DomainOfAnalysis`), and build setting.

Script to configure a SimAI model
---------------------------------

This script lists the variables of the reference sample, checks a global coefficient formula, and
creates a model configuration for a production build of up to 24 hours. Replace the variable
names and the Domain of Analysis values with the ones of your training data.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.model_configuration import (
       DomainOfAnalysis,
       GlobalCoefficientDefinition,
       ModelConfiguration,
       ModelInput,
       ModelOutput,
   )

   simai_client = asc.SimAIClient(organization="<your_organization>")
   project = simai_client.projects.get(name="<your_project_name>")

   # Choose the model inputs and model outputs
   # Variables available in the reference sample of the project
   print(project.get_variables())

   model_input = ModelInput(surface=["<your_surface_input_variable>"], scalars=["<your_scalar_name>"])
   # Remove the volume variables if your training data has no volume file
   model_output = ModelOutput(
       surface=["<your_surface_output_variable>"],
       volume=["<your_volume_output_variable>"],
   )

   # Check a global coefficient formula
   # Check the formula on the reference sample before you add it to the configuration
   value = project.process_gc_formula(
       "max(<your_surface_output_variable>)",
       bc=["<your_scalar_name>"],
       surface_variables=["<your_surface_output_variable>"],
       gc_location="cells",
   )
   print(f"Value on the reference sample: {value}")

   # Define the global coefficients
   global_coefficients = [
       GlobalCoefficientDefinition(
           formula="max(<your_surface_output_variable>)",
           name="<your_global_coefficient_name>",
           gc_location="cells",
       )
   ]

   # Set the Domain of Analysis
   doa = DomainOfAnalysis(
       length=("relative_to_min", 0.102, 1.219),
       width=("relative_to_min", 0.102, 1.219),
       height=("relative_to_min", 0.134, 1.61),
   )

   model_configuration = ModelConfiguration(
       project=project,
       # Choose the build setting
       build_preset="1_day",
       input=model_input,
       output=model_output,
       global_coefficients=global_coefficients,
       domain_of_analysis=doa,
   )
   print(model_configuration.build_preset)

Choose the model inputs and model outputs
-----------------------------------------

The variables of a SimAI model come from the reference sample of the project, which is the
training data point stored in ``project.sample``. List them with
:meth:`Project.get_variables() <ansys.simai.core.data.projects.Project.get_variables>`.

- :class:`~ansys.simai.core.data.model_configuration.ModelInput` takes the ``surface`` variables
  and the ``scalars`` that the SimAI model uses to predict its outputs. A model input must exist in
  every training data point and in every geometry you predict on.
- :class:`~ansys.simai.core.data.model_configuration.ModelOutput` takes the ``surface`` and
  ``volume`` variables, and the ``scalars``, that the SimAI model learns to predict. Volume
  variables need a volume file in the training data.
- :class:`~ansys.simai.core.data.model_configuration.PostProcessInput` takes the ``surface``
  variables that the SimAI model doesn't learn but that you need for global coefficients. Pass it
  with the ``pp_input`` parameter of ``ModelConfiguration``.

.. code-block:: python

   from ansys.simai.core.data.model_configuration import PostProcessInput

   pp_input = PostProcessInput(surface=["<your_postprocessing_input_variable>"])

``ModelConfiguration`` checks the variables against the reference sample when you create it, and
raises :class:`~ansys.simai.core.errors.ProcessingError` if a variable doesn't exist there.

Define the global coefficients
------------------------------

A global coefficient is a single value computed for a whole design after a prediction, such as a
drag or a lift, from a formula. Define each one with a
:class:`~ansys.simai.core.data.model_configuration.GlobalCoefficientDefinition` object:

- ``formula``: the formula, for example ``"integral(Pressure)"`` or ``"max(Pressure)"``.
- ``name``: the name of the global coefficient. It can't be the name of an output scalar.
- ``gc_location``: ``"cells"`` (default) or ``"points"``.

You can also pass a ``(formula, name)`` tuple, such as ``("max(Pressure)", "maxpress")``.
``ModelConfiguration`` computes each formula on the reference sample when you set the global
coefficients, so a project must be set first.

Check a global coefficient formula
----------------------------------

To test a formula before you put it in a model configuration, call
:meth:`Project.process_gc_formula() <ansys.simai.core.data.projects.Project.process_gc_formula>`.
The method checks and computes the formula on the reference sample, waits for the result, and
returns it as a float:

.. code-block:: python

   value = project.process_gc_formula(
       "integral(Pressure)",
       bc=["<your_scalar_name>"],
       surface_variables=["Pressure"],
       gc_location="points",
   )

- ``bc``: the names of the scalars that the formula can use.
- ``surface_variables``: the surface variables that the formula can use, in addition to
  ``Area``, ``Normals``, and ``Centroids``.
- ``gc_location``: ``"cells"`` (default) or ``"points"``.

The method raises :class:`~ansys.simai.core.errors.ProcessingError` if the project has no
reference sample or if the formula fails.

Set the Domain of Analysis
--------------------------

The Domain of Analysis (DoA) is the box that must enclose all designs: the training data and the
geometries you predict on. A smaller domain gives better accuracy. Set one axis definition for
each of ``length`` (X axis), ``width`` (Y axis), and ``height`` (Z axis), as a
``(position, value, length)`` tuple or a
:class:`~ansys.simai.core.data.model_configuration.DomainAxisDefinition` object:

- ``position``: ``"relative_to_min"``, ``"relative_to_max"``, ``"relative_to_center"``, or
  ``"absolute"``.
- ``value``: the distance of the anchor from the position. It must be positive unless the
  position is ``"absolute"``.
- ``length``: the length of the domain along the axis. It must be positive.

All three axes must be set before a model build.

Choose the build setting
------------------------

The ``build_preset`` parameter sets the build setting and, for production mode, the build duration:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - ``build_preset``
     - Build
   * - ``"debug"``
     - Debug mode: less than 30 minutes, four training data points only. Checks that the model
       configuration works. Don't use the SimAI model for production purposes.
   * - ``"1_day"``
     - Production mode, up to 24 hours of training (100,000 iterations).
   * - ``"2_days"``
     - Production mode, up to 48 hours of training (200,000 iterations). The default build
       duration of production mode.
   * - ``"7_days"``
     - Production mode, up to 7 days of training (400,000 iterations).

Always set ``build_preset`` explicitly: when you omit it, the ``ModelConfiguration`` constructor
uses ``"debug"``. Each iteration processes one training data point, so a build shouldn't have
more training data points than iterations. For more information, see
:doc:`/user-guide/simai-models/build-a-model`.

Reuse the configuration of the last model build
-----------------------------------------------

The :attr:`Project.last_model_configuration <ansys.simai.core.data.projects.Project.last_model_configuration>`
property returns the model configuration of the last model build of a project, or ``None`` if the
project has no build yet. Rebuilding from this configuration works for models created after v0.1.5
(April 15, 2024). Change what you need, then build again:

.. code-block:: python

   model_configuration = project.last_model_configuration
   model_configuration.build_preset = "2_days"

To use it in another project, set its ``project`` attribute:

.. code-block:: python

   model_configuration.project = simai_client.projects.get(name="<your_other_project_name>")

Expected result when you configure a SimAI model
------------------------------------------------

The complete script prints the variables of the reference sample, the value of the global
coefficient on the reference sample, and the build preset: ``1_day``.

Errors when you configure a SimAI model
---------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - A variable doesn't exist in the reference sample, a global coefficient has the name of an
       output scalar, a formula fails, or the project has no reference sample.
     - Check the names with ``project.get_variables()`` and the formula with
       ``project.process_gc_formula()``.
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - ``build_preset`` isn't one of ``debug``, ``1_day``, ``2_days``, ``7_days``, a Domain of
       Analysis value or length is out of range, or, when the model build starts, a Domain of
       Analysis axis is missing.
     - Use an accepted value and set the three axes.

More about how to configure a SimAI model
-----------------------------------------

- :doc:`/user-guide/simai-models/build-a-model`
- :ref:`ref_basic_build_model`
- :ref:`ref_model_configuration_reuse`
- :class:`~ansys.simai.core.data.model_configuration.ModelConfiguration`
- :meth:`Project.process_gc_formula() <ansys.simai.core.data.projects.Project.process_gc_formula>`
