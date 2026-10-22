# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from typing import TYPE_CHECKING, List, Optional

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.types import (
    Identifiable,
    MonitorCallback,
    NamedFile,
    get_id_from_identifiable,
    unpack_named_file,
)
from ansys.simai.core.errors import InvalidArguments

if TYPE_CHECKING:
    from ansys.simai.core.data.geomai.projections import GeomAIProjection
    from ansys.simai.core.data.geomai.workspaces import GeomAIWorkspace

logger = logging.getLogger(__name__)

SUPPORTED_GEOMETRY_FORMATS = ("vtp", "zip", "stl", "cgns")
"""File formats accepted by the GeomAI geometry upload."""


def _upload_geomai_geometry(named_file, client, monitor_callback) -> "GeomAIGeometry":
    with unpack_named_file(named_file) as (file, name, extension):
        if extension.lower() not in SUPPORTED_GEOMETRY_FORMATS:
            raise InvalidArguments(
                f"Unsupported file extension '{extension}'. "
                f"Supported extensions are: {', '.join(SUPPORTED_GEOMETRY_FORMATS)}."
            )
        (geometry_fields, upload_id) = client._api.create_geomai_geometry(name, extension)
        geometry = client.geomai.geometries._model_from(geometry_fields)
        parts = client._api.upload_parts(
            f"geomai/geometries/{geometry.id}/part",
            file,
            upload_id,
            monitor_callback=monitor_callback,
        )
        client._api.complete_geomai_geometry_upload(geometry.id, upload_id, parts)
    return geometry


class GeomAIGeometry(ComputableDataModel):
    """Provides the local representation of a GeomAI geometry object."""

    def __repr__(self) -> str:
        return f"<GeomAIGeometry: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """Name of the geometry."""
        return self.fields["name"]

    def rename(self, new_name: str) -> None:
        """Rename the geometry.

        Args:
            new_name: New name to give to the geometry.
        """
        self._client._api.update_geomai_geometry(self.id, name=new_name)
        self.reload()

    def delete(self) -> None:
        """Delete the geometry and all its data from the server."""
        self._client._api.delete_geomai_geometry(self.id)
        self._unregister()

    def run_projection(
        self, workspace: Optional[Identifiable["GeomAIWorkspace"]] = None
    ) -> "GeomAIProjection":
        """Project the geometry onto the model of the given workspace.

        Args:
            workspace: Optional ID or :class:`model <.workspaces.GeomAIWorkspace>` of the
                target workspace. Defaults to the current workspace if set.

        Returns:
            The :class:`~.projections.GeomAIProjection` of the geometry.
        """
        return self._client.geomai.projections.run(self, workspace)

    def get_projection(
        self, workspace: Optional[Identifiable["GeomAIWorkspace"]] = None
    ) -> Optional["GeomAIProjection"]:
        """Get the existing projection of the geometry onto the model of the given workspace.

        Args:
            workspace: Optional ID or :class:`model <.workspaces.GeomAIWorkspace>` of the
                target workspace. Defaults to the current workspace if set.

        Returns:
            The :class:`~.projections.GeomAIProjection` of the geometry if it exists,
            ``None`` otherwise.
        """
        projections = self._client.geomai.projections.list(workspace=workspace, geometry=self)
        return projections[0] if projections else None


class GeomAIGeometryDirectory(Directory[GeomAIGeometry]):
    """Provides a collection of methods related to GeomAI geometries.

    This class is accessed through ``client.geomai.geometries``.

    Example:
        .. code-block:: python

            import ansys.simai.core as asc

            simai_client = asc.from_config()
            simai_client.geomai.geometries.list()
    """

    _data_model = GeomAIGeometry

    def list(self) -> List[GeomAIGeometry]:
        """List all the :class:`GeomAIGeometry` objects on the server.

        Returns:
            List of all the :class:`GeomAIGeometry` objects on the server.
        """
        return [self._model_from(geometry) for geometry in self._client._api.geomai_geometries()]

    def get(self, id: Optional[str] = None, name: Optional[str] = None) -> GeomAIGeometry:
        """Get a specific :class:`GeomAIGeometry` object from the server.

        You can specify either the ID or the name, not both.

        Args:
            id: ID of the geometry.
            name: Name of the geometry.

        Returns:
            :class:`GeomAIGeometry`

        Raises:
            NotFoundError: No geometry with the given ID or name exists.
        """
        if name and id:
            raise InvalidArguments("Cannot specify both 'id' and 'name' arguments.")
        elif name:
            return self._model_from(self._client._api.get_geomai_geometry_by_name(name))
        elif id:
            return self._model_from(self._client._api.get_geomai_geometry(id))
        else:
            raise InvalidArguments("Either 'id' or 'name' argument must be specified.")

    def upload(
        self, file: NamedFile, monitor_callback: Optional[MonitorCallback] = None
    ) -> GeomAIGeometry:
        """Upload a geometry to the server.

        The supported file formats are ``vtp``, ``zip``, ``stl``, and ``cgns``.

        Args:
            file: :obj:`~ansys.simai.core.data.types.NamedFile` to upload.
            monitor_callback: Optional callback for monitoring the progress of the upload.
                For more information, see the :obj:`~ansys.simai.core.data.types.MonitorCallback`
                object.

        Returns:
            Created :class:`GeomAIGeometry` object.

        Raises:
            InvalidArguments: If the file extension is not supported.

        Example:
            .. code-block:: python

                import ansys.simai.core as asc

                simai_client = asc.from_config()
                geometry = simai_client.geomai.geometries.upload("my_geometry.vtp")
                geometry.wait()
        """
        return _upload_geomai_geometry(file, self._client, monitor_callback)

    def delete(self, geometry: Identifiable[GeomAIGeometry]) -> None:
        """Delete a :class:`GeomAIGeometry` object and all its data from the server.

        Args:
            geometry: ID or :class:`model <GeomAIGeometry>` of the geometry.

        Raises:
            NotFoundError: No geometry with the given ID exists.
        """
        geometry_id = get_id_from_identifiable(geometry)
        self._client._api.delete_geomai_geometry(geometry_id)
        self._unregister_item_with_id(geometry_id)
