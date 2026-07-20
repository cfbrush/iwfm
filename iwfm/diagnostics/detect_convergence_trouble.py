# detect_convergence_trouble.py
# Detect timesteps with convergence problems
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+


'''Extract trouble timesteps from ConvergenceSummary.'''

def detect_convergence_trouble(convergence, iter_threshold=40,
                               diffmax_threshold=0.1):
    """Extract trouble timesteps from ConvergenceSummary.

    Parameters
    ----------
    convergence : ConvergenceSummary
        From read_convergence_hdf.
    iter_threshold : int
        Flag timesteps with iterations >= this.
    diffmax_threshold : float
        Flag timesteps with abs(DIFFMAX) >= this.

    Returns
    -------
    list of dict
        [{timestep_index, diffmax, iterations, node, layer}]
    """
    results = []
    for ts in convergence.trouble_timesteps:
        if (ts['iterations'] >= iter_threshold or
                abs(ts['diffmax']) >= diffmax_threshold):
            results.append({
                'timestep_index': ts['timestep_index'],
                'diffmax': ts['diffmax'],
                'iterations': ts['iterations'],
                'node': ts['node'],
                'layer': ts['layer'],
            })
    return results
