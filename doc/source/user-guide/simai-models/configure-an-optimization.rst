:description: Choose the parameters of a non-parametric optimization of a SimAI model design: baseline geometry, offline token, bounding boxes, symmetries, scalars, number of iterations, objective, maximum displacement, detail level, and part morphing.

.. _configure_npo:

.. _simai_models_configure_an_optimization:

Configure a non-parametric optimization of a SimAI model design
===============================================================

**Applies to:** SimAI models

Choose the parameters of
:meth:`OptimizationDirectory.run_non_parametric() <ansys.simai.core.data.optimizations.OptimizationDirectory.run_non_parametric>`
so that the optimization gives physically realistic geometries with a meaningful gain. For how to
run the optimization and read its results, see :doc:`/user-guide/simai-models/optimize-a-design`.

Script to configure a non-parametric optimization of a SimAI model design
-------------------------------------------------------------------------


This script sets every parameter of a server-side non-parametric optimization. Replace the
values with ones that fit your geometry and your SimAI model.

.. code-block:: python

   import ansys.simai.core as asc
   from ansys.simai.core.data.optimizations import Optimization, OptimizationPartMorphingSchema
   from ansys.simai.core.errors import ProcessingError

   simai_client = asc.SimAIClient(organization="<your_organization>")
   workspace = simai_client.workspaces.get(name="<your_workspace_name>")

   # Choose the baseline geometry
   geometry = simai_client.geometries.get(name="<your_geometry_name>.vtp", workspace=workspace)

   # Provide an offline token
   offline_token = simai_client.me.generate_offline_token()

   optimization = simai_client.optimizations.run_non_parametric(
       geometry=geometry,
       offline_token=offline_token,
       # Define the bounding boxes
       bounding_boxes=[[0, 1, 0, 2, 0, 4], [10, 12, 10, 14, 10, 15]],
       # Set the maximum displacement
       max_displacement=[0.002, 0.001],
       # Set the symmetries
       symmetries=["X"],
       # Set the scalars
       scalars={"<your_scalar_name>": 10.5},
       # Set the number of iterations
       n_iters=5,
       # Set the objective
       minimize=["<your_global_coefficient_name>"],
       # Set the detail level
       detail_level=4,
       # Restrict the deformation to some parts
       part_morphing=OptimizationPartMorphingSchema(part_ids=[1, 2], continuity_constraint=0.8),
       # Show the progress
       show_progress=True,
   )

   try:
       if isinstance(optimization, Optimization):
           optimization.wait()
       print(f"Objectives: {optimization.list_objectives()}")
   except ProcessingError as error:
       print(f"Optimization failed: {error}")

Geometry to optimize
--------------------

The ``geometry`` and ``bounding_boxes`` parameters set the geometry that the optimization deforms
and the regions where the deformation can happen.

Choose the baseline geometry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The baseline geometry (``geometry`` parameter) is the foundation of the optimization. Choose a
geometry that's representative of your training data, so that the optimization produces relevant
results. It must be a geometry of the workspace that has been used to build the SimAI model.

The accepted geometry formats are ``vtp``, ``stl``, ``zip``, and ``cgns``.

If the optimization shows no improvement after several runs, try another geometry of the training
data as the baseline. Make sure the geometry is clean and of high quality: mesh errors can harm
the optimization.

Define the bounding boxes
~~~~~~~~~~~~~~~~~~~~~~~~~

Bounding boxes (``bounding_boxes`` parameter) define the regions where deformations can happen.
Each box is a list of six numbers, ``[xmin, xmax, ymin, ymax, zmin, zmax]``, in the coordinates
of the geometry, with each minimum less than its maximum. You can get them from any CAD tool, for
example Ansys SpaceClaim.

Start with boxes that cover the areas most likely to improve the performance. If the results
don't improve, make the boxes larger for more flexibility, or add boxes for finer control. Avoid
boxes that are too large: they can lead to unrealistic or unstable deformations that make no
physical sense.

Examples of bounding boxes:

.. list-table::

   * - .. image:: /_static/bounding_boxes_view_0.png
          :alt: Bounding boxes of Ansys SUV (front view)
     - .. image:: /_static/bounding_boxes_view_1.png
          :alt: Bounding boxes of Ansys SUV (back view)
   * - .. image:: /_static/bounding_boxes_view_3.png
          :alt: Bounding boxes of Ansys SUV (top view)
     - .. image:: /_static/bounding_boxes_view_2.png
          :alt: Bounding boxes of Ansys SUV (side view)

