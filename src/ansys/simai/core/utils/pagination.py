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

"""Helpers to handle paginated responses."""

import json
import logging
from typing import Any, Dict, Iterator, Sized, TypeVar

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.data.base import DataModel, Directory

logger = logging.getLogger(__name__)
M = TypeVar("M", bound=DataModel)


class PaginatedAPIRawIterator(Sized, Iterator[Dict[str, Any]]):
    """Iterator over a raw paginated response with a known length."""

    def __init__(self, client: ApiClientMixin, uri: str):
        self.client = client
        self._first_page = client._get(uri, return_json=False)
        try:
            x_pagination = self._first_page.headers["X-Pagination"]
            self.len = json.loads(x_pagination)["total"]
        except (KeyError, json.JSONDecodeError) as e:
            logger.warning(f"Could not fetch item count from pagination header: {e}")
            self.len = 0
        self.__it = self.__gen()

    def __gen(self):
        yield from self._first_page.json()
        next_page = self._first_page.links.get("next", {}).get("url")
        del self._first_page
        while next_page:
            page_request = self.client._get(next_page, return_json=False)
            next_page = page_request.links.get("next", {}).get("url")
            yield from page_request.json()

    def __next__(self) -> Dict[str, Any]:
        elem = next(self.__it)
        self.len -= 1
        return elem

    def __len__(self) -> int:
        return self.len


class DataModelIterator(Sized, Iterator[M]):
    """Iterator over paginated objects with a known length."""

    def __init__(self, raw: PaginatedAPIRawIterator, directory: Directory[M]):
        self.raw = raw
        self.directory = directory

    def __next__(self) -> M:
        entry = next(self.raw)
        return self.directory._model_from(entry)

    def __len__(self) -> int:
        return len(self.raw)
