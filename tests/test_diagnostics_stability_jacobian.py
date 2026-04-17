# test_diagnostics_stability_jacobian.py
# Unit tests for diagnostics/stability_jacobian.py
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

import os
import tempfile
import pytest
import numpy as np

from iwfm.diagnostics.stability_jacobian import (
    ConvergenceMetrics,
    StabilityJacobian,
    read_convergence_quick,
    compute_stability_scores,
    StabilityCollector,
)


def _make_convergence_hdf(path, n_timesteps=10, mean_iter=8.0,
                          max_iter=50, max_diffmax=0.5):
    """Create a synthetic Diagnostics_Convergence.hdf for testing."""
    import h5py

    # Columns: node, compID, layer, DIFFMAX, DIFF_L2, ITERX, RHSL2ratio
    data = np.zeros((n_timesteps, 7))
    data[:, 5] = mean_iter  # ITERX
    data[:, 3] = 0.01       # DIFFMAX (small)
    # Make one timestep extreme
    data[0, 5] = max_iter
    data[0, 3] = max_diffmax

    with h5py.File(path, 'w') as f:
        f.create_dataset('/ConvergenceSummary', data=data)


class TestConvergenceMetrics:
    """Tests for ConvergenceMetrics dataclass."""

    def test_defaults(self):
        m = ConvergenceMetrics()
        assert m.max_iterations == 0
        assert m.mean_iterations == 0.0
        assert m.n_timesteps == 0

    def test_custom_values(self):
        m = ConvergenceMetrics(max_iterations=50, mean_iterations=8.3,
                               max_diffmax=1.87, n_trouble_timesteps=5,
                               n_timesteps=504)
        assert m.max_iterations == 50
        assert m.n_trouble_timesteps == 5


class TestReadConvergenceQuick:
    """Tests for read_convergence_quick."""

    def test_reads_hdf5(self):
        with tempfile.NamedTemporaryFile(suffix='.hdf', delete=False) as f:
            path = f.name
        try:
            _make_convergence_hdf(path, n_timesteps=20, mean_iter=10.0,
                                  max_iter=50, max_diffmax=0.5)
            metrics = read_convergence_quick(path, iter_threshold=40,
                                             diffmax_threshold=0.1)
            assert metrics.n_timesteps == 20
            assert metrics.max_iterations == 50
            assert metrics.max_diffmax == pytest.approx(0.5, abs=1e-6)
            # 1 timestep at iter=50 (>= 40) and diffmax=0.5 (>= 0.1)
            assert metrics.n_trouble_timesteps >= 1
        finally:
            os.unlink(path)

    def test_empty_data(self):
        import h5py
        with tempfile.NamedTemporaryFile(suffix='.hdf', delete=False) as f:
            path = f.name
        try:
            with h5py.File(path, 'w') as fh:
                fh.create_dataset('/ConvergenceSummary',
                                  data=np.empty((0, 7)))
            metrics = read_convergence_quick(path)
            assert metrics.n_timesteps == 0
            assert metrics.max_iterations == 0
        finally:
            os.unlink(path)

    def test_all_calm(self):
        """No trouble timesteps when all values below thresholds."""
        import h5py
        with tempfile.NamedTemporaryFile(suffix='.hdf', delete=False) as f:
            path = f.name
        try:
            data = np.zeros((100, 7))
            data[:, 5] = 5.0   # ITERX = 5 (well below 40)
            data[:, 3] = 0.001  # DIFFMAX = 0.001 (well below 0.1)
            with h5py.File(path, 'w') as fh:
                fh.create_dataset('/ConvergenceSummary', data=data)
            metrics = read_convergence_quick(path, iter_threshold=40,
                                             diffmax_threshold=0.1)
            assert metrics.n_trouble_timesteps == 0
            assert metrics.mean_iterations == pytest.approx(5.0)
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(Exception):
            read_convergence_quick('/nonexistent/path.hdf')