Deformation constraints
-----------------------

The ``max_displacement``, ``symmetries``, ``axial_symmetry``, ``detail_level``, and ``part_morphing``
parameters limit how far and how finely the optimization deforms the baseline geometry, and
which parts it deforms.

Set the maximum displacement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``max_displacement`` parameter limits the deformation in each bounding box. It's required for
a server-side optimization and optional for a legacy one. It's computed from the baseline
geometry and applies to the whole optimization.

Pass one value per bounding box, in the same order as the bounding boxes:

.. code-block:: python

   bounding_boxes = [[0, 1, 0, 2, 0, 4], [10, 12, 10, 14, 10, 15]]
   max_displacement = [0.002, 0.001]

The values use the unit of the geometry coordinates. For example, if the bounding box is 2 meters
long, give the maximum displacement in meters too.

A value that's too high leads to an error that gives the maximum possible value for the
optimization parameters. A value that's too low can restrict the optimization too much. As a
guideline, limit the displacement to a small percentage of the characteristic length of the
geometry in each bounding box, so that the optimized geometry stays physically realistic.

Set the symmetries
~~~~~~~~~~~~~~~~~~

Symmetry constraints reduce computational costs and keep the results physically consistent
when you want a symmetrical design. Symmetry is planar or axial, and the two parameters are
mutually exclusive:

- Planar symmetry (``symmetries`` parameter) mirrors the geometry across a plane normal to each
  given axis: ``"x"``, ``"y"``, or ``"z"``. Lowercase and uppercase both work. Use it for designs that
  are identical on both sides of a plane. For example, for a symmetry across the YZ plane, pass
  ``["X"]``. It applies to all the bounding boxes.
- Axial symmetry (``axial_symmetry`` parameter) makes the deformation equal around one axis:
  ``"x"``, ``"y"``, or ``"z"``. The center of each bounding box must be on this axis, and the
  mesh must be axially symmetrical in the bounding box. It applies to all the bounding boxes.

Set the detail level
~~~~~~~~~~~~~~~~~~~~

The ``detail_level`` parameter sets how much deformation can be applied to the geometry. It's an
integer from 1 to 10, and 5 when you don't set it:

- Low values give coarse deformations with only rough shape changes.
- High values allow fine details and subtle local adjustments.

For a given ``detail_level``, the deformation refinement is the same whatever the size of the
bounding box. With several bounding boxes, each box gets the same amount of deformation.

.. warning::

   The total number of points to deform can't be greater than 6x10⁷.

Depending on the baseline geometry and the bounding boxes, some values of ``detail_level``
can't be reached. In those cases, the error gives the accepted range:

- If the value is too low:

  .. code-block:: text

      InputValueError: The size of box 'box_id' is too small for the chosen detail level.
      The minimum detail level is 'min_detail_level'.

- If the value is too high:

  .. code-block:: text

      InputValueError: The number of points to be deformed in the geometry ('nb_point') and
      this detail level ('current_detail_level') might lead to Out of Memory. The maximum detail level is 'max_detail_level'.

Legacy optimization ignores ``detail_level`` and shows a warning.

Restrict the deformation to some parts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``part_morphing`` parameter restricts the deformation to some parts of the geometry. Pass an
:class:`~ansys.simai.core.data.optimizations.OptimizationPartMorphingSchema` object or a
dictionary with the same keys:

- ``part_ids``: the IDs of the parts to deform, as a list of integers. They must match a cell
  field of the baseline geometry named exactly ``PartId``.
- ``continuity_constraint``: how much the continuity at the interface between deformed and
  non-deformed parts is enforced, from 0 to 1 included. At 0, the continuity isn't constrained.
  At 1, the continuity enforcement is at its maximum.

.. code-block:: python

   from ansys.simai.core.data.optimizations import OptimizationPartMorphingSchema

   part_morphing = OptimizationPartMorphingSchema(part_ids=[1, 2], continuity_constraint=0.8)

.. note::

   A higher ``continuity_constraint`` reduces the overall deformation. To compensate, increase
   ``detail_level``.

