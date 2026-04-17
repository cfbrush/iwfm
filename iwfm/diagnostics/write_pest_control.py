# write_pest_control.py
# Write PEST .pst control file from parameter recommendations
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

import os


def write_pest_control(template_pst, output_pst, recommendations,
                       initial_values=None, verbose=False):
    """Write a new .pst file applying parameter selection recommendations.

    Reads the template .pst, modifies the parameter data and tied
    parameter data sections based on recommendations from
    suggest_parameter_changes, and writes a new .pst file.

    Parameters
    ----------
    template_pst : str
        Path to existing .pst file to use as template.
    output_pst : str
        Path for the new .pst file.
    recommendations : dict
        From suggest_parameter_changes(). Contains 'param_groups'
        with representative/tied assignments, and 'bound_changes'.
    initial_values : dict, optional
        {param_name: initial_value}. If None, uses values from
        template .pst.
    verbose : bool
        Print progress.

    Returns
    -------
    dict
        Summary: {'n_adjustable': int, 'n_tied': int, 'n_fixed': int,
                  'n_total': int}.
    """
    # Parse template .pst
    sections = _parse_pst(template_pst)

    # Build lookup of current parameter values from template
    param_values = {}
    for p in sections['param_data']:
        param_values[p['name']] = p['initial']

    if initial_values:
        param_values.update(initial_values)

    # Build new parameter assignments from recommendations
    # Start with all params from template
    new_params = {p['name']: dict(p) for p in sections['param_data']}

    # Build representative and tied sets from recommendations
    rep_set = set()      # param names that should be 'none' (adjustable)
    tied_map = {}        # {tied_param_name: rep_param_name}
    bound_changes = {}   # {param_name: {'lower': x, 'upper': y}}

    for group_key, ginfo in recommendations['param_groups'].items():
        prefix = ginfo['prefix']
        layer = ginfo['layer']
        reps = ginfo['representatives']
        tmap = ginfo['tied_map']

        for node_id in reps:
            pname = _make_param_name(prefix, node_id, layer)
            if pname in new_params:
                rep_set.add(pname)

        for tied_node, rep_node in tmap.items():
            tied_pname = _make_param_name(prefix, tied_node, layer)
            rep_pname = _make_param_name(prefix, rep_node, layer)
            if tied_pname in new_params and rep_pname in new_params:
                tied_map[tied_pname] = rep_pname

    # Apply bound changes
    for bc in recommendations.get('bound_changes', []):
        name = bc['name']
        if name not in new_params:
            continue
        if bc['action'] == 'extend_upper':
            bound_changes[name] = {
                'upper': bc['new_upper'],
                'lower': new_params[name]['lower'],
            }
        elif bc['action'] == 'extend_lower':
            bound_changes[name] = {
                'lower': bc['new_lower'],
                'upper': new_params[name]['upper'],
            }

    # Also widen bounds for all representatives to use config multiplier
    for group_key, ginfo in recommendations['param_groups'].items():
        prefix = ginfo['prefix']
        layer = ginfo['layer']
        for node_id in ginfo['representatives']:
            pname = _make_param_name(prefix, node_id, layer)
            if pname in new_params and pname not in bound_changes:
                val = param_values.get(pname, new_params[pname]['initial'])
                if val > 0:
                    mult = 10.0
                    bound_changes[pname] = {
                        'lower': val / mult,
                        'upper': val * mult,
                    }

    # Update parameter entries
    n_adjustable = 0
    n_tied = 0
    n_fixed = 0

    for pname, pdata in new_params.items():
        if pname in rep_set:
            pdata['transform'] = 'none'
            n_adjustable += 1
        elif pname in tied_map:
            pdata['transform'] = 'tied'
            n_tied += 1
        else:
            # Keep as fixed (global factors or unused params)
            pdata['transform'] = 'fixed'
            n_fixed += 1

        if pname in bound_changes:
            pdata['lower'] = bound_changes[pname]['lower']
            pdata['upper'] = bound_changes[pname]['upper']

    # Validate: every tied param must reference an adjustable parent
    for child, parent in tied_map.items():
        if parent not in rep_set:
            raise ValueError(
                f'Tied param {child} references {parent} which is not '
                f'adjustable (not in rep_set). PEST requires tied params '
                f'to reference an adjustable parent.')

    # Write new .pst
    _write_pst(sections, new_params, tied_map, output_pst)

    summary = {
        'n_adjustable': n_adjustable,
        'n_tied': n_tied,
        'n_fixed': n_fixed,
        'n_total': len(new_params),
    }

    if verbose:
        print(f'  PST written: {output_pst}')
        print(f'    {n_adjustable} adjustable, {n_tied} tied, '
              f'{n_fixed} fixed ({len(new_params)} total)')

    return summary


