# select_parameters.py
# Select representative nodes for PEST parameter estimation
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Select representative nodes for PEST parameter estimation.'''

import numpy as np


def select_parameters(node_coords, n_reps, sensitivity=None, bundle=None,
                      param_prefix='PKH', layer=1, min_spacing=None,
                      candidate_nodes=None, diagnostic_weight=0.3,
                      verbose=False):
    """Select representative nodes for PEST parameter estimation.

    Uses a greedy algorithm that balances three criteria:
    1. Sensitivity — prefer nodes where parameters have high PEST sensitivity
    2. Diagnostic signal — prefer nodes near convergence/residual trouble
    3. Spatial coverage — enforce minimum spacing to avoid clustering

    Parameters
    ----------
    node_coords : dict or list
        Node coordinates. If dict: {node_id: (x, y)}.
        If list of (x, y), indexed 1-based (node 1 = index 0).
    n_reps : int
        Number of representative nodes to select.
    sensitivity : dict, optional
        From read_pest_sensitivity: {param_name: {sensitivity: float}}.
        Used to score nodes by their parameter's sensitivity.
    bundle : DiagnosticBundle, optional
        Diagnostic bundle for signal-based scoring.
    param_prefix : str
        Parameter name prefix for matching sensitivity data.
        'PKH' for Kh, 'PL' for leakance, 'PN' for Sy,
        'PS' for Ss, 'c_sn' for stream conductance.
    layer : int
        Layer number (1-based) for GW params. Ignored for stream.
    min_spacing : float, optional
        Minimum distance between representatives. If None, computed
        as domain_extent / (2 * sqrt(n_reps)).
    candidate_nodes : list of int, optional
        Restrict selection to these node IDs only. If None, all nodes
        in node_coords are candidates. Use this when only a subset of
        nodes have PEST parameters in the template file.
    diagnostic_weight : float
        Weight for diagnostic signals vs sensitivity (0-1).
        0 = sensitivity only, 1 = diagnostics only.
    verbose : bool
        Print progress.

    Returns
    -------
    list of int
        Selected representative node IDs (1-based).
    dict
        Scores: {node_id: {'sensitivity': float, 'diagnostic': float,
                           'combined': float}}.
    """
    # Normalize node_coords to dict {node_id: (x, y)}
    if isinstance(node_coords, list):
        coords = {i + 1: tuple(xy) for i, xy in enumerate(node_coords)}
    else:
        coords = dict(node_coords)

    # Restrict to candidate nodes if specified
    if candidate_nodes is not None:
        coords = {nid: xy for nid, xy in coords.items()
                  if nid in set(candidate_nodes)}

    node_ids = sorted(coords.keys())
    n_nodes = len(node_ids)

    if n_reps >= n_nodes:
        return node_ids, {}

    # Build coordinate array for distance calculations
    id_to_idx = {nid: i for i, nid in enumerate(node_ids)}
    xy = np.array([coords[nid] for nid in node_ids])

    # Compute default min_spacing from domain extent
    if min_spacing is None:
        extent = np.max(xy, axis=0) - np.min(xy, axis=0)
        domain_diag = np.sqrt(extent[0] ** 2 + extent[1] ** 2)
        min_spacing = domain_diag / (2 * np.sqrt(n_reps))

    # Score 1: Sensitivity
    sens_scores = np.zeros(n_nodes)
    if sensitivity:
        sens_scores = _score_sensitivity(node_ids, sensitivity,
                                         param_prefix, layer)

    # Score 2: Diagnostic signals
    diag_scores = np.zeros(n_nodes)
    if bundle:
        diag_scores = _score_diagnostics(node_ids, id_to_idx, bundle, layer)

    # Combine scores (both normalized to 0-1)
    sens_norm = _normalize(sens_scores)
    diag_norm = _normalize(diag_scores)
    w = diagnostic_weight
    combined = (1 - w) * sens_norm + w * diag_norm

    # Greedy selection with minimum spacing constraint
    selected = []
    available = set(range(n_nodes))

    scores_out = {}
    for nid, i in zip(node_ids, range(n_nodes)):
        scores_out[nid] = {
            'sensitivity': float(sens_norm[i]),
            'diagnostic': float(diag_norm[i]),
            'combined': float(combined[i]),
        }

    for _ in range(n_reps):
        if not available:
            break

        # Pick highest-scoring available node
        best_idx = max(available, key=lambda i: combined[i])
        selected.append(best_idx)
        available.discard(best_idx)

        # Remove nodes too close to selected
        if min_spacing > 0:
            best_xy = xy[best_idx]
            to_remove = set()
            for idx in available:
                dist = np.sqrt(np.sum((xy[idx] - best_xy) ** 2))
                if dist < min_spacing:
                    to_remove.add(idx)
            available -= to_remove

        # If we ran out of available nodes but need more reps,
        # relax spacing and continue from remaining
        if not available and len(selected) < n_reps:
            all_remaining = set(range(n_nodes)) - set(selected)
            if all_remaining:
                available = all_remaining
                min_spacing = min_spacing * 0.5

    selected_ids = [node_ids[i] for i in selected]

    if verbose:
        print(f'  Selected {len(selected_ids)}/{n_reps} reps for '
              f'{param_prefix}_L{layer} (min_spacing={min_spacing:.0f})')
        top = sorted(selected_ids,
                     key=lambda nid: scores_out[nid]['combined'],
                     reverse=True)[:5]
        for nid in top:
            s = scores_out[nid]
            print(f'    Node {nid}: sens={s["sensitivity"]:.3f} '
                  f'diag={s["diagnostic"]:.3f} combined={s["combined"]:.3f}')

    return selected_ids, scores_out


def _score_sensitivity(node_ids, sensitivity, param_prefix, layer):
    """Score nodes by their parameter sensitivity."""
    scores = np.zeros(len(node_ids))

    if param_prefix == 'c_sn':
        # Stream conductance: c_sn_NNN
        for i, nid in enumerate(node_ids):
            pname = f'c_sn_{nid:03d}'
            if pname in sensitivity:
                scores[i] = abs(sensitivity[pname]['sensitivity'])
    else:
        # GW params: PREFIX_NNN_LN
        layer_suffix = f'_L{layer}'
        for i, nid in enumerate(node_ids):
            pname = f'{param_prefix}{nid:03d}{layer_suffix}'
            if pname in sensitivity:
                scores[i] = abs(sensitivity[pname]['sensitivity'])

    return scores


def _score_diagnostics(node_ids, id_to_idx, bundle, layer):
    """Score nodes by diagnostic signal strength."""
    scores = np.zeros(len(node_ids))

    # Residual worst nodes
    if bundle.residuals and bundle.residuals.worst_nodes:
        for wn in bundle.residuals.worst_nodes:
            nid = wn['node_id']
            if nid in id_to_idx and wn['layer'] == layer:
                scores[id_to_idx[nid]] += wn['mean_rhs']

    # Convergence trouble nodes
    if bundle.convergence and bundle.convergence.trouble_timesteps:
        for tt in bundle.convergence.trouble_timesteps:
            nid = tt.get('node')
            if nid and nid in id_to_idx:
                scores[id_to_idx[nid]] += tt['iterations']

    # Residual clusters
    if (bundle.structural_signals and
            bundle.structural_signals.residual_cluster_nodes):
        for rc in bundle.structural_signals.residual_cluster_nodes:
            nid = rc['node_id']
            if nid in id_to_idx and rc.get('layer', layer) == layer:
                scores[id_to_idx[nid]] += rc.get('z_score', 1.0) * 1000

    return scores


def _normalize(arr):
    """Normalize array to 0-1 range."""
    vmin = np.min(arr)
    vmax = np.max(arr)
    if vmax - vmin < 1e-15:
        return np.zeros_like(arr)
    return (arr - vmin) / (vmax - vmin)
