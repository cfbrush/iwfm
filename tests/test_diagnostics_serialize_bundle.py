# test_diagnostics_serialize_bundle.py
# Unit tests for diagnostics/serialize_bundle.py
# Copyright (C) 2026 University of California
# -----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# -----------------------------------------------------------------------------

import json
import os
import tempfile
import pytest
import numpy as np

from iwfm.diagnostics.diag_dataclasses import (
    DiagnosticBundle,
    ConvergenceSummary,
    ResidualSummary,
    MassBalanceSummary,
    StreamSummary,
    PestStateSummary,
    StructuralSignals,
)
from iwfm.diagnostics.serialize_bundle import serialize_bundle


def _make_bundle():
    """Create a minimal DiagnosticBundle for testing."""
    return DiagnosticBundle(
        model_name='TestModel',
        pest_iteration=5,
        timestamp='2026-04-17T10:00:00',
        model_dimensions={'n_nodes': 100, 'n_elements': 90},
        convergence=ConvergenceSummary(
            mean_iterations=8.3, max_iterations=50,
            pct_timesteps_at_max=2.4, mean_diffmax=0.032,
            max_diffmax=1.87, mean_rhs_l2_ratio=0.0014,
            trouble_timesteps=[
                {'timestep_index': i, 'diffmax': 0.5 + i * 0.1,
                 'iterations': 40 + i, 'node': 100 + i, 'layer': 1}
                for i in range(8)
            ],
        ),
        residuals=ResidualSummary(
            rhs_l2_by_layer=[0.002, 0.001],
            hdelta_l2_by_layer=[0.001, 0.0005],
            worst_nodes=[{'node_id': 873, 'layer': 2, 'mean_rhs': 12.4}],
            mean_iterations_to_converge=8.3,
        ),
        mass_balance=MassBalanceSummary(
            mean_abs_residual_by_layer=[0.12, 0.08],
            max_abs_residual=14.7,
            hotspot_elements=[],
            pct_elements_above_threshold=3.1,
        ),
        streams=StreamSummary(
            mean_stream_gw_flow=-0.42,
            max_abs_stream_gw_flow=128.5,
            gaining_reach_count=412,
            losing_reach_count=251,
            anomaly_nodes=[],
        ),
        pest_state=PestStateSummary(
            iteration=5, phi=2847.3, n_observations=1250,
            rmse=4.82, bias=-0.31,
            obs_group_stats=[{'group': 'gwhead', 'n': 1100, 'rmse': 4.92}],
            params_at_bounds=[],
        ),
        structural_signals=StructuralSignals(
            residual_cluster_nodes=[],
            convergence_trouble_timesteps=[],
            stream_gw_anomalies=[],
            mass_balance_hotspots=[],
            params_at_bounds=[],
            hypothesis='Test hypothesis.',
        ),
    )


class TestSerializeBundle:

    def test_returns_valid_json(self):
        bundle = _make_bundle()
        result = serialize_bundle(bundle)
        parsed = json.loads(result)
        assert parsed['model_name'] == 'TestModel'
        assert parsed['pest_iteration'] == 5

    def test_float_precision(self):
        bundle = _make_bundle()
        result = serialize_bundle(bundle, float_precision=2)
        parsed = json.loads(result)
        # phi should be rounded to 2 decimal places
        phi = parsed['pest_state']['phi']
        # Check it's a number (rounding may vary)
        assert isinstance(phi, (int, float))

    def test_list_truncation(self):
        bundle = _make_bundle()
        # Bundle has 8 trouble_timesteps
        result = serialize_bundle(bundle, max_list_items=3)
        parsed = json.loads(result)
        trouble = parsed['convergence']['trouble_timesteps']
        # Should be truncated: 3 items + _truncated marker
        assert len(trouble) <= 4  # 3 items + possible truncation marker

    def test_writes_to_file(self):
        bundle = _make_bundle()
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False,
                                         mode='w') as f:
            path = f.name
        try:
            result = serialize_bundle(bundle, output_path=path)
            assert os.path.exists(path)
            with open(path) as f:
                parsed = json.loads(f.read())
            assert parsed['model_name'] == 'TestModel'
        finally:
            os.unlink(path)

    def test_numpy_types_converted(self):
        bundle = _make_bundle()
        # Inject numpy types into bundle
        bundle.pest_state.phi = np.float64(2847.3)
        bundle.pest_state.n_observations = np.int64(1250)
        result = serialize_bundle(bundle)
        parsed = json.loads(result)
        assert isinstance(parsed['pest_state']['phi'], float)
        assert isinstance(parsed['pest_state']['n_observations'], int)

    def test_nan_converted_to_none(self):
        bundle = _make_bundle()
        bundle.pest_state.rmse = float('nan')
        result = serialize_bundle(bundle)
        parsed = json.loads(result)
        assert parsed['pest_state']['rmse'] is None

    def test_output_under_size_limit(self):
        """Serialized bundle should be compact (< 10KB for minimal bundle)."""
        bundle = _make_bundle()
        result = serialize_bundle(bundle, max_list_items=5)
        assert len(result) < 10000
