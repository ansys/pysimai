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


import pytest

from ansys.simai.core.data.optimizations import _check_geometry_generation_fn_signature
from ansys.simai.core.errors import InvalidArguments


def test_geometry_generation_fn_invalid_signature(simai_client):
    """WHEN a geometry_generation_fn signature does not match geometry_parameters keys
    THEN an InvalidArgument error is raised."""

    def my_geometry_generation_function(param_a):
        return "test_geometry/param_{param_a}.vtp"

    geometry_parameters = {
        "param_a": {"bounds": (-12.5, 12.5)},
        "param_ski": {"choices": (0.1, 1.0)},
    }

    with pytest.raises(InvalidArguments) as exc:
        simai_client.optimizations.run(
            geometry_generation_fn=my_geometry_generation_function,
            geometry_parameters=geometry_parameters,
            boundary_conditions={"abc": 3.0},
            n_iters=5,
        )

    assert "geometry_generation_fn requires the following signature" in str(exc.value)


def test_check_geometry_generation_fn_valid_signature():
    """WHEN geometry_generation_fn signature matches geometry_parameters keys
    THEN check passes"""

    def my_geometry_generation_function(param_c, param_d):
        return "test_geometry/param_{param_c}_{param_d}.vtp"

    geometry_parameters = {"param_c": {"bounds": (-12.5, 12.5)}, "param_d": {"choices": (0.1, 1.0)}}

    _check_geometry_generation_fn_signature(my_geometry_generation_function, geometry_parameters)
