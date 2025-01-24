# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import TYPE_CHECKING

from ansys.simai.core.data.lists import ExportablePPList, PPList
from ansys.simai.core.data.post_processings import (
    GlobalCoefficients,
    Slice,
    SurfaceEvolution,
    SurfaceVTP,
    SurfaceVTPTDLocation,
    VolumeVTU,
)

if TYPE_CHECKING:
    from ansys.simai.core.data.selections import Selection


class SelectionPostProcessingsMethods:
    """Acts as a namespace inside :py:class:`~ansys.simai.core.data.selections.Selection` objects,
    allowing you to access or run postprocessings on whole selections.
    """

    def __init__(self, selection: "Selection"):
        self._selection = selection

    def global_coefficients(self) -> ExportablePPList[GlobalCoefficients]:
        """Compute or get the global coefficients of the selected predictions.

        This is a non-blocking method. It returns an
        :py:class:`~ansys.simai.core.data.lists.ExportablePPList` instance
        of :py:class:`~ansys.simai.core.data.post_processings.GlobalCoefficients`
        objects without waiting. Those ``PostProcessing`` objects may not have
        data right away if the computation is still in progress. Data is filled
        asynchronously once the computation is finished.
        The state of computation can be waited upon with the ``wait()`` method.

        The computation is launched only on the first call of this method.
        Subsequent calls do not relaunch it.

        Returns:
            :py:class:`~ansys.simai.core.data.lists.ExportablePPList` instance
            of :py:class:`~ansys.simai.core.data.post_processings.GlobalCoefficients`
            objects.
        """
        return ExportablePPList(
            selection=self._selection, post=lambda pred: pred.post.global_coefficients()
        )

    def surface_evolution(self, axis: str, delta: float) -> ExportablePPList[SurfaceEvolution]:
        """Compute or get the SurfaceEvolution of the predictions for specific parameters.

        This is a non-blocking method. It returns an
        :py:class:`~ansys.simai.core.data.lists.ExportablePPList` instance
        of :py:class:`~ansys.simai.core.data.post_processings.SurfaceEvolution`
        objects without waiting. Those ``PostProcessing`` objects may not have
        data right away if the computation is still in progress. Data is filled
        asynchronously once the computation is finished.
        The state of computation can be waited upon with the ``wait()`` method.

        The computation is launched only on the first call of this method
        with a specific set of parameters.
        Subsequent calls with the same parameters do not relaunch it.

        Args:
            axis: Axis to compute the the SurfaceEvolution on.
            delta: Increment of the abscissa in meters.

        Returns:
            :py:class:`~ansys.simai.core.data.lists.ExportablePPList` instance of
            :py:class:`~ansys.simai.core.data.post_processings.SurfaceEvolution` objects.
        """
        return ExportablePPList(
            selection=self._selection,
            post=lambda pred: pred.post.surface_evolution(axis, delta),
        )

    def slice(self, axis: str, coordinate: float) -> PPList[Slice]:
        """Compute or get a slice from each prediction in the selection.

        This is a non-blocking method. It returns a
        :py:class:`~ansys.simai.core.data.lists.PPList` instance of
        :py:class:`~ansys.simai.core.data.post_processings.Slice`
        objects without waiting. Those ``PostProcessing`` objects may not have
        data right away if the computation is still in progress. Data is filled
        asynchronously once the computation is finished.
        The state of computation can be waited upon with the ``wait()`` method.

        The computation is launched only on the first call of this method
        with a specific set of parameters.
        Subsequent calls with the same parameters do not relaunch it.

        The slices are in the NPZ format.

        Args:
            axis: Axis to slice.
            coordinate: Coordinate along the given axis to slice at.

        Returns:
            :py:class:`~ansys.simai.core.data.lists.PPList` list of
            :py:class:`~ansys.simai.core.data.post_processings.Slice` objects.
        """
        return PPList(
            selection=self._selection,
            post=lambda pred: pred.post.slice(axis=axis, coordinate=coordinate),
        )

    def volume_vtu(self) -> PPList[VolumeVTU]:
        """Compute or get the result of each prediction's volume in the VTU format.

        This is a non-blocking method. It returns a
        :py:class:`~ansys.simai.core.data.lists.PPList` instance of
        :py:class:`~ansys.simai.core.data.post_processings.VolumeVTU`
        objects without waiting. Those ``PostProcessing`` objects may not have
        data right away if the computation is still in progress. Data is filled
        asynchronously once the computation is finished.
        The state of computation can be waited upon with the ``wait()`` method.

        The computation is launched only on the first call of this method.
        Subsequent calls do not relaunch it.

        Returns:
            :py:class:`~ansys.simai.core.data.lists.PPList` instance of
            :py:class:`~ansys.simai.core.data.post_processings.VolumeVTU` objects.
        """
        return PPList(selection=self._selection, post=lambda pred: pred.post.volume_vtu())

    def surface_vtp(self) -> PPList[SurfaceVTP]:
        """Compute or get the result of each prediction's surface in the VTP format.

        This is a non-blocking method. It returns a
        :py:class:`~ansys.simai.core.data.lists.PPList` instance of
        :py:class:`~ansys.simai.core.data.post_processings.SurfaceVTP`
        objects without waiting. Those ``PostProcessing`` objects may not have
        data right away if the computation is still in progress. Data is filled
        asynchronously once the computation is finished.
        The state of computation can be waited upon with the ``wait()`` method.


        The computation is launched only on first call of this method.
        Subsequent calls do not relaunch it.

        Returns:
            :py:class:`~ansys.simai.core.data.lists.PPList` instance of
            :py:class:`~ansys.simai.core.data.post_processings.SurfaceVTP` objects.
        """
        return PPList(selection=self._selection, post=lambda pred: pred.post.surface_vtp())

    def surface_vtp_td_location(self) -> PPList[SurfaceVTPTDLocation]:
        """Compute or get the result of each prediction's surface in the VTP format.

        This method keeps the original data association as they are in the sample.

        It is a non-blocking method. It returns a
        :py:class:`~ansys.simai.core.data.lists.PPList` instance of
        :py:class:`~ansys.simai.core.data.post_processings.SurfaceVTPTDLocation`,
        objects without waiting. Those ``PostProcessing`` objects may not have
        data right away if the computation is still in progress. Data is filled
        asynchronously once the computation is finished.
        The state of computation can be waited upon with the ``wait()`` method.


        The computation is launched only on first call of this method.
        Subsequent calls do not relaunch it.

        Returns:
            :py:class:`~ansys.simai.core.data.lists.PPList` instance of
            :py:class:`~ansys.simai.core.data.post_processings.SurfaceVTPTDLocation`
        """
        return PPList(
            selection=self._selection, post=lambda pred: pred.post.surface_vtp_td_location()
        )
