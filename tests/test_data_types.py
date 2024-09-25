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

import pathlib
from io import BytesIO

import pytest

from ansys.simai.core.data.base import DataModel, Directory
from ansys.simai.core.data.types import (
    Range,
    are_boundary_conditions_equal,
    build_boundary_conditions,
    get_id_from_identifiable,
    get_object_from_identifiable,
    is_boundary_conditions,
    to_raw_filters,
    unpack_named_file,
)


def test_build_boundary_conditions(mocker):
    is_bc = mocker.patch("ansys.simai.core.data.types.is_boundary_conditions")
    is_bc.return_value = True
    assert build_boundary_conditions({"Vx": 10.1}) == {"Vx": 10.1}
    assert build_boundary_conditions({"Vx": 10, "Vy": 2}) == {"Vx": 10, "Vy": 2}
    assert build_boundary_conditions({"Vx": 10}, Vy=2) == {"Vx": 10, "Vy": 2}
    assert build_boundary_conditions(Vx=10, Vy=2) == {"Vx": 10, "Vy": 2}
    assert build_boundary_conditions() == {}
    assert build_boundary_conditions(boundary_conditions={}) == {}

    is_bc.return_value = False
    with pytest.raises(ValueError):
        build_boundary_conditions({"Vx": 10})


def test_basic_range():
    epsilon = 10**-7
    a_range = Range(10, 30)
    assert not a_range.match_value(-(10**8))
    assert not a_range.match_value(-30)
    assert not a_range.match_value(0)
    assert not a_range.match_value(10**-6)

    assert not a_range.match_value(a_range.min - 20 * epsilon)
    assert a_range.match_value(a_range.min - epsilon)
    assert a_range.match_value(a_range.min)
    assert a_range.match_value(a_range.min + epsilon)
    assert a_range.match_value(a_range.min + 20 * epsilon)

    assert a_range.match_value(20)

    assert a_range.match_value(a_range.max - 20 * epsilon)
    assert a_range.match_value(a_range.max - epsilon)
    assert a_range.match_value(a_range.max)
    assert a_range.match_value(a_range.max + epsilon)
    assert not a_range.match_value(a_range.max + 20 * epsilon)

    assert not a_range.match_value(40)
    assert not a_range.match_value(10**8)
    assert not a_range.match_value("toto")


def test_min_only_range():
    epsilon = 10**-7
    a_range = Range(min=10)
    assert not a_range.match_value(-(10**8))
    assert not a_range.match_value(-30)
    assert not a_range.match_value(0)
    assert not a_range.match_value(10**-6)

    assert not a_range.match_value(a_range.min - 20 * epsilon)
    assert a_range.match_value(a_range.min - epsilon)
    assert a_range.match_value(a_range.min)
    assert a_range.match_value(a_range.min + epsilon)
    assert a_range.match_value(a_range.min + 20 * epsilon)

    assert a_range.match_value(20)
    assert a_range.match_value(30)
    assert a_range.match_value(40)
    assert a_range.match_value(10**8)


def test_max_only_range():
    epsilon = 10**-7
    a_range = Range(max=30)
    assert a_range.match_value(-(10**8))
    assert a_range.match_value(-30)
    assert a_range.match_value(0)
    assert a_range.match_value(10**-6)
    assert a_range.match_value(10)
    assert a_range.match_value(20)

    assert a_range.match_value(a_range.max - 20 * epsilon)
    assert a_range.match_value(a_range.max - epsilon)
    assert a_range.match_value(a_range.max)
    assert a_range.match_value(a_range.max + epsilon)
    assert not a_range.match_value(a_range.max + 20 * epsilon)

    assert not a_range.match_value(40)
    assert not a_range.match_value(10**8)


def test_boundary_condition_identity():
    assert is_boundary_conditions({"Vx": 10})
    assert is_boundary_conditions({"Vx": 10, "Vy": 0, "Vz": 0})
    assert not is_boundary_conditions({"Vx": "beep"})
    assert not is_boundary_conditions({"Vx": 10, "Vy": "boop"})
    assert not is_boundary_conditions([0])
    assert not is_boundary_conditions((0))


