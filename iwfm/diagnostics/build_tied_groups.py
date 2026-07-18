# build_tied_groups.py
# Assign non-representative nodes to nearest representative (Voronoi tying)
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Assign non-representative nodes to nearest representative (Voronoi tying).'''

import numpy as np


def build_tied_groups(node_coords, representative_ids):
    """Assign each non-representative node to its nearest representative.

    Parameters
    ----------
    node_coords : dict
        {node_id: (x, y)} for all nodes in the group.
    representative_ids : list of int
        Node IDs selected as representatives (1-based).

    Returns
    -------
    dict
        {tied_node_id: representative_node_id} for all non-representative nodes.
    dict
        {representative_node_id: [list of tied node IDs]} — the groups.
    """
    if not representative_ids:
        return {}, {}

    rep_set = set(representative_ids)
    all_ids = sorted(node_coords.keys())

    # Build representative coordinate array
    rep_xy = np.array([node_coords[r] for r in representative_ids])

    tied_to_rep = {}
    groups = {r: [] for r in representative_ids}

    for nid in all_ids:
        if nid in rep_set:
            continue

        # Find nearest representative
        xy = np.array(node_coords[nid])
        dists = np.sqrt(np.sum((rep_xy - xy) ** 2, axis=1))
        nearest_idx = np.argmin(dists)
        nearest_rep = representative_ids[nearest_idx]

        tied_to_rep[nid] = nearest_rep
        groups[nearest_rep].append(nid)

    return tied_to_rep, groups


def build_stream_tied_groups(stream_node_ids, representative_ids,
                             gw_node_for_stream=None, node_coords=None):
    """Assign stream nodes to nearest representative stream node.

    Stream nodes are ordered along reaches, so tying is sequential:
    each non-representative stream node ties to the nearest representative
    by stream node ID distance (topological proximity along reach).

    If gw_node_for_stream and node_coords are provided, uses spatial
    distance instead.

    Parameters
    ----------
    stream_node_ids : list of int
        All stream node IDs (1-based, sequential).
    representative_ids : list of int
        Selected representative stream node IDs.
    gw_node_for_stream : dict, optional
        {stream_node_id: gw_node_id} mapping stream to GW nodes.
    node_coords : dict, optional
        {gw_node_id: (x, y)} for spatial distance.

    Returns
    -------
    dict
        {tied_stream_node: representative_stream_node}.
    dict
        {representative_stream_node: [list of tied stream nodes]}.
    """
    rep_set = set(representative_ids)
    rep_sorted = sorted(representative_ids)

    tied_to_rep = {}
    groups = {r: [] for r in representative_ids}

    use_spatial = (gw_node_for_stream is not None and
                   node_coords is not None)

    if use_spatial:
        # Spatial assignment
        rep_xy = np.array([node_coords[gw_node_for_stream[r]]
                           for r in rep_sorted])
        for sn in stream_node_ids:
            if sn in rep_set:
                continue
            gw = gw_node_for_stream.get(sn)
            if gw is None or gw not in node_coords:
                # Fallback to topological
                nearest = _nearest_by_id(sn, rep_sorted)
                tied_to_rep[sn] = nearest
                groups[nearest].append(sn)
                continue
            xy = np.array(node_coords[gw])
            dists = np.sqrt(np.sum((rep_xy - xy) ** 2, axis=1))
            nearest_rep = rep_sorted[np.argmin(dists)]
            tied_to_rep[sn] = nearest_rep
            groups[nearest_rep].append(sn)
    else:
        # Topological assignment (nearest by stream node ID)
        for sn in stream_node_ids:
            if sn in rep_set:
                continue
            nearest = _nearest_by_id(sn, rep_sorted)
            tied_to_rep[sn] = nearest
            groups[nearest].append(sn)

    return tied_to_rep, groups


def _nearest_by_id(node_id, sorted_reps):
    """Find nearest representative by absolute ID difference."""
    best = sorted_reps[0]
    best_dist = abs(node_id - best)
    for r in sorted_reps[1:]:
        d = abs(node_id - r)
        if d < best_dist:
            best = r
            best_dist = d
    return best
