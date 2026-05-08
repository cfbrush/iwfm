# detect_params_at_bounds.py
# Detect PEST parameters near their upper or lower bounds
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+


def detect_params_at_bounds(pest_state, bound_pct_threshold=0.05):
    """Identify parameters within a percentage of their bounds.

    Parameters
    ----------
    pest_state : PestStateSummary
        From read_pest_state.
    bound_pct_threshold : float
        Flag if pct_of_range < threshold or > (1 - threshold).
        Default 0.05 = 5%.

    Returns
    -------
    list of dict
        [{name, value, lower, upper, pct_of_range, bound}]
    """
    results = []
    for p in pest_state.params_at_bounds:
        pct = p.get('pct_of_range', None)
        if pct is None:
            continue
        bound = None
        if pct <= bound_pct_threshold:
            bound = 'lower'
        elif pct >= (1.0 - bound_pct_threshold):
            bound = 'upper'
        if bound:
            results.append({
                'name': p['name'],
                'value': p['value'],
                'lower': p['lower'],
                'upper': p['upper'],
                'pct_of_range': pct,
                'bound': bound,
            })
    # Phase 8.12: sort by distance-to-nearest-bound (most-pinned first) so
    # downstream serializer's [:max_items] truncation surfaces the most
    # pinned params, not the lexicographically-first ones.
    results.sort(key=lambda r: min(r['pct_of_range'], 1.0 - r['pct_of_range']))
    return results
