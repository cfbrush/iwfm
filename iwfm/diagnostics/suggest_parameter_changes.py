# suggest_parameter_changes.py
# Generate parameter selection recommendations from diagnostic bundle
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

from iwfm.diagnostics.select_parameters import select_parameters
from iwfm.diagnostics.build_tied_groups import (
    build_tied_groups, build_stream_tied_groups,
)


# Default parameter configuration for C2VSimCG-style models
DEFAULT_PARAM_CONFIG = {
    'PKH': {  # Horizontal hydraulic conductivity
        'layers': [1, 2],
        'group': 'fackh',
        'transform': 'none',
        'change_type': 'factor',
        'bound_multiplier': 10.0,  # upper = initial * mult, lower = initial / mult
        'phase': 1,
    },
    'PL': {  # Aquitard vertical hydraulic conductivity (clay layer above aquifer)
        'layers': [1, 2],
        'group': 'fackv',
        'transform': 'none',
        'change_type': 'factor',
        'bound_multiplier': 10.0,
        'phase': 2,
        'note': 'Only present where aquitard thickness > 0 (some L2 nodes in C2VSimCG)',
    },
    'PN': {  # Specific yield (Sy) — unconfined storage
        'layers': [1],
        'group': 'facsy',
        'transform': 'none',
        'change_type': 'factor',
        'bound_multiplier': 2.0,
        'phase': 3,
    },
    'PS': {  # Specific storage (Ss) — confined storage
        'layers': [2],
        'group': 'facss',
        'transform': 'none',
        'change_type': 'factor',
        'bound_multiplier': 10.0,
        'phase': 3,
    },
    'c_sn': {  # Stream bed conductance
        'layers': [0],  # 0 = no layer suffix
        'group': 'stcond',
        'transform': 'none',
        'change_type': 'factor',
        'bound_multiplier': 10.0,
        'phase': 2,
    },
}


