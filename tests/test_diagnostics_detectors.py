# test_diagnostics_detectors.py
# Unit tests for diagnostics signal detectors
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

import pytest
import numpy as np

from iwfm.diagnostics.diag_dataclasses import (
    ConvergenceSummary,
    MassBalanceSummary,
    PestStateSummary,
    ResidualSummary,
    StreamSummary,
)
from iwfm.diagnostics.detect_convergence_trouble import detect_convergence_trouble
from iwfm.diagnostics.detect_mass_balance_hotspots import detect_mass_balance_hotspots
from iwfm.diagnostics.detect_params_at_bounds import detect_params_at_bounds
from iwfm.diagnostics.detect_residual_clusters import detect_residual_clusters
from iwfm.diagnostics.detect_stream_gw_anomalies import detect_stream_gw_anomalies


# =========================================================================
# detect_convergence_trouble
# =========================================================================

class TestDetectConvergenceTrouble:

    def test_empty_trouble_timesteps(self):
        conv = ConvergenceSummary(
            mean_iterations=5.0, max_iterations=10,
            pct_timesteps_at_max=0.0, mean_diffmax=0.001,
            max_diffmax=0.01, mean_rhs_l2_ratio=0.001,
            trouble_timesteps=[],
        )
        result = detect_convergence_trouble(conv)
        assert result == []

    def test_filters_by_iter_threshold(self):
        conv = ConvergenceSummary(
            mean_iterations=8.0, max_iterations=50,
            pct_timesteps_at_max=2.0, mean_diffmax=0.01,
            max_diffmax=0.5, mean_rhs_l2_ratio=0.001,
            trouble_timesteps=[
                {'timestep_index': 10, 'diffmax': 0.001,
                 'iterations': 50, 'node': 100, 'layer': 1},
                {'timestep_index': 20, 'diffmax': 0.001,
                 'iterations': 5, 'node': 200, 'layer': 2},
            ],
        )
        result = detect_convergence_trouble(conv, iter_threshold=40,
                                            diffmax_threshold=0.1)
        assert len(result) == 1
        assert result[0]['timestep_index'] == 10

    def test_filters_by_diffmax_threshold(self):
        conv = ConvergenceSummary(
            mean_iterations=5.0, max_iterations=10,
            pct_timesteps_at_max=0.0, mean_diffmax=0.01,
            max_diffmax=1.0, mean_rhs_l2_ratio=0.001,
            trouble_timesteps=[
                {'timestep_index': 5, 'diffmax': 1.5,
                 'iterations': 8, 'node': 50, 'layer': 3},
            ],
        )
        result = detect_convergence_trouble(conv, iter_threshold=40,
                                            diffmax_threshold=0.1)
        assert len(result) == 1
        assert result[0]['diffmax'] == 1.5


# =========================================================================
# detect_mass_balance_hotspots
# =========================================================================

class TestDetectMassBalanceHotspots:

    def test_empty_hotspots(self):
        mb = MassBalanceSummary(
            mean_abs_residual_by_layer=[0.1, 0.05],
            max_abs_residual=0.2,
            hotspot_elements=[],
            pct_elements_above_threshold=0.0,
        )
        result = detect_mass_balance_hotspots(mb)
        assert result == []

    def test_flags_high_ratio_elements(self):
        mb = MassBalanceSummary(
            mean_abs_residual_by_layer=[0.1, 0.05, 0.2, 0.01],
            max_abs_residual=15.0,
            hotspot_elements=[
                {'element_id': 445, 'layer': 2, 'mean_abs_residual': 8.0,
                 'max_abs_residual': 15.0},
                {'element_id': 100, 'layer': 1, 'mean_abs_residual': 0.2,
                 'max_abs_residual': 0.3},
            ],
            pct_elements_above_threshold=3.0,
        )
        # layer 2 mean = 0.2, element 445 = 8.0 → ratio = 40.0 (>= 5.0)
        # layer 0 mean = 0.1, element 100 = 0.2 → ratio = 2.0 (< 5.0)
        result = detect_mass_balance_hotspots(mb, threshold_multiplier=5.0)
        flagged_ids = [r['element_id'] for r in result]
        assert 445 in flagged_ids
        assert 100 not in flagged_ids


# =========================================================================
# detect_params_at_bounds
# =========================================================================

