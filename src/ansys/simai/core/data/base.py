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
from abc import ABC, abstractmethod
from threading import Event
from typing import Dict, Generic, Optional, Type, TypeVar

import ansys.simai.core.client
from ansys.simai.core.errors import ProcessingError

logger = logging.getLogger(__name__)


ERROR_STATES = ["failure", "rejected", "cancelled"]
PENDING_STATES = [
    "unknown",
    "queued",
    "pending request",
    "requested",
    "processing",
    "pending_retry",
]


class DataModel:
    """
    A base class representing a single object of a particular type on the server.
    """

    def __init__(
        self,
        client: "ansys.simai.core.client.SimAIClient",
        directory: "Directory",
        fields: dict,
        **kwargs,
    ):
        # Override id_key to configure the field to return with :py:meth:`Model.id`.
        self.id_key = "id"
        self.fields = fields or dict()
        self._directory = directory
        self._client = client
        if (
            self.fields.get("workspace_id")
            and self.fields["workspace_id"] != self._client.current_workspace.id
        ):
            logger.warning("The object does not belong to the currently configured workspace.")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.id}>"

    @property
    def id(self) -> str:
        """The id of the object on the server."""
        # Uses the :py:attr:`id_key` to determine the name of the id.
        # :py:attr:`id_key` defaults to id
        return self._fields[self.id_key]

    @property
    def fields(self) -> dict:
        """A dictionary containing the raw object representation."""
        return self._fields

    @fields.setter
    def fields(self, new_fields: dict) -> None:
        self._fields = new_fields

    def reload(self) -> None:
        """
        Refresh the object with its representation from the server.
        """
        updated_data = self._directory.get(id=self.id)
        self.fields = updated_data._fields

    @property
    def _classname(self):
        return self.__class__.__name__


