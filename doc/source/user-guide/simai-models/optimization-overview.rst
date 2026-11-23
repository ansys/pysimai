:description: Understand non-parametric optimization in PySimAI, which deforms a baseline geometry to improve a global coefficient predicted by a SimAI model, and its iterative workflow.

.. _ref_npo_guide:

.. _simai_models_optimization_overview:

Non-parametric optimization of a SimAI model design
===================================================

**Applies to:** SimAI models

Non-parametric optimization improves the performance of a baseline geometry by applying smooth,
data-driven deformations to its surface, based on sensitivity maps predicted by a SimAI model.
In PySimAI, you run it with
:meth:`OptimizationDirectory.run_non_parametric() <ansys.simai.core.data.optimizations.OptimizationDirectory.run_non_parametric>`.
This feature is available through PySimAI only.

When to use non-parametric optimization
---------------------------------------

Use non-parametric optimization when your designs have no predefined design parameters, and
defining them afterward would be too difficult. The optimization deforms the baseline geometry
directly with smooth and continuous deformations. You explore the design space and change the
shape based on one objective, without generating new geometries or reparametrizing existing
designs.

The objective is one global coefficient of the SimAI model to minimize or maximize, such as a
drag or a lift.

Server-side and legacy optimization
-----------------------------------

``run_non_parametric()`` runs the optimization loop on the server when the SimAI model of the
workspace supports it. Otherwise, it falls back to a legacy loop that runs on the client:

- A server-side optimization returns an
  :class:`~ansys.simai.core.data.optimizations.Optimization` object right away. Call its
  ``wait()`` method to block until it ends. It needs an offline token and a maximum displacement.
- A legacy optimization returns a
  :class:`~ansys.simai.core.data.optimizations.LegacyOptimizationResult` object when it has
  already finished. This object has no ``wait()`` method. Legacy optimization ignores the
  ``detail_level`` and ``part_morphing`` parameters.

For both, ``list_geometries()`` and ``list_objectives()`` return the results. For a complete
script, see :doc:`/user-guide/simai-models/optimize-a-design`.

Prepare the training data for optimization
------------------------------------------

The training data limits the gain that the optimization can find. Make sure the maximum
difference of the objective within the training data is around the minimum optimization gain
you want. For example, for a drag reduction of at least 4%, the training data needs a difference
of around 4% in drag between the best and the worst designs.

Workflow of a non-parametric optimization
-----------------------------------------

.. image:: /_static/optimization_workflow_v2.png
    :align: center
    :alt: Workflow of a non-parametric optimization: upload data, train the SimAI model, optimize, verify with a solver, and enrich the training data

#. Upload the training data. Select the surface geometries to optimize, based on the preceding
   requirement, and prepare their files. For more information, see
   :doc:`/user-guide/simai-models/prepare-training-data` and the `Ansys SimAI User's Guide`_. Upload them with
   :doc:`/user-guide/simai-models/upload-training-data`.
#. Train the SimAI model. Add the training data to a project and build a SimAI model. The
   model build creates a workspace. For more information, see
   :doc:`/user-guide/simai-models/build-a-model`.
#. Optimize. Run ``run_non_parametric()`` on a baseline geometry of the workspace. At each
   iteration, the optimization uploads a deformed geometry to the workspace: ``n_iters`` sets
   their number. Run predictions and postprocessings on them if needed.
#. Verify the results with your solver. Download a selection of the geometries produced across the
   iterations, and run a simulation in your solver on each of them to find the best one.
#. Enrich the training data. Add the best geometries, with their simulation results, as new
   training data. Build a new SimAI model with them, then optimize again from step 3.

Repeat steps 3 to 5 at least three times, which is usually the number needed to get good results.
Stop when the performance verified in step 4 is satisfactory. Each loop lets the SimAI model learn
from its previous predictions.

.. _Ansys SimAI User's Guide: https://ansyshelp.ansys.com/public/account/secured?returnURL=%2Fpublic%2FViews%2FSecured%2FSimAI%2Fv000%2Fen%2FSimAI_ug%2Findex.html

More about how to non-parametric optimization of a SimAI model design
---------------------------------------------------------------------

- :doc:`/user-guide/simai-models/optimize-a-design`
- :doc:`/user-guide/simai-models/configure-an-optimization`
- :ref:`ref_non_parametric_optimization`
- :class:`~ansys.simai.core.data.optimizations.OptimizationDirectory`

.. toctree::
   :maxdepth: 2

   optimize-a-design
   configure-an-optimization
