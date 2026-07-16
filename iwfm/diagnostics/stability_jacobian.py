# stability_jacobian.py
# Stability Jacobian: identify parameters that destabilize model convergence
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

"""
Lightweight diagnostic capture during PEST Jacobian perturbation runs.

For each parameter perturbation, reads only the small Convergence HDF5
(~34 KB) and compares against base-run metrics. Parameters that increase
iteration counts, DIFFMAX, or trouble-timestep counts are flagged as
structurally destabilizing — they affect model *stability*, not just fit.

Usage with pypest
-----------------
    from iwfm.diagnostics.stability_jacobian import StabilityCollector

    collector = StabilityCollector(diagnostics_subdir='model/diagnostics')
    # ... set collector on JacobianCalculator.stability_collector ...
    # After Jacobian finishes:
    result = collector.compute()
    print(result.top_destabilizers)
"""

import os
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict


# Column indices — must match read_convergence_hdf.py
_COL_DIFFMAX = 3
_COL_ITERX = 5


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ConvergenceMetrics:
    """Lightweight convergence metrics from a single model run."""
    max_iterations: int = 0
    mean_iterations: float = 0.0
    max_diffmax: float = 0.0
    mean_diffmax: float = 0.0
    n_trouble_timesteps: int = 0
    n_timesteps: int = 0


@dataclass
class StabilityJacobian:
    """Per-parameter stability impact from Jacobian perturbation runs.

    Attributes
    ----------
    n_params : int
        Number of parameters with stability data.
    n_timesteps : int
        Timesteps in convergence file.
    base_max_iter : int
        Base run max iterations.
    base_mean_iter : float
        Base run mean iterations.
    base_max_diffmax : float
        Base run max DIFFMAX.
    base_n_trouble : int
        Base run trouble timestep count.
    param_scores : list of dict
        Per-parameter stability impact scores, sorted by score descending.
        Each dict: {param_name, param_index, delta_max_iter, delta_mean_iter,
        delta_max_diffmax, delta_n_trouble, stability_score, destabilizing}.
    top_destabilizers : list of dict
        Top N destabilizing parameters (subset of param_scores).
    n_destabilizing : int
        Count of parameters exceeding destabilization threshold.
    mean_stability_score : float
        Mean score across all parameters.
    max_stability_score : float
        Worst (highest) score.
    """
    n_params: int = 0
    n_timesteps: int = 0
    base_max_iter: int = 0
    base_mean_iter: float = 0.0
    base_max_diffmax: float = 0.0
    base_n_trouble: int = 0
    param_scores: List[Dict] = field(default_factory=list)
    top_destabilizers: List[Dict] = field(default_factory=list)
    n_destabilizing: int = 0
    mean_stability_score: float = 0.0
    max_stability_score: float = 0.0


# ---------------------------------------------------------------------------
# Lightweight convergence reader
# ---------------------------------------------------------------------------

def read_convergence_quick(hdf_path, iter_threshold=40, diffmax_threshold=0.1):
    """Read Diagnostics_Convergence.hdf and return lightweight metrics.

    Only reads the small convergence summary dataset (~34 KB),
    not the full residual history.

    Parameters
    ----------
    hdf_path : str
        Path to Diagnostics_Convergence.hdf.
    iter_threshold : int
        Flag timesteps with ITERX >= this value as trouble.
    diffmax_threshold : float
        Flag timesteps with abs(DIFFMAX) >= this value as trouble.

    Returns
    -------
    ConvergenceMetrics
    """
    import h5py

    with h5py.File(hdf_path, 'r') as f:
        data = f['/ConvergenceSummary'][:]

    if data.size == 0 or data.ndim < 2:
        return ConvergenceMetrics()

    iterations = data[:, _COL_ITERX]
    diffmax = np.abs(data[:, _COL_DIFFMAX])

    trouble_mask = (iterations >= iter_threshold) | (diffmax >= diffmax_threshold)

    return ConvergenceMetrics(
        max_iterations=int(np.nanmax(iterations)),
        mean_iterations=float(np.nanmean(iterations)),
        max_diffmax=float(np.nanmax(diffmax)),
        mean_diffmax=float(np.nanmean(diffmax)),
        n_trouble_timesteps=int(np.sum(trouble_mask)),
        n_timesteps=data.shape[0],
    )