class ComputableDataModel(DataModel):
    """
    Base class for all computable models whose creation eventually succeeds or fails.
    """

    def __init__(
        self,
        client: "ansys.simai.core.client.SimAIClient",
        directory: "Directory",
        fields: dict,
        **kwargs,
    ):
        super().__init__(client=client, directory=directory, fields=fields)

        # threading.Event object that represents the finalization state
        # of this object. Its wait() will block until the object
        # is finished processing. Used by this class' wait() method.
        # It is `cleared` state as long as the object is loading (queud or processing)
        # and in `set` state when finalized (complete or failed)
        self._is_over = Event()

        # set the initial state of _is_over event,
        # so the user can wait() on the object
        # even before we receive any SSE event
        state = self.fields.get("state")
        if state == "successful" or state in ERROR_STATES:
            logger.debug(f"set {self._classname} {fields['id']} as idle")
            self._set_is_over()
        else:
            logger.debug(f"set {self._classname} {fields['id']} as pending")
            self._set_is_pending()

        self._has_failed = state in ERROR_STATES

    def _set_is_pending(self):
        # todo maybe the is_failed status should be cleared here?
        # if is it possible to re-launch a failed operation?
        self._is_over.clear()

    @property
    def is_pending(self):
        """
        Boolean indicating the object is still in creation.
        Becomes False once it is either successful or has failed.

        See Also:
            - :meth:`~wait`
            - :attr:`~is_ready`
            - :attr:`~has_failed`
        """
        return not self._is_over.is_set()

    def _set_has_failed(self):
        self._has_failed = True
        self._set_is_over()

    @property
    def has_failed(self):
        """
        Boolean indicating if the creation of the object failed.

        See Also:
            - :attr:`~failure_reason`
            - :meth:`~wait`
            - :attr:`~is_ready`
            - :attr:`~is_pending`
        """
        return self._has_failed

    @property
    def is_ready(self):
        """
        Boolean indicating if the object is finished creating without error.

        See Also:
            - :meth:`~wait`
            - :attr:`~is_pending`
            - :attr:`~has_failed`
        """
        return not self.is_pending and not self.has_failed

    @property
    def failure_reason(self):
        """
        Optional message that can detail the causes of the failure
        of the creation of the object.

        See Also:
            - :attr:`~has_failed`
        """
        return self.fields.get("error")

    @property
    def _failure_message(self):
        reason_str = f": {self.fields['error']}" if self.failure_reason else ""
        return f"{self._classname} id {self.id} failed {reason_str}"

    def _set_is_over(self):
        """
        Sets the object as idle, that is without loading,
        (either because loading finished or failed),
        meaning a wait() will return immediately.
        """
        self._is_over.set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all jobs concerning the object to either finish
        or fail.

        Args:
            timeout: maximum amount of time to wait in seconds (defaults to unlimited)

        Returns:
            True if the computation is over. False if the operation timed out.
        """
        is_done = self._is_over.wait(timeout)
        if self.has_failed:
            raise ProcessingError(self._failure_message)
        return is_done

    def _unregister(self):
        self._directory._unregister_item(self)

    def _handle_job_sse_event(self, data):
        """Update object with the information and state received through the SSE"""
        logger.debug(f"Handling SSE job event for {self._classname} id {self.id}")
        self.fields = data["record"]
        state: str = data["record"]["state"]
        if state in PENDING_STATES:
            logger.debug(f"{self._classname} id {self.id} set status pending")
            self._set_is_pending()
        elif state == "successful":
            logger.debug(f"{self._classname} id {self.id} set status successful")
            self._set_is_over()
        elif state in ERROR_STATES:
            reason_str = f"with reason {self.fields.get('error')}"
            logger.debug(f"{self._classname} id {self.id} set status failed {reason_str}")
            self._set_has_failed()
            logger.error(self.fields.get("error"))


DataModelType = TypeVar("DataModelType", bound=DataModel)


class Directory(ABC, Generic[DataModelType]):
    @classmethod
    @property
    @abstractmethod
    def _data_model(cls) -> Type[DataModel]:
        pass

    def __init__(self, client: "ansys.simai.core.client.SimAIClient"):
        self._client = client

        # Registry for known objects of this type that have been created
        # locally. It is used to ensure only 1 instance of a particular class
        # exists with a given id.
        # Note that this dictionary must retain all models created locally
        # without relying on the user to keep a reference on them
        # (meaning e.g. WeakValueDictionary is not appropriate),
        # as he will expect simai.wait() to work on any object, even those
        # with no explicit reference.
        self._registry: Dict[str, DataModel] = dict()

    @abstractmethod
    def get(self, id: str) -> DataModel:
        pass

    def _model_from(
        self, data: dict, data_model: Optional[DataModel] = None, **kwargs
    ) -> DataModel:
        # _model_from overrides object data (fields),
        # thus it is, and should, only be called with
        # complete data from the server, i.e. from a GET request.
        if "id" not in data:
            raise ValueError("Cannot instantiate data object without an id")
        item_id = data["id"]
        if item_id in self._registry:
            # An instance with this id already exists: update and return it,
            # so we don't have two objects with different data
            item = self._registry[item_id]
            # update with new data
            item.fields = data
        else:
            constructor = data_model if data_model else self._data_model
            # item was unknown: create it and save it to the registry
            item = constructor(self._client, self, data, **kwargs)
            self._registry[item_id] = item
        return item

    def _unregister_item(self, item: DataModel):
        """
        Removes the item from the internal registry,
            mainly after a deletion.
        """
        self._unregister_item_with_id(item.id)

    def _unregister_item_with_id(self, item_id: str):
        """
        Removes the item from the internal registry,
            mainly after a deletion.
        """
        item = self._registry.pop(item_id, None)
        if item is not None:
            if isinstance(item, ComputableDataModel):
                item._set_is_over()

    def _handle_sse_event(self, data):
        item_id: str = data["target"]["id"]
        if item_id not in self._registry:
            # We ignore object whose id is unknown:
            # we only listen to objects that have been
            # created by a local operation
            logger.debug(f"Ignoring event for unknown object id {item_id}")
            return
        item = self._registry[item_id]

        if data["type"] == "job" and isinstance(item, ComputableDataModel):
            item._handle_job_sse_event(data)
        elif data["type"] == "resource" and isinstance(item, UploadableResourceMixin):
            item._handle_resource_sse_event(data)
        else:
            logger.error("Received a server update that could not be interpreted")

    def _all_objects(self):
        return self._registry.values()


class UploadableResourceMixin:
    """Class used to expand DataModel with support for resource type message from SSE"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_upload_complete = Event()
        if kwargs.get("is_upload_complete", True):
            self._is_upload_complete.set()

    def _wait_for_upload_completion(self):
        self._is_upload_complete.wait()

    def _handle_resource_sse_event(self, data):
        state = data["status"]
        if state == "created":
            self._is_upload_complete.set()
        elif state == "upload_failed":
            self._is_upload_complete.set()
            ProcessingError(
                f"Could not complete upload because: {data.get('reason', 'Upload failed')}"
            )
        else:
            logger.error("Invalid resource state")
