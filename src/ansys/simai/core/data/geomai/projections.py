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
from typing import List, Optional

from ansys.simai.core.data.base import ComputableDataModel, Directory
from ansys.simai.core.data.geomai.geometries import GeomAIGeometry
from ansys.simai.core.data.geomai.workspaces import GeomAIWorkspace
from ansys.simai.core.data.types import Identifiable, get_id_from_identifiable
from ansys.simai.core.errors import InvalidArguments

logger = logging.getLogger(__name__)


class GeomAIProjection(ComputableDataModel):
    """Provides the local representation of a GeomAI projection object."""

    def __repr__(self) -> str:
        return f"<GeomAIProjection: {self.id}, geometry {self.geometry_id}>"

    @property
    def geometry_id(self) -> str:
        """ID of the projected geometry."""
        return self.fields["geometry_id"]

    @property
    def workspace_id(self) -> str:
        """ID of the workspace the projection was run in."""
        return self.fields["workspace_id"]

    @property
    def latent_code(self) -> Optional[List[float]]:
        """Coordinates of the geometry in the latent space of the model.

        The value is ``None`` until the projection has finished successfully.

        See Also:
            :meth:`~get_latent_code`
        """
        return self.fields.get("latent_code")

    def get_latent_code(self, n: Optional[int] = None) -> List[float]:
        """Get the coordinates of the geometry in the latent space of the model.

        This method waits for the projection to be over before returning.

        By default, latent parameters are ordered by importance: the first ones capture
        the largest sources of variation in the training data, while later ones capture
        increasingly finer details.

        Args:
            n: Optional number of latent parameters to retrieve, that is the length of
                the returned vector. If ``None``, all latent parameters are returned.
                Must not exceed the number of latent parameters used for model training.

        Returns:
            The latent code of the geometry.

        Raises:
            InvalidArguments: If ``n`` exceeds the number of latent parameters used for
                model training.
        """
        latent_code = self.latent_code or []
        if n is not None:
            if n > len(latent_code):
                raise InvalidArguments(
                    f"n ({n}) exceeds the number of latent parameters used for model training ({len(latent_code)})."
                )
            latent_code = latent_code[:n]
        return latent_code

    def delete(self) -> None:
        """Delete the projection from the server."""
        self._client._api.delete_geomai_projection(self.id)
        self._unregister()


class GeomAIProjectionDirectory(Directory[GeomAIProjection]):
    """Provides a collection of methods related to GeomAI projections.

    This class is accessed through ``client.geomai.projections``.

    Example:
        .. code-block:: python

            import ansys.simai.core as asc

            simai_client = asc.from_config()
            simai_client.geomai.projections.list()
    """

    _data_model = GeomAIProjection

    def list(
        self,
        workspace: Optional[Identifiable[GeomAIWorkspace]] = None,
        geometry: Optional[Identifiable[GeomAIGeometry]] = None,
    ) -> List[GeomAIProjection]:
        """List the projections onto the model of the specified workspace or the configured one.

        Args:
            workspace: ID or :class:`model <.workspaces.GeomAIWorkspace>` of the workspace to
                list the projections for. This parameter is necessary if no workspace is set
                for the client.
            geometry: Optional ID or :class:`model <.geometries.GeomAIGeometry>` of a geometry
                to restrict the listing to.

        Returns:
            List of the matching :class:`GeomAIProjection` objects.
        """
        workspace_id = get_id_from_identifiable(
            workspace, default=self._client.geomai._current_workspace
        )
        geometry_id = get_id_from_identifiable(geometry, required=False)
        raw_projections = self._client._api.geomai_projections(workspace_id, geometry_id)
        return list(map(self._model_from, raw_projections))

    def get(self, id: str) -> GeomAIProjection:
        """Get a specific GeomAI projection object from the server by ID.

        Args:
            id: ID of the projection.

        Returns:
            :class:`GeomAIProjection` instance with the given ID if it exists.

        Raises:
            NotFoundError: No projection with the given ID exists.
        """
        return self._model_from(self._client._api.get_geomai_projection(id))

    def run(
        self,
        geometry: Identifiable[GeomAIGeometry],
        workspace: Optional[Identifiable[GeomAIWorkspace]] = None,
    ) -> GeomAIProjection:
        """Project a geometry onto the model of the given workspace.

        Args:
            geometry: ID or :class:`model <.geometries.GeomAIGeometry>` of the geometry
                to project.
            workspace: ID or :class:`model <.workspaces.GeomAIWorkspace>` of the
                target workspace. Defaults to the current workspace if set.

        Returns:
            The created or existing :class:`GeomAIProjection` object.


        Example:
            .. code-block:: python

                import ansys.simai.core as asc

                simai_client = asc.from_config()
                workspace = simai_client.geomai.workspaces.get(name="my-workspace")
                geometry = simai_client.geomai.geometries.upload("my_geometry.vtp")
                geometry.wait()

                projection = simai_client.geomai.projections.run(geometry, workspace)
                projection.wait()
                print(projection.latent_code)
        """
        workspace_id = get_id_from_identifiable(
            workspace, default=self._client.geomai._current_workspace
        )
        geometry_id = get_id_from_identifiable(geometry)
        return self._model_from(self._client._api.run_geomai_projection(workspace_id, geometry_id))

    def delete(self, projection: Identifiable[GeomAIProjection]) -> None:
        """Delete a specific GeomAI projection from the server.

        Args:
            projection: ID or :class:`model <GeomAIProjection>` of the projection.

        Raises:
            NotFoundError: No projection with the given ID exists.
        """
        projection_id = get_id_from_identifiable(projection)
        self._client._api.delete_geomai_projection(projection_id)
        self._unregister_item_with_id(projection_id)
