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

import logging
from numbers import Number
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Optional, Union

from ansys.simai.core.data.base import (
    ComputableDataModel,
    Directory,
    UploadableResourceMixin,
)
from ansys.simai.core.data.geometry_utils import (
    _geometry_matches_range_constraints,
    _sweep,
)
from ansys.simai.core.data.post_processings import CustomVolumePointCloud
from ansys.simai.core.data.types import (
    BoundaryConditions,
    File,
    Identifiable,
    MonitorCallback,
    NamedFile,
    Range,
    build_boundary_conditions,
    get_id_from_identifiable,
    get_object_from_identifiable,
    unpack_named_file,
)
from ansys.simai.core.data.workspaces import Workspace
from ansys.simai.core.errors import InvalidArguments, InvalidOperationError

if TYPE_CHECKING:
    from ansys.simai.core.data.predictions import Prediction

logger = logging.getLogger(__name__)


class Geometry(UploadableResourceMixin, ComputableDataModel):
    """Provides the local representation of a geometry object."""

    def __repr__(self) -> str:
        return f"<Geometry: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """Name of the geometry."""
        return self.fields["name"]

    @property
    def metadata(self) -> Dict[str, Any]:
        """User-given key-value associated with the geometry."""
        return self.fields["metadata"]

    @property
    def creation_time(self) -> str:
        """Time when the geometry was created in a UTC ISO8601 format string."""
        return self.fields["creation_time"]

    @property
    def point_cloud(self) -> Optional[Dict[str, Any]]:
        """The attached point cloud file information if any."""
        return self.fields.get("point_cloud")

    def rename(self, name: str) -> None:
        """Change the name of the geometry.

        Args:
            name: New name to give to the geometry.

        Note:
            Only the stem part is modified. The file extension is immutable.
            If a file extension is provided, it must be the same as the original one.
            If the new filename already contains dots other than for the extension,
            the extension must be provided.
        """
        self._client._api.update_geometry(self.id, name=name)
        self.reload()

    def update_metadata(self, metadata: Dict[str, Union[str, Number, bool]]):
        """Change the metadata of the geometry.

        - New keys-values are added.
        - Existing keys-values are overwritten.
        - Other key-values are not changed.

        To delete a metadata, set it to ``None`` explicitly.

        Args:
            metadata: Dictionary with the new data.

        Examples:
            Add or update a metadata.

            .. code-block:: python

                geometry.update_metadata({"new_metadata": "value", "existing_metadata": 10})

            Remove all metadata.

            .. code-block:: python

               geometry.update_metadata({key: None for key in geometry.metadata.keys()})
        """
        self._client._api.update_geometry(self.id, metadata=metadata)
        self.reload()

    def delete(self) -> None:
        """Delete the geometry and its data from the server.

        All the objects associated with this geometry (predictions and postprocessings)
        are also deleted.

        See Also:
            :func:`GeometryDirectory.delete`
        """
        self._client._api.delete_geometry(self.id)

    def run_prediction(
        self, boundary_conditions: Optional[BoundaryConditions] = None, **kwargs
    ) -> "Prediction":
        """Run a new prediction or return an existing prediction.

        This is a non-blocking method. The prediction object is returned.
        This object may be incomplete if its computation is not finished,
        in which case the information is filled once the computation is complete.
        The state of the computation can be monitored with the prediction's ``is_ready``
        attribute or waited upon with its ``wait()`` method.

        To learn more about the expected boundary conditions in your workspace, you can use the
        ``simai.current_workspace.model.boundary_conditions`` or ``simai.predictions.boundary_conditions``,
        where ``ex`` is your `~ansys.simai.core.client.SimAIClient` object.

        Args:
            boundary_conditions: Boundary conditions to apply as a dictionary.
            **kwargs: Boundary conditions to pass as keyword arguments.

        Returns:
            Created prediction object.

        Raises:
            ProcessingError: If the server failed to process the request.

        Examples:
            .. code-block:: python

                simai = ansys.simai.core.from_config()
                geometry = simai.geometries.list()[0]
                geometry.run_prediction(dict(Vx=10.5, Vy=2))

            Use kwargs:

            .. code-block:: python

                prediction = geometry.run_prediction(Vx=10.5, Vy=2)
        """
        bc = build_boundary_conditions(boundary_conditions, **kwargs)
        prediction_response = self._client._api.run_prediction(self.id, boundary_conditions=bc)
        return self._client.predictions._model_from(prediction_response)

    def get_predictions(self) -> List["Prediction"]:
        """Get the prediction objects associated with the geometry."""
        predictions_data = self._client._api.get_geometry_predictions(self.id)
        return [self._client.predictions._model_from(pred_data) for pred_data in predictions_data]

    def download(
        self,
        file: Optional[File] = None,
        monitor_callback: Optional[MonitorCallback] = None,
    ) -> Union[None, BinaryIO]:
        """Download the geometry into the provided file or in memory if no file is provided.

        Args:
            file: Optional binary file-object or the path of the file to put the
                content into.
            monitor_callback: Optional callback to monitor the progress of the download.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.

        Returns:
            ``None`` if a file is provided or the :class:`~io.BytesIO` object with the geometry's content otherwise.
        """
        return self._client._api.download_geometry(self.id, file, monitor_callback)

    def sweep(
        self,
        swept_metadata: Optional[Union[str, List[str]]] = None,
        fixed_metadata: Optional[List[str]] = None,
        geometries: Optional[List["Geometry"]] = None,
        order: Optional[int] = None,
        include_center: Optional[bool] = None,
        include_diagonals: Optional[bool] = None,
        tolerance: Optional[float] = None,
    ) -> List["Geometry"]:
        """Return geometries whose metadata are closest to the candidate geometry.

        This method returns geometries that have the values closest to the candidate
        geometry for each considered metadata variable. For example, if
        sweeping along ``length`` and ``width`` metadata variables, the method
        returns geometries that have identical width and the closest smaller
        and larger length, as well as identical length and the closest smaller
        and larger width.

        The ``fixed_metadata`` array allows you to fix one or several variables.
        For each fixed variable, the resulting geometries must have
        a metadata value equal to the considered geometry. For example, if
        ``fixed_metadata`` is ``["xbow"]``, every ``geometry.metadata["xbow"]``
        result must be equal to the ``candidate_geometry.metadata["xbow"]``.

        Metadata passed neither in ``swept_metadata`` nor in ``fixed_metadata``
        are ignored and can have any value (or absence thereof).

        Args:
            swept_metadata: Optional metadata name or a list of metadata names
                to consider. Only variables containing numerical values are
                supported. If no metadata names are passed, all metadata containing
                numerical values are taken into account.
            fixed_metadata: Optional list of metadata variables that should
                be fixed, meaning that all the resulting geometries
                have those values equal to the candidate geometry.
            geometries: Optional list of ``Geometry`` objects to consider for sweeping.
                If no ``Geometry`` objects are passed, all geometries are used.
            tolerance: Optional delta. If the difference between two numbers
                is lower than the tolerance, they are considered as equal.
                The default is ``10**-6``.
            order: Optional depth of the sweep. The default is ``1``. This parameter
                determines the number of returned groups of equal smaller and
                larger values for each swept variable. For example, if sweeping
                on a space with lengths ``[1, 2.1, 2.1, 3.5, 3.5, 4, 4]``
                from the candidate with ``length=1``, ``order=2`` returns
                the geometries with lengths ``2.1, 2.1, 3.5, 3.5``.
            include_center: Optional Boolean indicating whether geometries with values
                equal to the candidate geometry (including the candidate itself) are
                to be returned among the result. The default is ``False``.
            include_diagonals: Optional Boolean indicating whether to include diagonals
                when sweeping on more than one variable. The default is ``False``.
                For example, if sweeping on two variables from point ``(0, 0)``
                and with ``order=1``, in addition to ``(0, 1)`` and ``(1, 0)``,
                geometry ``(1, 1)`` is returned.

        Returns:
            List of ``Geometry`` objects neighboring the candidate geometry for each metadata.

        Raises:
            ValueError: If a passed variable doesn't exist in the
                candidate geometry.
            ValueError: If the considered metadata contains non-numerical values
                or mixed numerical and non numerical values.

        Example:
            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                geom = simai.geometries.get("kz19jyqm")
                geometries = geom.sweep(["length"])
        """
        if geometries is None:
            geometries = self._client.geometries.list()
        return _sweep(
            candidate_geometry=self,
            geometries=geometries,
            swept_metadata=swept_metadata,
            fixed_metadata=fixed_metadata,
            order=order,
            include_center=include_center,
            include_diagonals=include_diagonals,
            tolerance=tolerance,
        )

    def upload_point_cloud(
        self, file: NamedFile, monitor_callback: Optional[MonitorCallback] = None
    ):
        """Upload a point cloud for this geometry.

        Only the vtp file format is supported

        Args:
            file: :obj:`~ansys.simai.core.data.types.NamedFile` to upload.
            monitor_callback: Optional callback for monitoring the progress of the upload.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.
        """
        with unpack_named_file(file) as (readable_file, name, extension):
            response = self._client._api.create_point_cloud(self.id, name, extension)
            upload_id = response["upload_id"]
            point_cloud_fields = response["point_cloud"]
            parts = self._client._api.upload_parts(
                f"point-clouds/{point_cloud_fields['id']}/part",
                readable_file,
                upload_id,
                monitor_callback=monitor_callback,
            )
            self._client._api.complete_point_cloud_upload(
                point_cloud_fields["id"], upload_id, parts
            )
            self._fields["point_cloud"] = point_cloud_fields

    def delete_point_cloud(self):
        """Delete the associated point cloud file."""
        if not self.point_cloud:
            raise InvalidOperationError("No point cloud file to delete")
        self._client._api.delete_point_cloud(self.point_cloud["id"])
        self._fields["point_cloud"] = None
        # The post-processing will be deleted server side but the prediction cache will still
        # have the post-processing registered. Meaning a new _get_or_run of the post-processing will
        # attempt a get, thinking the post-processing exists. So for all the registered prediction who
        # belong to the current geometry, we need to clear the CustomVolumePointCloud local registry.
        for prediction in self._client._prediction_directory._registry.values():
            if prediction.geometry_id == self.id:
                prediction.post._post_processings[CustomVolumePointCloud] = {}


class GeometryDirectory(Directory[Geometry]):
    """Provides a collection of methods related to geometries.

    This class is accessed through ``client.geometries``.

    Example:
        .. code-block:: python

            import ansys.simai.core

            simai = ansys.simai.core.from_config()
            simai.geometries.list()
    """

    _data_model = Geometry

    def list(
        self,
        workspace: Optional[Identifiable[Workspace]] = None,
        filters: Optional[Dict[str, Union[str, float, Range]]] = None,
    ) -> List[Geometry]:
        """List geometries from the server that belong to the currently set workspace or the specified one.

        Args:
            workspace: ID or :class:`model <.workspaces.Workspace>` of the workspace to list geometries for.
                This parameter is required if no global workspace is set for the client.
            filters: Optional filters. Only the elements with matching key-values in
                their metadata are returned. Each filter can be one of the following data types:

                - A string
                - A numerical value (int or float)
                - A :py:class:`Range` condition for filtering values matching a
                  given numerical range of values

        Returns:
            List of all or filtered geometries on the server.

        Raises:
            TypeError: If a :py:class:`Range` condition is applied on non-numerical metadata.
        """
        workspace_id = get_id_from_identifiable(workspace, default=self._client._current_workspace)

        # for now we filter ranges locally, so we filter
        # local filters (ranges) from server filters (everything else)
        ranges: Dict[str, Range] = {}
        server_filters: Dict[str, Union[str, float]] = {}
        if filters is not None:
            for metadata, filter in filters.items():
                if isinstance(filter, Range):
                    ranges[metadata] = filter
                else:
                    server_filters[metadata] = filter
        geometries = [
            self._model_from(data)
            for data in self._client._api.geometries(workspace_id, server_filters)
        ]
        return [
            geometry
            for geometry in geometries
            if _geometry_matches_range_constraints(geometry, ranges)
        ]

    def filter(self, **kwargs: Dict[str, Union[str, float, Range]]) -> List[Geometry]:
        """Filter geometries from the server that belong to the currently set workspace.

        Args:
            kwargs: Filters to apply. Only the elements with matching key-values in
                their metadata are returned. Each filter can be one of the following data types:

                - A string
                - A numerical value (int or float)
                - A :py:class:`Range` condition for filtering values matching a
                  given numerical range of values

        Returns:
            List of filtered geometries on the server.

        Raises:
            TypeError: If a :py:class:`Range` condition is applied on non-numerical metadata.
        """
        return self.list(filters=kwargs)

    def get(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        workspace: Optional[Identifiable[Workspace]] = None,
    ) -> Geometry:
        """Get a specific geometry object from the server either by name or ID.

        You can specify either the ID or the name, not both.


        Args:
            name: Name of the geometry.
            id: ID of the geometry.
            workspace: ID or :class:`model <.workspaces.Workspace>` of the workspace containing the geometry.
                This parameter is necessary if providing a name and no global workspace is set for the client.

        Returns:
            :py:class:`Geometry`.

        Raises:
            InvalidArguments: If neither a name nor an ID is given.
            NotFoundError: If no geometry with the given name or ID exists.

        Examples:
            Get a geometry by name.

            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                geometry = simai.geometries.get("my_geometry.stl")
                # geometry = simai.geometries.get(name="my_geometry.stl") # is equivalent

            Get a geometry by ID.

            .. code-block:: python

                    geometry = simai.geometries.get(id="abcdef12")
        """
        if name and id:
            raise InvalidArguments("Name and ID cannot both be specified.")
        if name:
            return self._model_from(
                self._client._api.get_geometry_by_name(
                    name,
                    get_id_from_identifiable(workspace, default=self._client._current_workspace),
                )
            )
        if id:
            return self._model_from(self._client._api.get_geometry(id))
        raise InvalidArguments("Either the name or the ID must be specified.")

    def delete(self, geometry: Identifiable[Geometry]) -> None:
        """Delete a specific geometry and its data from the server.

        All the objects associated with this geometry (predictions and postprocessings)
        are also deleted.

        Args:
            geometry: ID or :class:`model <Geometry>` of the geometry.

        Raises:
            NotFoundError: No geometry with the given ID exists.

        See Also:
            :func:`Geometry.delete`
        """
        self._client._api.delete_geometry(get_id_from_identifiable(geometry))

    def upload(  # noqa: D417
        self,
        file: NamedFile,
        metadata: Optional[Dict[str, Any]] = None,
        workspace: Optional[Identifiable[Workspace]] = None,
        monitor_callback: Optional[MonitorCallback] = None,
        **kwargs,
    ) -> Geometry:
        """Upload a geometry to the SimAI platform.

        Args:
            file: Binary file-object or the path of the geometry to open.
                For more information, see the :class:`~ansys.simai.core.data.types.NamedFile` class.
            metadata: Optional metadata to add to the geometry's simple key-value store.
                Lists and nested objects are not supported.
            workspace: ID or :class:`model <.workspaces.Workspace>` of the workspace to
                upload the geometry to. This parameter is only necessary if no workspace
                is set for the client.
            monitor_callback: Optional callback for monitoring the progress of the download.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.

        Returns:
            Created :py:class:`Geometry` object.
        """
        workspace = get_object_from_identifiable(
            workspace, self._client.workspaces, default=self._client._current_workspace
        )
        with unpack_named_file(file) as (readable_file, name, extension):
            if extension not in workspace.model_manifest.geometry["accepted_file_formats"]:
                raise InvalidArguments(
                    f"Got a file with {extension} extension but expected one of : {workspace.model_manifest.geometry['accepted_file_formats']}"
                )
            (geometry_fields, upload_id) = self._client._api.create_geometry(
                workspace.id, name, extension, metadata
            )
            geometry = self._model_from(geometry_fields, is_upload_complete=False)
            parts = self._client._api.upload_parts(
                f"geometries/{geometry.id}/part",
                readable_file,
                upload_id,
                monitor_callback=monitor_callback,
            )
            self._client._api.complete_geometry_upload(geometry.id, upload_id, parts)
        return geometry

    def download(
        self,
        geometry: Identifiable[Geometry],
        file: Optional[File] = None,
        monitor_callback: Optional[MonitorCallback] = None,
    ) -> Union[None, BinaryIO]:
        """Download the geometry with the given ID into the file at the given path.

        Args:
            geometry: ID or :class:`model <Geometry>` of the geometry.
            file: Optional binary file-object or the path of the file to put the
                content into.
            monitor_callback: Optional callback for monitoring the progress of the download.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.

        Returns:
            ``None`` if a file is provided or a :class:`~io.BytesIO` object with the geometry's content otherwise.

        See Also:
            :func:`Geometry.download`
        """
        return self._client._api.download_geometry(
            get_id_from_identifiable(geometry), file, monitor_callback
        )

    def sweep(
        self,
        candidate_geometry: Identifiable[Geometry],
        swept_metadata: Optional[Union[str, List[str]]] = None,
        fixed_metadata: Optional[List[str]] = None,
        geometries: Optional[List["Geometry"]] = None,
        order: Optional[int] = None,
        include_center: Optional[bool] = None,
        include_diagonals: Optional[bool] = None,
        tolerance: Optional[float] = None,
    ) -> List["Geometry"]:
        """Get the geometries whose metadata are closest to the candidate geometry.

        For more information, see the :func:`Geometry.sweep` method.

        Example:
            .. code-block:: python

                import ansys.simai.core

                simai = ansys.simai.core.from_config()
                geom = simai.geometries.get("kz19jyqm")
                geometries = simai.geometries.sweep(geom, ["length"])

        See Also:
            :func:`Geometry.sweep`
        """
        candidate_geometry = get_object_from_identifiable(
            candidate_geometry, self._client.geometries
        )
        return candidate_geometry.sweep(
            swept_metadata=swept_metadata,
            fixed_metadata=fixed_metadata,
            geometries=geometries,
            order=order,
            include_center=include_center,
            include_diagonals=include_diagonals,
            tolerance=tolerance,
        )
