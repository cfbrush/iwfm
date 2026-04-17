# read_stream_hdf.py
# Read Diagnostics_Stream.hdf and return StreamSummary
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

import numpy as np
from iwfm.diagnostics.diag_dataclasses import StreamSummary


def read_stream_hdf(hdf_path, last_n_timesteps=12, top_n_nodes=20,
                    verbose=False):
    """Read Diagnostics_Stream.hdf and compute summary statistics.

    Parameters
    ----------
    hdf_path : str
        Path to Diagnostics_Stream.hdf.
    last_n_timesteps : int
        Number of recent timesteps to use for anomaly detection.
    top_n_nodes : int
        Max number of anomaly nodes to report.
    verbose : bool
        Print progress.

    Returns
    -------
    StreamSummary
    """
    import h5py

    with h5py.File(hdf_path, 'r') as f:
        # All datasets shape (NTIME, NStrmNodes)
        strmgw = f['/StrmGWFlow'][:]

    n_ts, n_nodes = strmgw.shape

    # Use last N timesteps for statistics
    start = max(0, n_ts - last_n_timesteps)
    recent = strmgw[start:, :]

    # Overall statistics on recent window
    node_mean = np.nanmean(recent, axis=0)  # per-node temporal mean
    node_std = np.nanstd(recent, axis=0)    # per-node temporal std

    overall_mean = float(np.nanmean(node_mean))
    max_abs = float(np.nanmax(np.abs(node_mean)))

    # Gaining (positive StrmGWFlow = stream gains from GW) vs losing
    # Convention: positive = GW→stream (gaining), negative = stream→GW (losing)
    gaining = int(np.sum(node_mean > 0))
    losing = int(np.sum(node_mean < 0))

    # Anomaly detection: high coefficient of variation or magnitude outliers
    # Z-score on |mean| across nodes
    abs_mean = np.abs(node_mean)
    global_mean_abs = np.nanmean(abs_mean)
    global_std_abs = np.nanstd(abs_mean)

    anomaly_list = []
    if global_std_abs > 0:
        z_scores = (abs_mean - global_mean_abs) / global_std_abs
        # Also flag high-variance nodes (sign-flipping)
        with np.errstate(divide='ignore', invalid='ignore'):
            cv = np.where(np.abs(node_mean) > 1e-10,
                           node_std / np.abs(node_mean),
                           0.0)

        # Combine: magnitude outliers OR high CV
        magnitude_outliers = z_scores > 2.0
        cv_outliers = cv > 3.0
        anomaly_mask = magnitude_outliers | cv_outliers

        anomaly_indices = np.where(anomaly_mask)[0]
        # Sort by z-score descending
        sorted_idx = anomaly_indices[np.argsort(-z_scores[anomaly_indices])]
        sorted_idx = sorted_idx[:top_n_nodes]

        for idx in sorted_idx:
            flag = 'high_variance' if cv_outliers[idx] else 'extreme_magnitude'
            if magnitude_outliers[idx] and cv_outliers[idx]:
                flag = 'high_variance_and_magnitude'
            anomaly_list.append({
                'node_id': int(idx + 1),  # 1-based
                'mean_strmgw': float(node_mean[idx]),
                'std_strmgw': float(node_std[idx]),
                'z_score': float(z_scores[idx]),
                'flag': flag,
            })

    summary = StreamSummary(
        mean_stream_gw_flow=overall_mean,
        max_abs_stream_gw_flow=max_abs,
        gaining_reach_count=gaining,
        losing_reach_count=losing,
        anomaly_nodes=anomaly_list,
    )

    if verbose:
        print(f'  Stream: {n_ts} timesteps, {n_nodes} nodes, '
              f'{gaining} gaining, {losing} losing, '
              f'{len(anomaly_list)} anomalies')

    return summary