class TestComputeStabilityScores:
    """Tests for compute_stability_scores."""

    def test_empty_inputs(self):
        result = compute_stability_scores(None, [])
        assert result.n_params == 0
        assert result.n_destabilizing == 0
        assert result.top_destabilizers == []

    def test_no_perturb_data(self):
        base = ConvergenceMetrics(mean_iterations=8.0, max_iterations=20,
                                  max_diffmax=0.01, n_trouble_timesteps=2,
                                  n_timesteps=100)
        result = compute_stability_scores(base, [])
        assert result.n_params == 0

    def test_stable_perturbations(self):
        """Perturbations that don't worsen convergence get score=0."""
        base = ConvergenceMetrics(mean_iterations=10.0, max_iterations=50,
                                  max_diffmax=0.5, n_trouble_timesteps=10,
                                  n_timesteps=100)
        # Perturbation with same or better metrics
        pert = ConvergenceMetrics(mean_iterations=9.0, max_iterations=45,
                                  max_diffmax=0.3, n_trouble_timesteps=8,
                                  n_timesteps=100)
        perturb_data = [(0, 'PKH001_L1', pert)]
        result = compute_stability_scores(base, perturb_data)
        assert result.n_params == 1
        assert result.n_destabilizing == 0
        scores = result.param_scores
        assert scores[0]['stability_score'] == pytest.approx(0.0)

    def test_destabilizing_perturbation(self):
        """Perturbation that worsens convergence gets positive score."""
        base = ConvergenceMetrics(mean_iterations=8.0, max_iterations=20,
                                  max_diffmax=0.01, n_trouble_timesteps=2,
                                  n_timesteps=100)
        pert = ConvergenceMetrics(mean_iterations=25.0, max_iterations=50,
                                  max_diffmax=5.0, n_trouble_timesteps=30,
                                  n_timesteps=100)
        perturb_data = [(0, 'PKH_BAD', pert)]
        result = compute_stability_scores(base, perturb_data,
                                          score_threshold=0.01)
        assert result.n_params == 1
        assert result.n_destabilizing == 1
        assert result.param_scores[0]['stability_score'] > 0.1
        assert result.param_scores[0]['delta_mean_iter'] > 0

    def test_multiple_params_sorted(self):
        """Top destabilizers sorted by score descending."""
        base = ConvergenceMetrics(mean_iterations=8.0, max_iterations=20,
                                  max_diffmax=0.01, n_trouble_timesteps=2,
                                  n_timesteps=100)
        mild = ConvergenceMetrics(mean_iterations=10.0, max_iterations=22,
                                  max_diffmax=0.02, n_trouble_timesteps=4,
                                  n_timesteps=100)
        severe = ConvergenceMetrics(mean_iterations=30.0, max_iterations=50,
                                    max_diffmax=5.0, n_trouble_timesteps=40,
                                    n_timesteps=100)
        perturb_data = [
            (0, 'MILD_PARAM', mild),
            (1, 'SEVERE_PARAM', severe),
        ]
        result = compute_stability_scores(base, perturb_data)
        assert result.n_params == 2
        assert result.param_scores[0]['param_name'] == 'SEVERE_PARAM'
        assert (result.param_scores[0]['stability_score']
                >= result.param_scores[1]['stability_score'])

    def test_top_n_limits(self):
        base = ConvergenceMetrics(mean_iterations=8.0, max_iterations=20,
                                  max_diffmax=0.01, n_trouble_timesteps=2,
                                  n_timesteps=100)
        perturb_data = []
        for i in range(10):
            pert = ConvergenceMetrics(
                mean_iterations=8.0 + i, max_iterations=20 + i,
                max_diffmax=0.01 + i * 0.5, n_trouble_timesteps=2 + i * 3,
                n_timesteps=100)
            perturb_data.append((i, f'P{i:03d}', pert))
        result = compute_stability_scores(base, perturb_data, top_n=3)
        assert len(result.top_destabilizers) <= 3
        assert len(result.param_scores) == 10


class TestStabilityCollector:
    """Tests for StabilityCollector."""

    def test_initial_state(self):
        c = StabilityCollector()
        assert not c.has_base
        assert c.n_captured == 0

    def test_capture_base_missing_file(self):
        c = StabilityCollector(diagnostics_subdir='nonexistent')
        c.capture_base('/tmp')
        assert not c.has_base
        assert len(c._capture_errors) == 1

    def test_capture_base_and_perturbation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            diag_dir = os.path.join(tmpdir, 'diagnostics')
            os.makedirs(diag_dir)
            hdf_path = os.path.join(diag_dir, 'Diagnostics_Convergence.hdf')
            _make_convergence_hdf(hdf_path, n_timesteps=50)

            c = StabilityCollector(diagnostics_subdir='diagnostics')
            c.capture_base(tmpdir)
            assert c.has_base

            # Capture perturbation from same dir (same metrics)
            c.capture_perturbation(0, 'PKH001_L1', tmpdir)
            assert c.n_captured == 1

            result = c.compute()
            assert result.n_params == 1
            assert result.param_scores[0]['param_name'] == 'PKH001_L1'

    def test_reset(self):
        c = StabilityCollector()
        c.base_metrics = ConvergenceMetrics(n_timesteps=10)
        c._perturb_data = [(0, 'x', ConvergenceMetrics())]
        assert c.has_base
        assert c.n_captured == 1

        c.reset()
        assert not c.has_base
        assert c.n_captured == 0

    def test_perturbation_missing_file_silent(self):
        """Missing perturbation file is silently skipped (expected)."""
        c = StabilityCollector(diagnostics_subdir='nonexistent')
        c.capture_perturbation(0, 'PKH001_L1', '/tmp')
        assert c.n_captured == 0
        assert len(c._capture_errors) == 0  # silent skip, no error

    def test_compute_without_base(self):
        c = StabilityCollector()
        result = c.compute()
        assert result.n_params == 0
