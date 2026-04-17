# read_convergence_hdf.py
# Read Diagnostics_Convergence.hdf and return ConvergenceSummary
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

import numpy as np
from iwfm.diagnostics.diag_dataclasses import ConvergenceSummary

# ConvergenceSummary columns from Fortran DiagnosticsManager:
#   0: node     1: compID   2: layer   3: DIFFMAX
#   4: DIFF_L2  5: ITERX    6: RHSL2ratio

COL_NODE = 0
COL_COMP = 1
COL_LAYER = 2
COL_DIFFMAX = 3
COL_DIFF_L2 = 4
COL_ITERX = 5
COL_RHSL2 = 6


def read_convergence_hdf(hdf_path, max_iter_threshold=40,
                         diffmax_threshold=0.1, top_n_trouble=10,
                         verbose=False):
    """Read Diagnostics_Convergence.hdf and compute summary statistics.

    Parameters
    ----------
    hdf_path : str
        Path to Diagnostics_Convergence.hdf.
    max_iter_threshold : int
        Flag timesteps with ITERX >= this value.
    diffmax_threshold : float
        Flag timesteps with |DIFFMAX| >= this value.
    top_n_trouble : int
        Max number of trouble timesteps to report.
    verbose : bool
        Print progress.

    Returns
    -------
    ConvergenceSummary
    """
    import h5py

    with h5py.File(hdf_path, 'r') as f:
        data = f['/ConvergenceSummary'][:]  # (NTIME, 7), small dataset

    if data.size == 0 or data.ndim < 2:
        return ConvergenceSummary()

    n_ts = data.shape[0]
    iterations = data[:, COL_ITERX]
    diffmax = data[:, COL_DIFFMAX]
    rhs_ratio = data[:, COL_RHSL2]

    max_iter = int(np.nanmax(iterations))

    # pct_timesteps_at_max: fraction hitting the threshold (not observed max)
    pct_at_max = float(
        100.0 * np.sum(iterations >= max_iter_threshold) / n_ts
    )

    # Trouble timesteps: high iteration count or large DIFFMAX
    trouble_mask = (iterations >= max_iter_threshold) | \
                   (np.abs(diffmax) >= diffmax_threshold)
    trouble_indices = np.where(trouble_mask)[0]

    # Sort by |DIFFMAX| descending
    trouble_sorted = trouble_indices[
        np.argsort(-np.abs(diffmax[trouble_indices]))
    ][:top_n_trouble]

    trouble_list = []
    for idx in trouble_sorted:
        trouble_list.append({
            'timestep_index': int(idx),
            'diffmax': float(diffmax[idx]),
            'iterations': int(iterations[idx]),
            'node': int(data[idx, COL_NODE]),
            'comp_id': int(data[idx, COL_COMP]),
            'layer': int(data[idx, COL_LAYER]),
        })

    summary = ConvergenceSummary(
        mean_iterations=float(np.nanmean(iterations)),
        max_iterations=max_iter,
        pct_timesteps_at_max=pct_at_max,
        mean_diffmax=float(np.nanmean(np.abs(diffmax))),
        max_diffmax=float(np.nanmax(np.abs(diffmax))),
        mean_rhs_l2_ratio=float(np.nanmean(rhs_ratio)),
        trouble_timesteps=trouble_list,
    )

    if verbose:
        print(f'  Convergence: {n_ts} timesteps, '
              f'mean {summary.mean_iterations:.1f} iters, '
              f'max DIFFMAX {summary.max_diffmax:.3e}, '
              f'{len(trouble_list)} trouble timesteps')

    return summary
