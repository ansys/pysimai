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

import io
import os
import pathlib
from contextlib import contextmanager
from numbers import Number
from typing import Any, BinaryIO, Callable, Dict, Generator, List, Optional, Tuple, Union

from requests import Response

from ansys.simai.core.data.base import DataModel, DataModelType, Directory
from ansys.simai.core.errors import InvalidArguments
from ansys.simai.core.utils.files import file_path_to_obj_file
from ansys.simai.core.utils.numerical import (
    is_bigger_or_equal_with_tolerance,
    is_equal_with_tolerance,
    is_number,
    is_smaller_or_equal_with_tolerance,
    validate_tolerance_parameter,
)

BoundaryConditions = Dict[str, Number]
"""
:obj:`BoundaryConditions` describes the external conditions of a prediction.
"""

Path = Union[pathlib.Path, str, os.PathLike]
"""
Path to a file or folder as an :obj:`pathlib.Path` object or a format supported by ``pathlib``.
"""

File = Union[BinaryIO, io.RawIOBase, io.BufferedIOBase, Path]
"""
Either a binary file-object (:obj:`typing.BinaryIO`) or a :obj:`Path`.
"""

NamedFile = Union[Path, Tuple[File, str]]
"""
A named file is either a ``FilePath``, from which a name can be inferred, or a tuple with a file and a name.
To be valid, the name needs to contain an extension.

Example:
    .. code-block:: python

        file = "/path/to/my/file.stl"  # The file is named file.stl
        file = ("/path/to/my/file.stl", "override.stl")  # The file is named override.stl
        file = (io.BinaryIO(my_data), "file.stl")  # The file is named file.stl

        invalid_file = io.BinaryIO(my_data)  # Cannot infer name from binaryIO
        invalid_file = "/path/to/my/file"  # Inferred name has no extension
        invalid_file = ("/path/to/my/file.stl", "override")  # Specified name has no extension
"""


APIResponse = Union[Response, Dict[str, Any], List[Dict[str, Any]]]

MonitorCallback = Callable[[int], None]
"""Callback used to monitor the download or upload of a file.

For downloads, the callback is called one time with the total size of the download.
Subsequent calls are passed the number of bytes read in this iteration.

For uploads, the callback receives the number of bytes written each iteration.
"""

Identifiable = Union[DataModelType, str]
"""Either a model or the string ID of an object of the same type."""


def build_boundary_conditions(boundary_conditions: Optional[Dict[str, Number]] = None, **kwargs):
    bc = boundary_conditions if boundary_conditions else {}
    bc.update(**kwargs)
    if bc is None:
        raise ValueError("No boundary condition was specified.")
    if not is_boundary_conditions(bc):
        raise ValueError("Boundary conditions must be in a dictionary with numbers as values.")
    return bc


def is_boundary_conditions(bc):
    return isinstance(bc, dict) and all(is_number(x) for x in bc.values())


def are_boundary_conditions_equal(
    left: BoundaryConditions,
    right: BoundaryConditions,
    tolerance: Optional[Number] = None,
):
    if not is_boundary_conditions(left):
        raise TypeError(
            f"is_boundary_conditions_equal called with incorrect left parameter (received {left})"
        )
    if not is_boundary_conditions(right):
        raise TypeError(
            f"is_boundary_conditions_equal called with incorrect right parameter (received {right})"
        )
    validate_tolerance_parameter(tolerance)
    if left.keys() != right.keys():
        return False
    for key in left.keys():  # noqa: SIM118
        if not is_equal_with_tolerance(left[key], right[key], tolerance=tolerance):
            return False
    return True