class TestDetectParamsAtBounds:

    def test_no_params_at_bounds(self):
        pest = PestStateSummary(
            iteration=1, phi=1000.0, n_observations=500,
            rmse=5.0, bias=-0.1,
            obs_group_stats=[],
            params_at_bounds=[
                {'name': 'PKH001', 'value': 5.0, 'lower': 0.1,
                 'upper': 10.0, 'pct_of_range': 0.50},
            ],
        )
        result = detect_params_at_bounds(pest, bound_pct_threshold=0.05)
        assert result == []

    def test_param_at_lower_bound(self):
        pest = PestStateSummary(
            iteration=1, phi=1000.0, n_observations=500,
            rmse=5.0, bias=0.0,
            obs_group_stats=[],
            params_at_bounds=[
                {'name': 'PKH001', 'value': 0.11, 'lower': 0.1,
                 'upper': 10.0, 'pct_of_range': 0.001},
            ],
        )
        result = detect_params_at_bounds(pest, bound_pct_threshold=0.05)
        assert len(result) == 1
        assert result[0]['name'] == 'PKH001'
        assert result[0]['bound'] == 'lower'

    def test_param_at_upper_bound(self):
        pest = PestStateSummary(
            iteration=1, phi=1000.0, n_observations=500,
            rmse=5.0, bias=0.0,
            obs_group_stats=[],
            params_at_bounds=[
                {'name': 'PKH002', 'value': 9.9, 'lower': 0.1,
                 'upper': 10.0, 'pct_of_range': 0.99},
            ],
        )
        result = detect_params_at_bounds(pest, bound_pct_threshold=0.05)
        assert len(result) == 1
        assert result[0]['bound'] == 'upper'

    def test_pct_of_range_none_skipped(self):
        pest = PestStateSummary(
            iteration=1, phi=1000.0, n_observations=500,
            rmse=5.0, bias=0.0,
            obs_group_stats=[],
            params_at_bounds=[
                {'name': 'PKH003', 'value': 1.0, 'lower': 0.1,
                 'upper': 10.0, 'pct_of_range': None},
            ],
        )
        result = detect_params_at_bounds(pest)
        assert result == []


# =========================================================================
# detect_residual_clusters
# =========================================================================

class TestDetectResidualClusters:

    def test_empty_worst_nodes(self):
        res = ResidualSummary(
            rhs_l2_by_layer=[0.001],
            hdelta_l2_by_layer=[0.0005],
            worst_nodes=[],
            mean_iterations_to_converge=8.0,
        )
        result = detect_residual_clusters(res)
        assert result == []

    def test_z_score_flagging(self):
        # 9 nodes with mean_rhs ~1.0, one outlier at 20.0
        worst = [{'node_id': i, 'layer': 1, 'mean_rhs': 1.0,
                  'mean_hdelta': 0.01} for i in range(1, 10)]
        worst.append({'node_id': 99, 'layer': 1, 'mean_rhs': 20.0,
                      'mean_hdelta': 0.5})
        res = ResidualSummary(
            rhs_l2_by_layer=[0.01],
            hdelta_l2_by_layer=[0.005],
            worst_nodes=worst,
            mean_iterations_to_converge=8.0,
        )
        result = detect_residual_clusters(res, z_threshold=2.0)
        flagged_ids = [r['node_id'] for r in result]
        assert 99 in flagged_ids

    def test_spatial_clustering(self):
        # Need enough low-residual nodes to make outliers stand out
        worst = [{'node_id': i, 'layer': 1, 'mean_rhs': 1.0,
                  'mean_hdelta': 0.01} for i in range(1, 9)]
        # Two outlier nodes that are spatially close (both well above z=2)
        worst.append({'node_id': 9, 'layer': 1, 'mean_rhs': 80.0,
                      'mean_hdelta': 0.5})
        worst.append({'node_id': 10, 'layer': 1, 'mean_rhs': 75.0,
                      'mean_hdelta': 0.4})
        res = ResidualSummary(
            rhs_l2_by_layer=[0.01],
            hdelta_l2_by_layer=[0.005],
            worst_nodes=worst,
            mean_iterations_to_converge=8.0,
        )
        # node_coords as list (0-indexed); nodes 9 and 10 close together
        coords = [(i * 1000.0, 0.0) for i in range(11)]
        result = detect_residual_clusters(res, node_coords=coords,
                                          z_threshold=1.5)
        flagged_ids = [r['node_id'] for r in result]
        assert 9 in flagged_ids
        assert 10 in flagged_ids
        # Spatial clustering should assign same cluster_id
        if len(result) >= 2:
            clusters = {r['node_id']: r.get('cluster_id') for r in result}
            assert clusters[9] == clusters[10]


# =========================================================================
# detect_stream_gw_anomalies
# =========================================================================

class TestDetectStreamGwAnomalies:

    def test_empty_anomalies(self):
        stream = StreamSummary(
            mean_stream_gw_flow=-0.5,
            max_abs_stream_gw_flow=50.0,
            gaining_reach_count=300,
            losing_reach_count=200,
            anomaly_nodes=[],
        )
        result = detect_stream_gw_anomalies(stream)
        assert result == []

    def test_filters_by_z_threshold(self):
        stream = StreamSummary(
            mean_stream_gw_flow=-0.5,
            max_abs_stream_gw_flow=128.0,
            gaining_reach_count=400,
            losing_reach_count=250,
            anomaly_nodes=[
                {'node_id': 88, 'mean_strmgw': -45.0,
                 'std_strmgw': 82.0, 'z_score': 5.2,
                 'flag': 'high_variance'},
                {'node_id': 200, 'mean_strmgw': -2.0,
                 'std_strmgw': 1.0, 'z_score': 1.5,
                 'flag': 'normal'},
            ],
        )
        result = detect_stream_gw_anomalies(stream, z_threshold=3.0)
        assert len(result) == 1
        assert result[0]['node_id'] == 88
