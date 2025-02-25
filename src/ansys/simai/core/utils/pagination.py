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

from typing import Any, Dict, Iterable, Sized, TypeVar

from ansys.simai.core.api.mixin import ApiClientMixin
from ansys.simai.core.data.base import DataModel, Directory

M = TypeVar("M", bound=DataModel)


class APIRawIterable(Sized, Iterable[Dict[str, Any]]):
    """Iterable over a raw paginated response with a known length."""

    def __init__(self, client: ApiClientMixin, uri: str):
        self.client = client
        self._first_page = client._get(uri, return_json=False)
        self.len = self._first_page.headers.get("X-Pagination", {}).get("total", -1)

    def __iter__(self):
        yield from self._first_page.json()
        next_page = self._first_page.links.get("next", {}).get("url")
        del self._first_page
        while next_page:
            page_request = self.client._get(next_page, return_json=False)
            next_page = page_request.links.get("next", {}).get("url")
            yield from page_request.json()

    def __len__(self):
        return self.len


class DataModelIterable(Sized, Iterable[M]):
    """Iterable over paginated objects with a known length."""

    def __init__(self, raw: APIRawIterable, directory: Directory[M]):
        self.raw = raw
        self.directory = directory

    def __iter__(self):
        for entry in self.raw:
            yield self.directory._model_from(entry)

    def __len__(self):
        return self.raw.len()
