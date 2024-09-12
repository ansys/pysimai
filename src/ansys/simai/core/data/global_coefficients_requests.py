# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

from ansys.simai.core.data.base import (
    ERROR_STATES,
    PENDING_STATES,
    ComputableDataModel,
    Directory,
)
from ansys.simai.core.utils.numerical import cast_values_to_float

if TYPE_CHECKING:
    import ansys.simai.core.client

EXTRA_CALCULETTE_FIELDS = ["Area", "Normals", "Centroids"]

logger = logging.getLogger(__name__)


class GlobalCoefficientRequest(ABC, ComputableDataModel):
    """Creates the foundational request for subsequent Global Coefficients requests/inquiries."""

    def __init__(
        self,
        client: "ansys.simai.core.client.SimAIClient",
        directory: "Directory",
        fields: dict,
        project_id: str,
        gc_formula: str,
        sample_metadata: dict[str, Any],
        bc: list[str] = None,
        surface_variables: list[str] = None,
        **kwargs,
    ):
        super().__init__(client=client, directory=directory, fields=fields)

        self.project_id = project_id
        self._calculette_payload = self._compose_calculette_payload(
            gc_formula, sample_metadata, bc, surface_variables
        )

    @ComputableDataModel._failure_message.getter
    def _failure_message(self):
        return self.fields.get("error")

    def _compose_calculette_payload(
        self,
        gc_formula: str,
        sample_metadata: dict[str, Any],
        bc: list[str] = None,
        surface_variables: list[str] = None,
    ):
        """Composes the payload for a calculette request."""

        surface_vars_list = EXTRA_CALCULETTE_FIELDS
        if surface_variables:
            surface_vars_list += surface_variables

        return {
            "formula": gc_formula,
            "bc_list": bc if bc else [],
            "surface_field_list": [
                fd
                for fd in sample_metadata.get("surface").get("fields")
                if fd.get("name") in surface_vars_list
            ],
            "volume_field_list": [],
        }

    @abstractmethod
    def run(self):
        """Abstract method to perform the customized required process."""


GlobalCoefficientRequestType = TypeVar(
    "GlobalCoefficientRequestType", bound=GlobalCoefficientRequest
)


class GlobalCoefficientRequestDirectory(Directory[GlobalCoefficientRequestType]):
    """Provides methods for handling SSEs related to Global Coefficients."""

    def get(self, item_id: str) -> GlobalCoefficientRequestType:
        """Get a  by project ID.

        Args:
            item_id: ID of the Global Coefficient request.
        """

        return self._registry[item_id] if item_id not in self._registry else None

    def _handle_sse_event(self, data):
        gc_formula = data.get("target").get("formula")
        action = data.get("target").get("action")
        item_id: str = f"{data['target']['id']}-{action}-{gc_formula}"
        if item_id not in self._registry:
            logger.debug(
                f"{self.__class__.__name__}: Ignoring event for unknown object id {item_id}"
            )
            return
        item = self._registry[item_id]

        item._handle_job_sse_event(data)


class CheckGlobalCoefficient(GlobalCoefficientRequest):
    """Verifies a Global Coefficient formula."""

    def run(self):
        """Performs a check-formula request."""
        self._client._api.check_formula(self.project_id, self._calculette_payload)

    def _handle_job_sse_event(self, data):
        """Manage object's state according to SSE."""
        logger.debug(f"Handling SSE job event for {self._classname} id {self.id}")

        state: str = data.get("status")

        target = data.get("target")

        if state in PENDING_STATES:
            logger.debug(f"{self._classname} id {self.id} set status pending")
            self._set_is_pending()
        elif state == "successful":
            logger.debug(f"{self._classname} id {self.id} set status successful")
            self._set_is_over()
        elif state in ERROR_STATES:
            error_message = f"Verification of formula {target.get('formula')} failed with {data.get('reason', 'UNKNOWN ERROR')}"
            self.fields["error"] = error_message
            self._set_has_failed()
            logger.error(error_message)


class CheckGlobalCoefficientDirectory(GlobalCoefficientRequestDirectory[CheckGlobalCoefficient]):
    """Extends GlobalCoefficientRequestDirectory for verifying a Global Coefficient formula."""

    _data_model = CheckGlobalCoefficient


class ComputeGlobalCoefficient(GlobalCoefficientRequest):
    """Computes the result of a Global Coefficient formula."""

    def run(self):
        """Performs a compute-formula request."""
        self._client._api.compute_formula(self.project_id, self._calculette_payload)

    def _handle_job_sse_event(self, data):
        """Manage object's state according to SSE and store the result of the formula."""
        logger.debug(f"Handling SSE job event for {self._classname} id {self.id}")

        state: str = data.get("status")

        target = data.get("target")

        if state in PENDING_STATES:
            logger.debug(f"{self._classname} id {self.id} set status pending")
            self._set_is_pending()
        elif state == "successful":
            logger.debug(f"{self._classname} id {self.id} set status successful")
            self._result = cast_values_to_float(data.get("result", {}).get("value"))
            self._set_is_over()
        elif state in ERROR_STATES:
            error_message = f"Computation of global coefficient {target.get('formula')} failed with {data.get('reason', 'UNKNOWN ERROR')}"
            self.fields["error"] = error_message
            self._set_has_failed()
            logger.error(error_message)

    @property
    def result(self):
        """Get the result of the Global Coefficient formula."""
        return self._result if self.is_ready else None


class ComputeGlobalCoefficientDirectory(
    GlobalCoefficientRequestDirectory[ComputeGlobalCoefficient]
):
    """Extends GlobalCoefficientRequestDirectory for computing the result of a Global Coefficient formula."""

    _data_model = ComputeGlobalCoefficient
