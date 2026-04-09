.. _configure_automorphing:

How to configure the non-parametric optimization
==================================================

Learn about the parameters to set when configuring the non-parametric optimization.
For more information about using those parameters, see :ref:`optimizations`.

Baseline geometry (geometry)
----------------------------

The baseline geometry should be chosen carefully, as it forms the foundation for the optimization process.
It is recommended to select a geometry that is representative of your dataset to ensure that the optimization produces relevant results.

The supported input formats are ``vtp``, ``stl``, ``zip`` and ``cgns``.

If the optimization does not show improvement after several optimization processes,
try using a different geometry from the training data as the baseline (``geometry``).
Always make sure the geometry is clean and of high quality, as issues like mesh errors can negatively impact the optimization process.

Offline token (offline_token)
-----------------------------

The optimization runs server-side. At each iteration, the geometry corresponding to the
current step is uploaded to your workspace. To allow the server to authenticate on your
behalf during this process, you must provide an ``offline_token``.

Generating the token requires a one-time manual action (a browser login prompt).
Once generated, the token is valid for **30 days**. You can generate as many tokens as needed.

.. code-block:: Python

    offline_token = simai_client.me.generate_offline_token()

If no ``offline_token`` is passed as a function parameter or defined in the client configuration,
server-side optimization will not work.

.. note::

    For more information on managing tokens, see :ref:`current_user`.

Bounding boxes
---------------

Bounding boxes can be obtained from any CAD tool (for example, Ansys SpaceClaim).
Bounding boxes define the regions where deformations can occur during optimization.

A good starting point is to use the bounding boxes that cover the areas most likely to influence performance improvements.
If the optimization results do not improve, you can increase the size of the boxes to allow more flexibility or add additional boxes for finer control.
However, avoid using excessively large boxes, as they can lead to unrealistic or unstable deformations that do not make sense physically.

Examples of bounding boxes:

+----------------------------------------------------------------+----------------------------------------------------------------+
| .. image:: ../../../source/_static/bounding_boxes_view_0.png   | .. image:: ../../../source/_static/bounding_boxes_view_1.png   |
|   :alt: Bounding boxes of Ansys SUV (front view)               |   :alt: Bounding boxes of Ansys SUV (back view)                |
+----------------------------------------------------------------+----------------------------------------------------------------+
| .. image:: ../../../source/_static/bounding_boxes_view_3.png   | .. image:: ../../../source/_static/bounding_boxes_view_2.png   |
|   :alt: Bounding boxes of Ansys SUV (top view)                 |   :alt: Bounding boxes of Ansys SUV (side view)                |
+----------------------------------------------------------------+----------------------------------------------------------------+

Symmetries
-----------

Symmetry constraints help reduce computational costs and ensure physically consistent results if you are looking for symmetrical optimizations.

Symmetry can be planar or axial:

- Planar symmetry (``symmetries`` parameter)
  ensures that the geometry is mirrored across a plane normal to the given direction,
  which is useful for designs that are identical on both sides of a plane. For example,
  if the design has a planar symmetry based on the "YZ" plane, then "X" is the parameter to specify.

- Axial symmetry (``axial_symmetry`` parameter)
  should be chosen when the deformation needs to be equal around a specific axis,
  resulting in rotational symmetry.

Scalars
--------------------

The values of the scalars should remain consistent with those defined in your model configuration,
so the ``scalars`` parameter must correspond to the ones defined in the SimAI workspace.
Frequent changes to scalars can create inconsistencies and reduce the reliability of optimization results.
Make adjustments only when necessary to maintain a stable and physically realistic simulation environment.

Number of iterations (n_iters)
------------------------------

The number of iterations determines how many rounds of improvement will be executed in one optimization process.
For quick tests, 5 iterations are usually sufficient.
If convergence is slow or the optimum remains unstable, consider increasing the number of iterations to 100 or more.
Before committing to long runs, you should monitor the convergence trend to ensure additional iterations will provide value rather than waste computation time.

