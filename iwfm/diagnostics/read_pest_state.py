# read_pest_state.py
# Read PEST iteration state from .res, .rec, .par, .pst, .sen files
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Read PEST iteration state from .res, .rec, .par, .pst, .sen files.'''

import math
from iwfm.diagnostics.diag_dataclasses import PestStateSummary


def read_pest_state(res_file=None, rec_file=None, par_file=None,
                    pst_file=None, sen_file=None, param_bounds=None,
                    iteration=0, verbose=False):
    """Read PEST iteration state and return PestStateSummary.

    Parameters
    ----------
    res_file : str, optional
        Path to PEST .res file (observation residuals).
    rec_file : str, optional
        Path to PEST .rec file (iteration history with phi).
    par_file : str, optional
        Path to PEST .par file (current parameter values).
    pst_file : str, optional
        Path to PEST .pst file (parameter bounds from control file).
    sen_file : str, optional
        Path to PEST .sen file (parameter sensitivities).
    param_bounds : dict, optional
        Override bounds: {name: (lower, upper)}. If None and pst_file
        provided, bounds are read from .pst.
    iteration : int
        PEST iteration number (used if .rec not available).
    verbose : bool
        Print progress.

    Returns
    -------
    PestStateSummary
    """
    # Parse bounds from .pst if not provided
    if param_bounds is None and pst_file:
        param_bounds = _parse_pst_bounds(pst_file)

    # Parse .rec for iteration/phi history
    rec_iteration = iteration
    phi = 0.0
    if rec_file:
        rec_iteration, phi = _parse_rec_last_iteration(rec_file)
        if verbose:
            print(f'  PEST rec: iteration {rec_iteration}, phi {phi:.4e}')

    # Parse .res for per-group residual statistics
    n_obs = 0
    rmse = 0.0
    bias = 0.0
    obs_group_stats = []
    if res_file:
        n_obs, rmse, bias, obs_group_stats = _parse_res_file(res_file)
        if not phi:
            phi = sum(r['rmse'] ** 2 * r['n'] for r in obs_group_stats)
        if verbose:
            print(f'  PEST res: {n_obs} obs, RMSE {rmse:.2f}, '
                  f'{len(obs_group_stats)} groups')

    # Parse .par + bounds for params-at-bounds detection
    params_at_bounds = []
    params_at_bounds_by_group = {}
    n_params_at_bounds = 0
    if par_file and param_bounds:
        params_at_bounds = _detect_bounds(par_file, param_bounds)
        n_params_at_bounds = len(params_at_bounds)
        # Phase 8.12: aggregate by group so total picture survives truncation
        for rec in params_at_bounds:
            grp = rec.get('group', 'unknown')
            params_at_bounds_by_group[grp] = params_at_bounds_by_group.get(grp, 0) + 1
        if verbose:
            print(f'  PEST par: {n_params_at_bounds} params near bounds; '
                  f'by group: {params_at_bounds_by_group}')

    return PestStateSummary(
        iteration=rec_iteration,
        phi=phi,
        n_observations=n_obs,
        rmse=rmse,
        bias=bias,
        obs_group_stats=obs_group_stats,
        params_at_bounds=params_at_bounds,
        params_at_bounds_by_group=params_at_bounds_by_group,
        n_params_at_bounds=n_params_at_bounds,
    )


def _parse_res_file(res_file):
    """Parse PEST .res file for per-group RMSE and bias.

    .res format: whitespace-delimited columns
      Name  Group  Measured  Modelled  Residual  Weight  ...

    Returns (n_obs, overall_rmse, overall_bias, group_stats_list)
    """
    groups = {}  # group -> {n, sum_res, sum_res_sq}

    with open(res_file, encoding='utf-8') as f:
        f.readline()  # skip header
        for line in f:
            parts = line.split()
            if len(parts) < 6:
                continue
            group = parts[1]
            try:
                residual = float(parts[4])
                weight = float(parts[5])
            except (ValueError, IndexError):
                continue

            weighted_res = residual * weight

            if group not in groups:
                groups[group] = {'n': 0, 'sum_res': 0.0, 'sum_res_sq': 0.0}
            g = groups[group]
            g['n'] += 1
            g['sum_res'] += weighted_res
            g['sum_res_sq'] += weighted_res ** 2

    # Compute per-group and overall statistics
    total_n = 0
    total_sum_res = 0.0
    total_sum_res_sq = 0.0
    group_stats = []

    for group_name, g in sorted(groups.items()):
        n = g['n']
        if n == 0:
            continue
        grp_bias = g['sum_res'] / n
        grp_rmse = math.sqrt(g['sum_res_sq'] / n)
        group_stats.append({
            'group': group_name,
            'n': n,
            'rmse': grp_rmse,
            'bias': grp_bias,
        })
        total_n += n
        total_sum_res += g['sum_res']
        total_sum_res_sq += g['sum_res_sq']

    overall_bias = total_sum_res / total_n if total_n > 0 else 0.0
    overall_rmse = math.sqrt(total_sum_res_sq / total_n) if total_n > 0 else 0.0

    return total_n, overall_rmse, overall_bias, group_stats


def _parse_rec_last_iteration(rec_file):
    """Parse PEST .rec file to get last iteration number and phi.

    .rec format:
      Line 1: header (Iteration  Phi  param1  param2 ...)
      Line 2: dashes
      Lines 3+: iteration_number  phi  param_values...

    Returns (iteration, phi)
    """
    last_iter = 0
    last_phi = 0.0

    with open(rec_file, encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                iter_num = int(parts[0])
                phi = float(parts[1])
                last_iter = iter_num
                last_phi = phi
            except (ValueError, IndexError):
                continue

    return last_iter, last_phi


def _parse_pst_bounds(pst_file):
    """Parse PEST .pst control file for parameter bounds (and group).

    Parameter data section format:
      name  transform  type  initial  lower  upper  group  ...

    Only returns adjustable parameters (transform != 'fixed' and != 'tied').

    Returns dict: {name: (lower, upper, group)}.
    Group is captured so downstream diagnostics can aggregate at-bounds
    counts by group (Phase 8.12).
    """
    bounds = {}
    in_param_section = False

    with open(pst_file, encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('* parameter data'):
                in_param_section = True
                continue
            if stripped.startswith('*') and in_param_section:
                break  # next section
            if not in_param_section:
                continue

            parts = stripped.split()
            if len(parts) < 7:
                continue

            name = parts[0]
            transform = parts[1]
            # Skip fixed/tied parameters
            if transform in ('fixed', 'tied'):
                continue

            try:
                lower = float(parts[4])
                upper = float(parts[5])
                group = parts[6]
                bounds[name] = (lower, upper, group)
            except (ValueError, IndexError):
                continue

    return bounds


def _detect_bounds(par_file, param_bounds, threshold=0.05):
    """Compare .par values against bounds, flag those near limits.

    .par format:
      Line 1: "single point"
      Lines 2+: name  value  scale  offset

    Returns list of dicts for params within threshold of bounds, sorted
    by distance-from-nearest-bound (most pinned first) so downstream
    truncation in serialize_bundle keeps the most informative rows.
    """
    results = []

    with open(par_file, encoding='utf-8') as f:
        f.readline()  # skip "single point"
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue

            name = parts[0]
            try:
                value = float(parts[1])
            except (ValueError, IndexError):
                continue

            if name not in param_bounds:
                continue

            entry = param_bounds[name]
            # Backward-compat: param_bounds may be (lo, hi) or (lo, hi, group)
            if len(entry) == 3:
                lower, upper, group = entry
            else:
                lower, upper = entry
                group = None
            span = upper - lower
            if span <= 0:
                continue

            pct = (value - lower) / span

            if pct <= threshold or pct >= (1.0 - threshold):
                rec = {
                    'name': name,
                    'value': value,
                    'lower': lower,
                    'upper': upper,
                    'pct_of_range': pct,
                    'distance_from_bound': min(pct, 1.0 - pct),
                }
                if group is not None:
                    rec['group'] = group
                results.append(rec)

    # Sort by distance_from_bound ascending (most pinned first). Equal
    # distances fall back to name for stable order.
    results.sort(key=lambda r: (r['distance_from_bound'], r['name']))
    return results
