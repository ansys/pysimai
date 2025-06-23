# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.simai.core.data.base import DataModel, Directory, UploadableResourceMixin


class GeomAITrainingDataPart(UploadableResourceMixin, DataModel):
    """Provides the local representation of a GeomAI training data part object."""

    def __repr__(self) -> str:
        return f"<GeomAITrainingDataPart: {self.id}, {self.name}>"

    @property
    def name(self) -> str:
        """Name of the file."""
        return self.fields["name"]

    @property
    def size(self) -> int:
        """Size of the file in bytes."""
        return self.fields["size"]


class GeomAITrainingDataPartDirectory(Directory[GeomAITrainingDataPart]):
    """Provides the collection of methods related to GeomAI training data parts.

    This class is accessed through ``client.geomai.training_data_parts``.
    """

    _data_model = GeomAITrainingDataPart

    def get(self, id: str) -> GeomAITrainingDataPart:
        """Get a :class:`GeomAITrainingDataPart` object from the server.

        Args:
            id: ID of the training data part.

        Returns:
            :class:`GeomAITrainingDataPart` instance with the given ID if it exists.

        Raises:
            NotFoundError: No prediction with the given ID exists.
        """
        return self._model_from(self._client._api.get_geomai_training_data_part(id))
