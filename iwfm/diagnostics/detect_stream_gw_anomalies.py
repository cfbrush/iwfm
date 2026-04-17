# detect_stream_gw_anomalies.py
# Detect anomalous stream-groundwater exchange nodes
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+


def detect_stream_gw_anomalies(stream_summary, z_threshold=3.0):
    """Extract anomalous stream nodes from StreamSummary.

    Parameters
    ----------
    stream_summary : StreamSummary
        From read_stream_hdf.
    z_threshold : float
        Minimum z-score to include in results.

    Returns
    -------
    list of dict
        [{node_id, mean_strmgw, std_strmgw, z_score, flag}]
    """
    results = []
    for node in stream_summary.anomaly_nodes:
        z = node.get('z_score', 0.0)
        if z >= z_threshold:
            results.append({
                'node_id': node['node_id'],
                'mean_strmgw': node['mean_strmgw'],
                'std_strmgw': node['std_strmgw'],
                'z_score': z,
                'flag': node['flag'],
            })
    return results
