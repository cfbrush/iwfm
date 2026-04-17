# read_pest_sensitivity.py
# Parse PEST .sen file for parameter sensitivities
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+


def read_pest_sensitivity(sen_file, iteration=None, verbose=False):
    """Parse PEST .sen file and return parameter sensitivities.

    Parameters
    ----------
    sen_file : str
        Path to PEST .sen file.
    iteration : int, optional
        Return sensitivities for this iteration only. If None, return
        the last iteration.
    verbose : bool
        Print progress.

    Returns
    -------
    dict
        {param_name: {'group': str, 'value': float, 'sensitivity': float}}
        for the requested iteration.
    int
        Iteration number returned.
    """
    iterations = {}  # {iter_num: {param_name: {group, value, sensitivity}}}
    current_iter = None

    with open(sen_file) as f:
        for line in f:
            stripped = line.strip()

            # Detect iteration header
            if 'OPTIMISATION ITERATION NO.' in stripped:
                # Extract iteration number
                parts = stripped.split()
                for i, p in enumerate(parts):
                    if p == 'NO.':
                        try:
                            current_iter = int(parts[i + 1])
                        except (ValueError, IndexError):
                            pass
                        break
                if current_iter is not None:
                    iterations[current_iter] = {}
                continue

            if current_iter is None:
                continue

            # Skip header lines
            if stripped.startswith('Parameter') or not stripped:
                continue

            # Parse: name  group  value  sensitivity
            parts = stripped.split()
            if len(parts) < 4:
                continue

            name = parts[0]
            group = parts[1]
            try:
                value = float(parts[2])
                sensitivity = float(parts[3])
            except (ValueError, IndexError):
                continue

            iterations[current_iter][name] = {
                'group': group,
                'value': value,
                'sensitivity': sensitivity,
            }

    if not iterations:
        return {}, 0

    # Select requested iteration
    if iteration is not None and iteration in iterations:
        selected_iter = iteration
    else:
        selected_iter = max(iterations.keys())

    result = iterations[selected_iter]

    if verbose:
        print(f'  Sensitivity: iteration {selected_iter}, '
              f'{len(result)} parameters')
        # Top 5 by sensitivity
        ranked = sorted(result.items(),
                        key=lambda x: abs(x[1]['sensitivity']),
                        reverse=True)
        for name, info in ranked[:5]:
            print(f'    {name}: sensitivity={info["sensitivity"]:.4e}')

    return result, selected_iter