# ---------------------------------------------------------------------------
# Stability scoring
# ---------------------------------------------------------------------------

def compute_stability_scores(base_metrics, perturb_data,
                             score_threshold=0.1, top_n=20):
    """Compute stability Jacobian from base and perturbation metrics.

    Parameters
    ----------
    base_metrics : ConvergenceMetrics
        Metrics from base model run.
    perturb_data : list of (int, str, ConvergenceMetrics)
        (param_index, param_name, metrics) from each perturbation.
    score_threshold : float
        Parameters with score above this are flagged as destabilizing.
    top_n : int
        Number of top destabilizers to report.

    Returns
    -------
    StabilityJacobian
    """
    if base_metrics is None or not perturb_data:
        return StabilityJacobian()

    scores = []
    for param_idx, param_name, metrics in perturb_data:
        delta_max_iter = metrics.max_iterations - base_metrics.max_iterations
        delta_mean_iter = metrics.mean_iterations - base_metrics.mean_iterations
        delta_max_diffmax = metrics.max_diffmax - base_metrics.max_diffmax
        delta_n_trouble = (metrics.n_trouble_timesteps
                           - base_metrics.n_trouble_timesteps)

        # Combined score: weighted normalized destabilization.
        # Only positive deltas count (parameter made things worse).
        # Weights: mean_iter (0.35) + max_diffmax (0.30) +
        #          n_trouble (0.20) + max_iter (0.15)
        score = 0.0
        if base_metrics.mean_iterations > 0:
            score += 0.35 * max(0, delta_mean_iter) / base_metrics.mean_iterations
        if base_metrics.max_diffmax > 0:
            score += 0.30 * max(0, delta_max_diffmax) / base_metrics.max_diffmax
        if base_metrics.n_timesteps > 0:
            score += 0.20 * max(0, delta_n_trouble) / base_metrics.n_timesteps
        if base_metrics.max_iterations > 0:
            score += 0.15 * max(0, delta_max_iter) / base_metrics.max_iterations

        scores.append({
            'param_name': param_name,
            'param_index': param_idx,
            'delta_max_iter': delta_max_iter,
            'delta_mean_iter': round(delta_mean_iter, 2),
            'delta_max_diffmax': round(delta_max_diffmax, 6),
            'delta_n_trouble': delta_n_trouble,
            'stability_score': round(score, 4),
            'destabilizing': score > score_threshold,
        })

    scores.sort(key=lambda x: x['stability_score'], reverse=True)

    n_destab = sum(1 for s in scores if s['destabilizing'])
    all_scores_vals = [s['stability_score'] for s in scores]

    return StabilityJacobian(
        n_params=len(scores),
        n_timesteps=base_metrics.n_timesteps,
        base_max_iter=base_metrics.max_iterations,
        base_mean_iter=round(base_metrics.mean_iterations, 2),
        base_max_diffmax=round(base_metrics.max_diffmax, 6),
        base_n_trouble=base_metrics.n_trouble_timesteps,
        param_scores=scores,
        top_destabilizers=scores[:top_n],
        n_destabilizing=n_destab,
        mean_stability_score=(round(float(np.mean(all_scores_vals)), 4)
                              if all_scores_vals else 0.0),
        max_stability_score=(round(float(np.max(all_scores_vals)), 4)
                             if all_scores_vals else 0.0),
    )


# ---------------------------------------------------------------------------
# Collector — stateful, used during pypest Jacobian computation
# ---------------------------------------------------------------------------

