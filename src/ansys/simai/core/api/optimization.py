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

from typing import Dict

from ansys.simai.core.api.mixin import ApiClientMixin


class OptimizationClientMixin(ApiClientMixin):
    def define_optimization(self, workspace_id: str, optimization_parameters: Dict):
        return self._post(f"workspaces/{workspace_id}/optimizations", json=optimization_parameters)

    def run_optimization_trial(self, optimization_id: str, parameters: Dict):
        return self._post(
            f"optimizations/{optimization_id}/trial-runs",
            json=parameters,
        )

    def get_optimization(self, optimization_id: str):
        return self._get(f"optimizations/{optimization_id}")

    def get_optimization_trial_run(self, trial_run_id: str):
        return self._get(f"optimizations/trial-runs/{trial_run_id}")