def suggest_parameter_changes(bundle, sensitivity, node_coords,
                              stream_node_ids=None, n_reps_per_group=25,
                              phase=None, param_config=None,
                              candidate_nodes=None, pst_file=None,
                              diagnostic_weight=0.3, verbose=False):
    """Generate parameter selection recommendations from diagnostic data.

    Parameters
    ----------
    bundle : DiagnosticBundle
        Assembled diagnostic bundle from current PEST iteration.
    sensitivity : dict
        From read_pest_sensitivity: {param_name: {sensitivity, ...}}.
    node_coords : dict
        {node_id: (x, y)} for all GW nodes.
    stream_node_ids : list of int, optional
        All stream node IDs. If None, stream params skipped.
    n_reps_per_group : int
        Target number of representative nodes per parameter group per layer.
    phase : int, optional
        Calibration phase (1-3). Only parameters with phase <= this are
        activated. If None, determine from bundle signals.
    param_config : dict, optional
        Override DEFAULT_PARAM_CONFIG.
    candidate_nodes : dict, optional
        {prefix: set of int} restricting which nodes can be selected
        per parameter prefix. If None and pst_file provided, extracted
        automatically from .pst file.
    pst_file : str, optional
        Path to .pst file. Used to auto-detect candidate nodes if
        candidate_nodes not provided.
    diagnostic_weight : float
        Weight for diagnostic signals in selection (0-1).
    verbose : bool
        Print progress.

    Returns
    -------
    dict
        Recommendation structure with keys:
        - 'phase': int, recommended calibration phase
        - 'param_groups': dict of per-group recommendations
        - 'bound_changes': list of bound adjustment recommendations
        - 'summary': str, human-readable summary
    """
    config = param_config or DEFAULT_PARAM_CONFIG

    # Auto-detect candidate nodes from .pst if needed
    if candidate_nodes is None and pst_file:
        from iwfm.diagnostics.parse_model_geometry import parse_pst_param_nodes
        candidate_nodes = {}
        for prefix in config:
            candidate_nodes[prefix] = parse_pst_param_nodes(
                pst_file, prefix=prefix)

    # Determine phase from bundle if not specified
    if phase is None:
        phase = _recommend_phase(bundle)

    recommendations = {
        'phase': phase,
        'param_groups': {},
        'bound_changes': [],
        'summary': '',
    }

    active_groups = {k: v for k, v in config.items() if v['phase'] <= phase}

    for prefix, pconf in active_groups.items():
        for layer in pconf['layers']:
            is_stream = prefix == 'c_sn'

            # Get candidate nodes for this prefix
            candidates = None
            if candidate_nodes and prefix in candidate_nodes:
                candidates = candidate_nodes[prefix]

            if is_stream:
                if stream_node_ids is None:
                    continue
                strm_candidates = (list(candidates)
                                   if candidates else stream_node_ids)
                strm_coords = {sn: node_coords.get(sn, (0, 0))
                               for sn in strm_candidates}
                reps, scores = select_parameters(
                    strm_coords, n_reps_per_group,
                    sensitivity=sensitivity, bundle=bundle,
                    param_prefix=prefix, layer=0,
                    candidate_nodes=candidates,
                    diagnostic_weight=diagnostic_weight,
                    verbose=verbose,
                )
                tied_map, groups = build_stream_tied_groups(
                    strm_candidates, reps)
                group_key = prefix
            else:
                reps, scores = select_parameters(
                    node_coords, n_reps_per_group,
                    sensitivity=sensitivity, bundle=bundle,
                    param_prefix=prefix, layer=layer,
                    candidate_nodes=candidates,
                    diagnostic_weight=diagnostic_weight,
                    verbose=verbose,
                )
                # Only tie candidate nodes, not all model nodes
                tie_coords = {nid: node_coords[nid]
                              for nid in (candidates or node_coords)
                              if nid in node_coords}
                tied_map, groups = build_tied_groups(tie_coords, reps)
                group_key = f'{prefix}_L{layer}'

            recommendations['param_groups'][group_key] = {
                'prefix': prefix,
                'layer': layer,
                'pest_group': pconf['group'],
                'transform': pconf['transform'],
                'change_type': pconf['change_type'],
                'representatives': reps,
                'tied_map': tied_map,
                'groups': groups,
                'n_reps': len(reps),
                'n_tied': len(tied_map),
                'scores': scores,
            }

    # Generate bound change recommendations
    recommendations['bound_changes'] = _recommend_bounds(
        bundle, sensitivity, config)

    # Generate summary
    total_reps = sum(g['n_reps']
                     for g in recommendations['param_groups'].values())
    total_tied = sum(g['n_tied']
                     for g in recommendations['param_groups'].values())
    group_names = list(recommendations['param_groups'].keys())

    recommendations['summary'] = (
        f'Phase {phase}: {len(group_names)} parameter groups active '
        f'({", ".join(group_names)}). '
        f'{total_reps} representative nodes, {total_tied} tied. '
        f'{len(recommendations["bound_changes"])} bound changes recommended.'
    )

    if verbose:
        print(f'\n  {recommendations["summary"]}')

    return recommendations


def _recommend_phase(bundle):
    """Determine calibration phase from diagnostic signals."""
    if bundle.pest_state is None:
        return 1

    # Phase 1: early calibration, focus on Kh
    # Phase 2: add leakance + stream conductance
    # Phase 3: add storage + porosity

    rmse = bundle.pest_state.rmse
    iteration = bundle.pest_state.iteration

    # Simple heuristic: advance phase as model improves
    if iteration <= 3 or rmse > 50:
        return 1
    if iteration <= 8 or rmse > 20:
        return 2
    return 3


def _recommend_bounds(bundle, sensitivity, config):
    """Generate bound change recommendations."""
    changes = []

    if bundle.pest_state is None:
        return changes

    for pab in bundle.pest_state.params_at_bounds:
        name = pab['name']
        value = pab['value']
        lower = pab['lower']
        upper = pab['upper']
        pct = pab['pct_of_range']

        # Determine which config group this belongs to
        prefix = None
        for p in config:
            if name.startswith(p):
                prefix = p
                break

        if prefix is None:
            continue

        mult = config[prefix]['bound_multiplier']

        if pct >= 0.95:
            # At upper bound — extend upper
            new_upper = value * mult
            changes.append({
                'name': name,
                'action': 'extend_upper',
                'current_upper': upper,
                'new_upper': new_upper,
                'reason': f'{name} at upper bound ({value:.4g} = {upper:.4g})',
            })
        elif pct <= 0.05:
            # At lower bound — extend lower
            new_lower = value / mult
            if new_lower < 1e-10:
                new_lower = 1e-10
            changes.append({
                'name': name,
                'action': 'extend_lower',
                'current_lower': lower,
                'new_lower': new_lower,
                'reason': f'{name} at lower bound ({value:.4g} = {lower:.4g})',
            })

    return changes
