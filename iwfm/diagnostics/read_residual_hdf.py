# read_residual_hdf.py
# Read Diagnostics_Residual.hdf with chunked access and return ResidualSummary
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Read Diagnostics_Residual.hdf with chunked access and return ResidualSummary.'''

import numpy as np
from iwfm.diagnostics.diag_dataclasses import ResidualSummary


def read_residual_hdf(hdf_path, n_gw_nodes, n_layers, max_iter_store=50,
                      last_n_timesteps=12, top_n_nodes=20, verbose=False):
    """Read Diagnostics_Residual.hdf using chunked access.

    Only loads the last N timestep blocks to avoid reading the full
    2+ GB file into memory.

    Parameters
    ----------
    hdf_path : str
        Path to Diagnostics_Residual.hdf.
    n_gw_nodes : int
        Number of groundwater nodes per layer.
    n_layers : int
        Number of model layers.
    max_iter_store : int
        Max iterations stored per timestep (rows per timestep block).
    last_n_timesteps : int
        Number of recent timesteps to process.
    top_n_nodes : int
        Max number of worst nodes to report.
    verbose : bool
        Print progress.

    Returns
    -------
    ResidualSummary
    """
    import h5py

    n_cols = n_gw_nodes * n_layers

    with h5py.File(hdf_path, 'r') as f:
        rhs_ds = f['/RHS']
        hdelta_ds = f['/HDelta']
        # IWFM diagnostics HDF stores per-timestep values. RHS is volumetric
        # flux balance (ft^3/timestep); HDelta is head change (ft, no time).
        # Normalize RHS to per-day. DeltaT_InMinutes=43200 for 1MON = 30 days.
        attrs = dict(f['Attributes'].attrs) if 'Attributes' in f else {}
        dt_minutes = attrs.get('TimeStep%DeltaT_InMinutes', None)
        if dt_minutes is None or dt_minutes <= 0:
            days_per_step = 1.0  # assume per-day if metadata absent
        else:
            days_per_step = float(dt_minutes) / 1440.0
        actual_cols = rhs_ds.shape[1]
        if actual_cols != n_cols:
            raise ValueError(
                f'Residual has {actual_cols} columns, expected '
                f'n_gw_nodes*n_layers={n_cols} ({n_gw_nodes}*{n_layers})')
        n_rows = rhs_ds.shape[0]
        n_ts = n_rows // max_iter_store

        start_ts = max(0, n_ts - last_n_timesteps)
        ts_count = n_ts - start_ts

        # Accumulators: per-node converged-state statistics
        rhs_sum = np.zeros(n_cols)
        hdelta_sum = np.zeros(n_cols)
        rhs_sq_sum = np.zeros(n_cols)
        hdelta_sq_sum = np.zeros(n_cols)
        valid_count = 0
        iter_total = 0

        for ts in range(start_ts, n_ts):
            row_start = ts * max_iter_store
            row_end = row_start + max_iter_store

            # Read one timestep block: (max_iter_store, n_cols)
            rhs_block = rhs_ds[row_start:row_end, :]
            hdelta_block = hdelta_ds[row_start:row_end, :]

            # Find valid (non-NaN) rows — NaN padding may be at start
            # or end of block depending on Fortran write order
            nan_mask = np.isnan(rhs_block[:, 0])
            valid_rows = np.where(~nan_mask)[0]
            n_valid = len(valid_rows)

            if n_valid == 0:
                continue

            iter_total += n_valid

            # Use the last valid row (converged state)
            last_valid_idx = valid_rows[-1]
            # RHS has time dimension → normalize to per-day. HDelta is
            # head change (ft) — no time conversion needed.
            rhs_converged = np.abs(rhs_block[last_valid_idx, :]) / days_per_step
            hdelta_converged = np.abs(hdelta_block[last_valid_idx, :])

            rhs_sum += rhs_converged
            hdelta_sum += hdelta_converged
            rhs_sq_sum += rhs_converged ** 2
            hdelta_sq_sum += hdelta_converged ** 2
            valid_count += 1

    if valid_count == 0:
        return ResidualSummary()

    # Per-node mean absolute values at convergence
    rhs_mean = rhs_sum / valid_count
    hdelta_mean = hdelta_sum / valid_count

    # Reshape to (n_layers, n_gw_nodes) — layer-major column ordering
    rhs_by_layer = rhs_mean.reshape(n_layers, n_gw_nodes)
    hdelta_by_layer = hdelta_mean.reshape(n_layers, n_gw_nodes)

    # L2 norm per layer (over nodes, of mean converged residual)
    rhs_l2 = [float(np.linalg.norm(rhs_by_layer[lay, :]))
              for lay in range(n_layers)]
    hdelta_l2 = [float(np.linalg.norm(hdelta_by_layer[lay, :]))
                 for lay in range(n_layers)]

    # Worst nodes: highest mean |RHS| at convergence
    worst_indices = np.argsort(-rhs_mean)[:top_n_nodes]
    worst_list = []
    for idx in worst_indices:
        layer = int(idx // n_gw_nodes) + 1   # 1-based
        node = int(idx % n_gw_nodes) + 1      # 1-based
        worst_list.append({
            'node_id': node,
            'layer': layer,
            'mean_rhs': float(rhs_mean[idx]),
            'mean_hdelta': float(hdelta_mean[idx]),
        })

    mean_iters = iter_total / valid_count if valid_count > 0 else 0.0

    summary = ResidualSummary(
        rhs_l2_by_layer=rhs_l2,
        hdelta_l2_by_layer=hdelta_l2,
        worst_nodes=worst_list,
        mean_iterations_to_converge=float(mean_iters),
    )

    if verbose and worst_list:
        print(f'  Residual: processed {valid_count}/{ts_count} timesteps, '
              f'mean {mean_iters:.1f} iters, '
              f'worst RHS node {worst_list[0]["node_id"]} L{worst_list[0]["layer"]}')
    elif verbose:
        print(f'  Residual: processed {valid_count}/{ts_count} timesteps, '
              f'mean {mean_iters:.1f} iters')

    return summary