class Range:
    """Describes a numerical range used for filtering geometries.

    Range objects describe a numerical range between a minimum and
    a maximum boundary. Both are optional. Thus, if no maximum boundary
    is passed, the range describes values greater than or equal to the
    minimum boundary. Note that ranges are inclusive. Thus, both minimum
    and maximum boundaries match if they are equal to the passed value
    (as opposed to Python's ``range()`` method).

    Ranges can be used as a filter in the
    :func:`geometries.list<ansys.simai.core.data.geometries.GeometryDirectory.list>` method.

    Args:
        min: Minimum boundary.
        max: Maximum boundary.
        tolerance: Tolerance delta. Two values whose difference is smaller
            than the tolerance are considered as equal.
    """

    def __init__(
        self,
        min: Optional[float] = None,
        max: Optional[float] = None,
        tolerance: Optional[float] = None,
    ):
        self.min = min
        self.max = max
        self.tolerance = tolerance

    def match_value(self, value: float) -> bool:
        """Determine whether the given value belongs to the :class:`Range` class."""
        if not is_number(value):
            return False
        # if min, value >= min
        if self.min is not None and not is_bigger_or_equal_with_tolerance(
            value, self.min, tolerance=self.tolerance
        ):
            return False
        # if max, value <= max
        if self.max is not None and not is_smaller_or_equal_with_tolerance(
            value, self.max, tolerance=self.tolerance
        ):
            return False
        return True


class _HollowRange(Range):
    """_HollowRange is a range that excludes a value in its center."""

    def __init__(
        self,
        min: Optional[float] = None,
        max: Optional[float] = None,
        tolerance: Optional[float] = None,
        excluded_value: Optional[float] = None,
    ):
        super().__init__(min=min, max=max, tolerance=tolerance)
        self.excluded_value = excluded_value

    def match_value(self, value: float):
        if not super().match_value(value):
            return False
        if self.excluded_value is not None and is_equal_with_tolerance(
            value, self.excluded_value, tolerance=self.tolerance
        ):
            return False
        return True


@contextmanager
def unpack_named_file(
    named_file: NamedFile,
) -> Generator[Tuple[BinaryIO, str, str], None, None]:
    """Unpack a named file by providing a readable file, its name, and an extension."""
    if (
        isinstance(named_file, Tuple)
        and len(named_file) == 2
        # == isinstance(named_file, File) on python >=3.10
        and isinstance(named_file[0], File.__args__)
    ):
        file = named_file[0]
        filename = named_file[1]
    # == isinstance(named_file, Path) on python >=3.10
    elif isinstance(named_file, Path.__args__):
        file = named_file
        filename = pathlib.Path(named_file).name
    else:
        raise InvalidArguments("Did not receive a valid named file type.")

    # Parse name and extension
    try:
        obj_name, file_ext = filename.rsplit(".", 1)
        assert file_ext
    except (ValueError, AssertionError):
        raise AttributeError(f"Could not determine file extension for {named_file}.") from None

    # Open the file if needed
    close_file = False
    if not isinstance(file, (io.RawIOBase, io.BufferedIOBase)):
        file = file_path_to_obj_file(file, "rb")
        close_file = True

    try:
        yield file, obj_name, file_ext
    finally:
        if close_file is True:
            file.close()


def get_id_from_identifiable(
    identifiable: Optional[Identifiable] = None,
    required: bool = True,
    default: Optional[Identifiable] = None,
) -> Optional[str]:
    if isinstance(identifiable, DataModel):
        return identifiable.id
    elif isinstance(identifiable, str):
        return identifiable
    elif default:
        return get_id_from_identifiable(default, required)
    elif required:
        raise InvalidArguments(f"Argument {identifiable} is neither a data model nor an ID string.")


def get_object_from_identifiable(
    identifiable: Optional[Identifiable],
    directory: Directory,
    default: Optional[Identifiable] = None,
) -> DataModel:
    if isinstance(identifiable, DataModel):
        return identifiable
    elif isinstance(identifiable, str):
        return directory.get(id=identifiable)
    elif default:
        return get_object_from_identifiable(default, directory)
    else:
        raise InvalidArguments(f"Argument {identifiable} is neither a data model nor an ID string.")