Objective: Minimize or Maximize
--------------------------------

When defining an objective, focus on the most relevant performance indicator, for example, minimizing drag or maximizing lift.
For non-parametric optimization, only one objective can be defined.

Maximum displacement
---------------------

The ``max_displacement`` parameter is optional. It controls the allowable deformation for each bounding box.
It is calculated from the baseline geometry and applied to the entire optimization.

If you want to use the ``max_displacement`` parameter, you must set one per bounding box defined.
If you want to use a different maximum displacement parameter for each box, you must list them in the same order as the bounding boxes.
For example, for two bounding boxes:

.. code-block:: Python


    bounding_boxes = [[0,1,0,2,0,4],[10,2,10,4,10,5]]
    max_displacement = [0.002, 0.001]


Its unit must correspond to the geometry coordinates unit.
For example, if the bounding box is 2 meters long, the maximum displacement should be specified in meters as well.

Setting this value too high leads to an error that returns the maximum possible value based on the optimization parameters,
while values that are too low may overly restrict the optimization.

A practical guideline is to limit displacement to a small percentage of the geometry's characteristic length for each bounding box.
This ensures that the optimized geometry remains physically realistic while still allowing meaningful shape changes.

Show progress
--------------

The ``show_progress`` parameter determines whether progress updates are displayed during the optimization run.
It is generally recommended to enable this feature during development and testing phases
so that you can monitor the process and detect potential issues early.

Detail level (detail_level)
----------------------------

The ``detail_level`` parameter adjusts how much deformation can be applied to the geometry.
It is an integer from 1 to 10 and defaults to **5** when not provided.

- **Low values** produce coarse deformations with only rough shape changes.
- **High values** allow fine details and subtle local adjustments.

For a given value of ``detail_level``, the deformation refinement remains the same regardless of
the bounding box size. When using multiple bounding boxes, this ensures the same amount of
deformation in each box.

.. code-block:: Python

    detail_level = 4

.. warning::

    The total number of points to be deformed cannot be greater than **6x10⁷**.

Depending on the baseline geometry and bounding boxes, some values of ``detail_level`` may not be achievable.
In those cases, errors are raised indicating the acceptable range:

- If the value is too low:

  .. code-block:: text

      InputValueError: The size of box 'i' is too small for the chosen detail level.
      The minimum detail level is 'n'.

- If the value is too high:

  .. code-block:: text

      InputValueError: The number of points to be deformed in the geometry ('nb_point') and
      this detail level ('m') might lead to OOM. The maximum detail level is 'n'.

Part morphing (part_morphing)
------------------------------

The ``part_morphing`` parameter provides user-defined constraints to restrict deformation to
specific parts of the geometry.

The parts to be deformed are identified by their IDs, provided as a list of integers in
``part_ids``. These IDs must correspond to a cell field of the baseline geometry
exactly named ``PartId``.

The ``continuity_constraint`` parameter controls how much the continuity at the interface
between deformed and non-deformed parts is enforced. It can be set between **0** and **1** (inclusive):

- At **0**, the continuity is not constrained at all during the optimization.
- At **1**, the continuity enforcement is at its maximum.

.. note::

    Increasing ``continuity_constraint`` reduces the overall deformation magnitude.
    To compensate, you can increase the ``detail_level`` value.

.. code-block:: Python

    from ansys.simai.core.data.optimizations import OptimizationPartMorphingSchema

    part_morphing = OptimizationPartMorphingSchema(
        part_ids=[1, 2],
        continuity_constraint=0.8
    )

.. warning::

    For a given configuration of ``detail_level``, ``bounding_boxes``, and other parameters that
    passes validation, adding ``part_morphing`` may trigger an out-of-memory error. If this occurs,
    reduce the ``detail_level`` or simplify the bounding box configuration.