def _make_param_name(prefix, node_id, layer):
    """Build PEST parameter name from prefix, node ID, and layer."""
    if prefix == 'c_sn':
        return f'c_sn_{node_id:03d}'
    return f'{prefix}{node_id:03d}_L{layer}'


def _parse_pst(pst_path):
    """Parse .pst file into sections."""
    sections = {
        'header_lines': [],       # Everything before * parameter data
        'param_groups_lines': [], # * parameter groups section
        'param_data': [],         # Parsed parameter dicts
        'obs_section': [],        # Everything from * observation groups onward
    }

    with open(pst_path) as f:
        lines = f.readlines()

    # Find section boundaries
    param_data_start = None
    obs_groups_start = None
    param_groups_start = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '* parameter groups':
            param_groups_start = i
        elif stripped == '* parameter data':
            param_data_start = i
        elif stripped == '* observation groups':
            obs_groups_start = i
            break

    # Header: everything before * parameter groups
    sections['header_lines'] = lines[:param_groups_start]

    # Parameter groups
    sections['param_groups_lines'] = lines[param_groups_start:param_data_start]

    # Parse parameter data
    # Lines between * parameter data and * observation groups
    # But tied parameter data lines (2-column) are mixed in after main params
    param_lines = lines[param_data_start + 1:obs_groups_start]

    for line in param_lines:
        parts = line.split()
        if len(parts) < 7:
            continue

        # Check if this is a tied data line (2 columns: child parent)
        if len(parts) == 2:
            continue  # Skip tied data lines, we regenerate these

        name = parts[0]
        transform = parts[1]
        change_type = parts[2]

        try:
            initial = float(parts[3])
            lower = float(parts[4])
            upper = float(parts[5])
        except (ValueError, IndexError):
            continue

        group = parts[6]

        # Remaining fields: scale, offset, dercom (typically "1 0 1")
        extra = parts[7:] if len(parts) > 7 else ['1', '0', '1']

        sections['param_data'].append({
            'name': name,
            'transform': transform,
            'change_type': change_type,
            'initial': initial,
            'lower': lower,
            'upper': upper,
            'group': group,
            'extra': extra,
        })

    # Observation section onward
    sections['obs_section'] = lines[obs_groups_start:]

    return sections


def _write_pst(sections, new_params, tied_map, output_path):
    """Write .pst file from parsed sections with updated parameters."""
    # Count new totals for control data line
    n_total = len(new_params)

    # Update NPAR in control data (line index 3, 0-based)
    # Format: NPAR  NOBS  NPARGP  NPRIOR  NOBSGP
    header = list(sections['header_lines'])
    for i, line in enumerate(header):
        parts = line.split()
        if len(parts) >= 5:
            try:
                int(parts[0])
                int(parts[1])
                # This is the control data line
                parts[0] = str(n_total)
                header[i] = '  ' + '    '.join(parts) + ' \n'
                break
            except ValueError:
                continue

    with open(output_path, 'w') as f:
        # Header (control data)
        for line in header:
            f.write(line)

        # Parameter groups (unchanged)
        for line in sections['param_groups_lines']:
            f.write(line)

        # Parameter data
        f.write('* parameter data\n')

        # Write in original order (preserved from template)
        ordered_names = [p['name'] for p in sections['param_data']]
        for pname in ordered_names:
            if pname not in new_params:
                continue
            p = new_params[pname]
            extra_str = ' '.join(p['extra']) if p['extra'] else '1 0 1'
            f.write(
                f'  {p["name"]:<14s} {p["transform"]:<7s} '
                f'{p["change_type"]:<7s} '
                f'{p["initial"]:<15g} {p["lower"]:<15g} '
                f'{p["upper"]:<15g} {p["group"]:<12s} {extra_str}\n'
            )

        # Tied parameter data (child -> parent mapping)
        for pname in ordered_names:
            if pname in tied_map:
                f.write(f'{pname}\t{tied_map[pname]}\n')

        # Observation section onward
        for line in sections['obs_section']:
            f.write(line)
