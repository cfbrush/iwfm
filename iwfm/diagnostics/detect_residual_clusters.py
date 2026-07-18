# detect_residual_clusters.py
# Detect spatially clustered high-residual nodes
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Detect spatially clustered high-residual nodes.'''

import numpy as np


def detect_residual_clusters(residual_summary, node_coords=None,
                             z_threshold=2.0):
    """Identify nodes with persistently high residuals.

    If node_coords are provided, groups flagged nodes by spatial
    proximity. Otherwise returns a flat list of outlier nodes.

    Parameters
    ----------
    residual_summary : ResidualSummary
        From read_residual_hdf.
    node_coords : list of (float, float), optional
        XY coordinates per node (1-indexed matching node_id).
    z_threshold : float
        Z-score threshold for flagging outlier nodes.

    Returns
    -------
    list of dict
        [{node_id, layer, mean_rhs, z_score, cluster_id?}]
    """
    worst = residual_summary.worst_nodes
    if not worst:
        return []

    rhs_vals = np.array([n['mean_rhs'] for n in worst])
    mean_rhs = np.mean(rhs_vals)
    std_rhs = np.std(rhs_vals)

    if std_rhs < 1e-15:
        return []

    results = []
    for node in worst:
        z = (node['mean_rhs'] - mean_rhs) / std_rhs
        if z >= z_threshold:
            entry = {
                'node_id': node['node_id'],
                'layer': node['layer'],
                'mean_rhs': node['mean_rhs'],
                'z_score': float(z),
            }
            results.append(entry)

    # Spatial clustering if coordinates available
    if node_coords and len(results) > 1:
        _add_spatial_clusters(results, node_coords, distance_threshold=5000.0)

    return results


def _add_spatial_clusters(nodes, node_coords, distance_threshold):
    """Group flagged nodes by spatial proximity using union-find."""
    n = len(nodes)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(n):
        nid_i = nodes[i]['node_id'] - 1  # 0-based index into coords
        if nid_i >= len(node_coords):
            continue
        xi, yi = node_coords[nid_i]
        for j in range(i + 1, n):
            nid_j = nodes[j]['node_id'] - 1
            if nid_j >= len(node_coords):
                continue
            xj, yj = node_coords[nid_j]
            dist = ((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5
            if dist <= distance_threshold:
                union(i, j)

    for i, node in enumerate(nodes):
        node['cluster_id'] = find(i)