class StabilityCollector:
    """Collects convergence metrics from base and perturbation model runs.

    Set as ``JacobianCalculator.stability_collector``.  The calculator
    calls ``capture_base()`` after the base run and
    ``capture_perturbation()`` after each perturbation run.  At end of
    Jacobian, call ``compute()`` to get the StabilityJacobian.

    Parameters
    ----------
    diagnostics_subdir : str
        Subdirectory within each run directory where convergence HDF5
        is written (relative to the run script's CWD).
    convergence_filename : str
        Name of convergence HDF5 file.
    iter_threshold : int
        ITERX threshold for trouble-timestep detection.
    diffmax_threshold : float
        abs(DIFFMAX) threshold for trouble-timestep detection.
    score_threshold : float
        Stability score above which a parameter is flagged.
    top_n : int
        Number of top destabilizers to report.
    verbose : bool
        Print capture events.
    """

    def __init__(self, diagnostics_subdir='model/diagnostics',
                 convergence_filename='Diagnostics_Convergence.hdf',
                 iter_threshold=40, diffmax_threshold=0.1,
                 score_threshold=0.1, top_n=20, verbose=False):
        self.diagnostics_subdir = diagnostics_subdir
        self.convergence_filename = convergence_filename
        self.iter_threshold = iter_threshold
        self.diffmax_threshold = diffmax_threshold
        self.score_threshold = score_threshold
        self.top_n = top_n
        self.verbose = verbose

        self.base_metrics = None
        self._perturb_data = []   # [(param_idx, param_name, ConvergenceMetrics)]
        self._capture_errors = []

    def capture_base(self, run_dir):
        """Read convergence metrics after base model run.

        Parameters
        ----------
        run_dir : str
            Working directory where model ran (parent of diagnostics_subdir).
        """
        hdf_path = os.path.join(run_dir, self.diagnostics_subdir,
                                self.convergence_filename)
        if not os.path.exists(hdf_path):
            self._capture_errors.append(f'base: {hdf_path} not found')
            return

        try:
            self.base_metrics = read_convergence_quick(
                hdf_path, self.iter_threshold, self.diffmax_threshold)
            if self.verbose:
                m = self.base_metrics
                print(f'  [stability] base: {m.mean_iterations:.1f} mean iter, '
                      f'{m.max_diffmax:.3e} max DIFFMAX, '
                      f'{m.n_trouble_timesteps} trouble ts')
        except (OSError, KeyError, ValueError) as e:
            self._capture_errors.append(f'base: {e}')

    def capture_perturbation(self, param_idx, param_name, run_dir):
        """Read convergence metrics after a perturbation model run.

        Thread-safe (CPython GIL protects list.append).

        Parameters
        ----------
        param_idx : int
            Parameter column index in Jacobian.
        param_name : str
            Parameter name.
        run_dir : str
            Working directory where perturbed model ran.
        """
        hdf_path = os.path.join(run_dir, self.diagnostics_subdir,
                                self.convergence_filename)
        if not os.path.exists(hdf_path):
            # Expected when diagnostics disabled for perturbation runs
            return

        try:
            metrics = read_convergence_quick(
                hdf_path, self.iter_threshold, self.diffmax_threshold)
            self._perturb_data.append((param_idx, param_name, metrics))
        except (OSError, KeyError, ValueError) as e:
            self._capture_errors.append(f'{param_name}: {e}')

    def compute(self):
        """Compute stability scores from collected metrics.

        Returns
        -------
        StabilityJacobian
        """
        result = compute_stability_scores(
            self.base_metrics, self._perturb_data,
            score_threshold=self.score_threshold, top_n=self.top_n)

        if self.verbose and result.n_params > 0:
            print(f'  [stability] {result.n_params} params scored, '
                  f'{result.n_destabilizing} destabilizing, '
                  f'max score {result.max_stability_score:.4f}')
            if result.top_destabilizers:
                top = result.top_destabilizers[0]
                print(f'  [stability] worst: {top["param_name"]} '
                      f'(score={top["stability_score"]:.4f}, '
                      f'Δiter={top["delta_mean_iter"]:+.1f}, '
                      f'ΔDIFFMAX={top["delta_max_diffmax"]:+.3e})')

        return result

    def reset(self):
        """Reset for next iteration. Called at start of each Jacobian."""
        self.base_metrics = None
        self._perturb_data = []
        self._capture_errors = []

    @property
    def n_captured(self):
        """Number of perturbation metrics captured so far."""
        return len(self._perturb_data)

    @property
    def has_base(self):
        """Whether base metrics have been captured."""
        return self.base_metrics is not None