def test_boundary_condition_equality():
    assert are_boundary_conditions_equal({"Vx": 10}, {"Vx": 10})
    assert are_boundary_conditions_equal({"Vx": 10, "Vy": 0}, {"Vx": 10, "Vy": 0})
    assert are_boundary_conditions_equal({"Vy": 0, "Vx": 10}, {"Vx": 10, "Vy": 0})
    assert are_boundary_conditions_equal({"Vx": 10**-7}, {"Vx": 0})
    assert not are_boundary_conditions_equal({"Vx": 10**-7}, {"Vx": 0}, tolerance=10**-8)


def test_boundary_condition_equality_wrong_parameters():
    with pytest.raises(TypeError):
        are_boundary_conditions_equal({"Vx": 10}, "toto")
    with pytest.raises(TypeError):
        are_boundary_conditions_equal("buz", {"Vx": 10})
    with pytest.raises(ValueError):
        are_boundary_conditions_equal({"Vx": 10}, {"Vx": 10}, tolerance=-5)


def test_unpack_named_file(mocker):
    open_file = mocker.patch("ansys.simai.core.data.types.file_path_to_obj_file")
    fake_file = mocker.MagicMock()
    open_file.return_value = fake_file

    with unpack_named_file("test.stl") as (file, name, extension):
        assert file == fake_file
        assert name == "test"
        assert extension == "stl"
        open_file.assert_called_once()
    fake_file.close.assert_called_once()
    open_file.reset_mock()
    fake_file.reset_mock()

    with unpack_named_file(pathlib.Path("test.stl")) as (file, name, extension):
        assert file == fake_file
        assert name == "test"
        assert extension == "stl"
        open_file.assert_called_once()
    fake_file.close.assert_called_once()
    open_file.reset_mock()
    fake_file.reset_mock()

    with unpack_named_file(("test.stl", "override.cgns")) as (file, name, extension):
        assert file == fake_file
        assert name == "override"
        assert extension == "cgns"
        open_file.assert_called_once()
    fake_file.close.assert_called_once()
    open_file.reset_mock()
    fake_file.reset_mock()

    binary_file_obj = BytesIO(b"blah")
    with unpack_named_file((binary_file_obj, "test.stl")) as (file, name, extension):
        assert file == binary_file_obj
        assert name == "test"
        assert extension == "stl"
        open_file.assert_not_called()
    fake_file.close.assert_not_called()
    open_file.reset_mock()
    fake_file.reset_mock()

    with unpack_named_file(("f.zip.stl", "¹³³⁷/ᵤₛₑᵣ-aₚᵢ\\n-..cgns")) as (
        file,
        name,
        extension,
    ):
        assert file == fake_file
        assert name == "¹³³⁷/ᵤₛₑᵣ-aₚᵢ\\n-."
        assert extension == "cgns"
        open_file.assert_called_once()
    fake_file.close.assert_called_once()


def test_get_id_from_identifiable():
    class MyTestModel(DataModel):
        pass

    test_model = MyTestModel(None, None, {"id": "yo"})

    assert get_id_from_identifiable(test_model) == "yo"
    assert get_id_from_identifiable("yo") == "yo"


def test_get_object_from_identifiable():
    class MyTestModel(DataModel):
        pass

    test_model = MyTestModel(None, None, {"id": "yo"})

    class MyTestDirectory(Directory):
        _data_model = MyTestModel

        def get(self, id: str):
            if id == "yo":
                return test_model
            else:
                raise ValueError

    directory = MyTestDirectory(client=None)

    assert get_object_from_identifiable(test_model, directory) == test_model
    assert get_object_from_identifiable("yo", directory) == test_model


@pytest.mark.parametrize(
    ("filters", "expected_raw_filters"),
    [
        (
            {"name": "paul", "production_capacity": "6e34Kg"},
            [
                {"field": "name", "operator": "EQ", "value": "paul"},
                {"field": "production_capacity", "operator": "EQ", "value": "6e34Kg"},
            ],
        ),
        (
            [("name", "EQ", "paul"), ("production_capacity", "GTE", 10**10)],
            [
                {"field": "name", "operator": "EQ", "value": "paul"},
                {"field": "production_capacity", "operator": "GTE", "value": 10**10},
            ],
        ),
        (
            [{"field": "nofield", "operator": "GTE", "value": 9000}],
            [{"field": "nofield", "operator": "GTE", "value": 9000}],
        ),
    ],
    ids=["simple_filters", "complex_filters", "raw_filters"],
)
def test_to_raw_filters(filters, expected_raw_filters):
    filters = to_raw_filters(filters)
    assert filters == expected_raw_filters
