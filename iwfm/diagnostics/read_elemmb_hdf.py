# read_elemmb_hdf.py
# Read Diagnostics_ElemMB.hdf and return MassBalanceSummary
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Read Diagnostics_ElemMB.hdf and return MassBalanceSummary.'''

import numpy as np
from iwfm.diagnostics.diag_dataclasses import MassBalanceSummary


def read_elemmb_hdf(hdf_path, n_elements, n_layers, threshold=1e5,
                    top_n_elements=20, verbose=False):
    """Read Diagnostics_ElemMB.hdf and compute summary statistics.

    Parameters
    ----------
    hdf_path : str
        Path to Diagnostics_ElemMB.hdf.
    n_elements : int
        Number of model elements.
    n_layers : int
        Number of model layers.
    threshold : float, default = 1e5
        Absolute residual threshold (ft^3/day) for flagging elements as
        hotspots. 
    top_n_elements : int, default = 20
        Max number of hotspot elements to report.
    verbose : bool, default = False
        Print progress.

    Returns
    -------
    MassBalanceSummary
    """
    import h5py

    with h5py.File(hdf_path, 'r') as f:
        # Shape: (NTIME, n_elements * n_layers)
        data = f['/MassBalanceResidual'][:]
        # IWFM diagnostics HDF stores residuals per-timestep where the
        # timestep length is set by the model's UNITT (1DAY, 1MON, etc.).
        # The threshold here is documented as ft^3/day, so normalize the
        # raw values to a per-day basis. DeltaT_InMinutes = 43200 means
        # 1MON (30 days exactly), giving days_per_step = 30.
        attrs = dict(f['Attributes'].attrs) if 'Attributes' in f else {}
    dt_minutes = attrs.get('TimeStep%DeltaT_InMinutes', None)
    if dt_minutes is None or dt_minutes <= 0:
        days_per_step = 1.0  # assume already per-day if metadata absent
    else:
        days_per_step = float(dt_minutes) / 1440.0  # 1440 min = 1 day

    n_ts, n_cols = data.shape
    expected_cols = n_layers * n_elements
    if n_cols != expected_cols:
        raise ValueError(
            f'ElemMB has {n_cols} columns, expected n_layers*n_elements='
            f'{expected_cols} ({n_layers}*{n_elements})')

    abs_data = np.abs(data) / days_per_step  # convert ft^3/step → ft^3/day

    # Reshape to (NTIME, n_layers, n_elements) — columns are layer-major
    reshaped = abs_data.reshape(n_ts, n_layers, n_elements)

    # Per-layer mean absolute residual (averaged over time and elements)
    mean_by_layer = [
        float(np.nanmean(reshaped[:, lay, :]))
        for lay in range(n_layers)
    ]

    max_abs = float(np.nanmax(abs_data))

    # Per-element, per-layer time-averaged absolute residual
    # Shape: (n_layers, n_elements)
    elem_mean = np.nanmean(reshaped, axis=0)
    elem_max = np.nanmax(reshaped, axis=0)

    # Find hotspots: elements exceeding threshold
    hotspot_mask = elem_mean > threshold
    n_above = int(np.sum(hotspot_mask))
    total_cells = n_elements * n_layers
    pct_above = 100.0 * n_above / total_cells if total_cells > 0 else 0.0

    # Get top-N hotspot elements sorted by mean residual
    flat_mean = elem_mean.ravel()
    flat_max = elem_max.ravel()
    top_indices = np.argsort(-flat_mean)[:top_n_elements]

    hotspot_list = []
    for idx in top_indices:
        layer = int(idx // n_elements)
        elem = int(idx % n_elements)
        if flat_mean[idx] <= 0:
            break
        hotspot_list.append({
            'element_id': elem + 1,  # 1-based
            'layer': layer + 1,      # 1-based
            'mean_abs_residual': float(flat_mean[idx]),
            'max_abs_residual': float(flat_max[idx]),
        })

    summary = MassBalanceSummary(
        mean_abs_residual_by_layer=mean_by_layer,
        max_abs_residual=max_abs,
        hotspot_elements=hotspot_list,
        pct_elements_above_threshold=float(pct_above),
    )

    if verbose:
        print(f'  ElemMB: {n_ts} timesteps, {n_elements} elements, '
              f'{n_layers} layers, max |residual| {max_abs:.3e}, '
              f'{n_above} cells above threshold')

    return summary