.. warning::

   For a configuration of ``detail_level``, ``bounding_boxes``, and other parameters that passes
   validation, adding ``part_morphing`` can cause an out-of-memory error. If it happens, lower
   ``detail_level`` or simplify the bounding boxes.

Legacy optimization ignores ``part_morphing`` and shows a warning.

Objective, scalars, and number of iterations
--------------------------------------------

The ``minimize`` or ``maximize``, ``scalars``, and ``n_iters`` parameters set the global
coefficient to optimize, the scalars at which the optimization runs, and the number of iterations
after which it stops.

Set the objective
~~~~~~~~~~~~~~~~~

Set one objective: ``minimize`` or ``maximize``, each a list of one global coefficient name. The
two parameters are mutually exclusive. The global coefficient must exist in the model
configuration of the SimAI model and must be computed from surface fields. Choose the most
relevant performance indicator, for example a drag to minimize or a lift to maximize.

Set the scalars
~~~~~~~~~~~~~~~

The ``scalars`` parameter sets the scalars at which the optimization runs. They must be scalars
of the SimAI model of the workspace, listed in ``workspace.model_manifest.scalars``. Changing the
scalars often between runs makes the results inconsistent and less reliable. Change them only
when you need to.

Set the number of iterations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``n_iters`` parameter sets the number of iterations of one optimization run, and the number
of deformed geometries uploaded to the workspace. It must be a strictly positive integer.

Five iterations are usually enough for quick tests. If the convergence is slow or the optimum
stays unstable, use 100 iterations or more. Before you commit to long runs, check the convergence
trend to make sure the extra iterations are worth their computation time.

Execution of the optimization
-----------------------------

The ``offline_token`` parameter lets a server-side optimization authenticate on your behalf, and
the ``show_progress`` parameter sets whether a legacy optimization prints its progress.

Provide an offline token
~~~~~~~~~~~~~~~~~~~~~~~~

A server-side optimization uploads the geometry of the current step to your workspace at each
iteration. To authenticate on your behalf during this process, the server needs an offline token
(``offline_token`` parameter).

Generate the token with ``simai_client.me.generate_offline_token()``. This call needs a manual
action from you: a browser login prompt. The token expires, and you can generate as many tokens
as you need.

.. TODO: confirm the offline token lifetime with the product team.

.. code-block:: python

   offline_token = simai_client.me.generate_offline_token()

If you pass no ``offline_token`` and the client configuration defines none, a server-side
optimization raises :class:`~ansys.simai.core.errors.InvalidArguments`. A legacy optimization
doesn't use the token. For more information on tokens, see :ref:`current_user`.

Show the progress
~~~~~~~~~~~~~~~~~

The ``show_progress`` parameter prints a progress bar that updates at each iteration. Only legacy
optimization uses it. To follow a server-side optimization, use the ``wait()`` method of the
returned :class:`~ansys.simai.core.data.optimizations.Optimization` object.

Expected result when you configure a non-parametric optimization of a SimAI model design
----------------------------------------------------------------------------------------

The complete script prints the objective values of the iterations once the optimization ends.

Errors when you configure a non-parametric optimization of a SimAI model design
-------------------------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Exception
     - Cause
     - Fix
   * - :class:`~ansys.simai.core.errors.InvalidArguments`
     - The message names the invalid parameter: missing offline token or ``max_displacement``,
       ``max_displacement`` with a different number of items than ``bounding_boxes``, both
       ``symmetries`` and ``axial_symmetry``, both or neither of ``minimize`` and ``maximize``,
       a bounding box that isn't six numbers in increasing order, or ``n_iters`` that isn't a
       positive integer.
     - Fix the parameter named in the message.
   * - :class:`~ansys.simai.core.errors.ProcessingError`
     - The server-side optimization failed.
     - Read the message, change the parameters, or try another baseline geometry.

More about how to configure a non-parametric optimization of a SimAI model design
---------------------------------------------------------------------------------

- :doc:`/user-guide/simai-models/optimization-overview`
- :doc:`/user-guide/simai-models/optimize-a-design`
- :ref:`ref_non_parametric_optimization`
- :meth:`OptimizationDirectory.run_non_parametric() <ansys.simai.core.data.optimizations.OptimizationDirectory.run_non_parametric>`
- :class:`~ansys.simai.core.data.optimizations.OptimizationPartMorphingSchema`
