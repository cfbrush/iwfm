# detect_mass_balance_hotspots.py
# Detect elements with persistent mass balance residuals
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+


'''Identify elements with residuals far above the layer mean.'''

def detect_mass_balance_hotspots(mb_summary, threshold_multiplier=5.0):
    """Identify elements with residuals far above the layer mean.

    Parameters
    ----------
    mb_summary : MassBalanceSummary
        From read_elemmb_hdf.
    threshold_multiplier : float
        Flag elements where mean abs(residual) exceeds this multiple
        of the layer mean.

    Returns
    -------
    list of dict
        [{element_id, layer, mean_abs_residual, max_abs_residual, ratio}]
    """
    layer_means = mb_summary.mean_abs_residual_by_layer
    results = []

    for elem in mb_summary.hotspot_elements:
        layer_idx = elem['layer'] - 1  # 0-based
        if layer_idx < len(layer_means) and layer_means[layer_idx] > 0:
            ratio = elem['mean_abs_residual'] / layer_means[layer_idx]
        else:
            ratio = 0.0

        if ratio >= threshold_multiplier:
            results.append({
                'element_id': elem['element_id'],
                'layer': elem['layer'],
                'mean_abs_residual': elem['mean_abs_residual'],
                'max_abs_residual': elem['max_abs_residual'],
                'ratio': float(ratio),
            })

    return results
