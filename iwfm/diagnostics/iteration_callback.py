# iteration_callback.py
# Post-iteration callback: assemble bundle, serialize, optionally apply changes
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Post-iteration callback for LLM-supervised PEST.'''

import os
import json

from iwfm.diagnostics.assemble_bundle import assemble_bundle
from iwfm.diagnostics.serialize_bundle import serialize_bundle
from iwfm.diagnostics.read_pest_sensitivity import read_pest_sensitivity
from iwfm.diagnostics.suggest_parameter_changes import suggest_parameter_changes
from iwfm.diagnostics.write_pest_control import write_pest_control
from iwfm.diagnostics.parse_model_geometry import parse_node_coords


def iteration_callback(pest_dir, iteration=None, model_config=None,
                       apply_changes=False, stability_result=None,
                       verbose=False):
    """Post-iteration callback for LLM-supervised PEST.

    Assembles diagnostic bundle from HDF5 files and PEST output,
    serializes to JSON, optionally generates and applies parameter
    change recommendations.

    Designed to be called between PEST iterations, either by the
    LLM supervisor loop or as a standalone diagnostic tool.

    Parameters
    ----------
    pest_dir : str
        Root PEST run directory (contains .pst, .res, .rec, .par,
        .sen files, model/ and diagnostics/ subdirectories).
    iteration : int, optional
        Current PEST iteration number. If None, auto-detected from
        .rec file.
    model_config : dict, optional
        Model dimensions override. If None, uses C2VSimCG defaults.
    apply_changes : bool
        If True, generate parameter recommendations and write a
        new .pst file. If False, only produce diagnostic bundle.
    stability_result : StabilityJacobian, optional
        Stability Jacobian from StabilityCollector.compute().
        If provided, attached to the diagnostic bundle.
    verbose : bool
        Print progress.

    Returns
    -------
    dict
        Result dictionary::

            {
                'bundle_json': str,          # Serialized diagnostic bundle
                'bundle': DiagnosticBundle,  # Full bundle object
                'recommendations': dict,     # Parameter recommendations (if apply_changes)
                'output_pst': str,           # Path to new .pst (if apply_changes)
                'iteration': int,
            }
    """
    # Default model config for C2VSimCG
    if model_config is None:
        model_config = {
            'model_name': 'C2VSimCG',
            'n_gw_nodes': 1393,
            'n_elements': 1392,
            'n_layers': 4,
            'n_stream_nodes': 663,
            'max_iter_store': 50,
            'last_n_timesteps': 12,
        }

    # Locate files
    diag_dir = os.path.join(pest_dir, 'diagnostics')
    pst_file = _find_file(pest_dir, '.pst', prefix='c2vsim_diag')
    res_file = _find_latest(pest_dir, '.res')
    rec_file = _find_latest(pest_dir, '.rec')
    par_file = _find_latest(pest_dir, '.par')
    sen_file = _find_latest(pest_dir, '.sen')
    node_file = os.path.join(pest_dir, 'model', 'C2VSimCG_Nodes.dat')

    if verbose:
        print(f'PEST dir: {pest_dir}')
        print(f'PST: {pst_file}')
        print(f'RES: {res_file}')
        print(f'SEN: {sen_file}')
        print(f'Diagnostics: {diag_dir}')

    # Step 1: Assemble diagnostic bundle
    bundle = assemble_bundle(
        diagnostics_dir=diag_dir,
        pest_iteration=iteration or 0,
        pest_res_file=res_file,
        pest_rec_file=rec_file,
        pest_par_file=par_file,
        pest_pst_file=pst_file,
        pest_sen_file=sen_file,
        verbose=verbose,
        **model_config,
    )

    # Update iteration from bundle if auto-detected
    if iteration is None:
        iteration = bundle.pest_state.iteration if bundle.pest_state else 0

    # Attach stability Jacobian if provided
    if stability_result is not None:
        from iwfm.diagnostics.diag_dataclasses import StabilityJacobianSummary
        # Convert StabilityJacobian → StabilityJacobianSummary for bundle
        if hasattr(stability_result, 'n_params'):
            bundle.stability_jacobian = StabilityJacobianSummary(
                n_params=stability_result.n_params,
                n_timesteps=stability_result.n_timesteps,
                base_max_iter=stability_result.base_max_iter,
                base_mean_iter=stability_result.base_mean_iter,
                base_max_diffmax=stability_result.base_max_diffmax,
                base_n_trouble=stability_result.base_n_trouble,
                param_scores=stability_result.param_scores,
                top_destabilizers=stability_result.top_destabilizers,
                n_destabilizing=stability_result.n_destabilizing,
                mean_stability_score=stability_result.mean_stability_score,
                max_stability_score=stability_result.max_stability_score,
            )

    # Step 2: Serialize to JSON
    bundle_json = serialize_bundle(bundle, max_list_items=5, float_precision=3)

    # Save bundle to file
    bundle_path = os.path.join(pest_dir, f'diagnostics_iter_{iteration:03d}.json')
    with open(bundle_path, 'w', encoding='utf-8') as f:
        f.write(bundle_json)

    if verbose:
        print(f'\nBundle saved: {bundle_path} ({len(bundle_json)} bytes)')

    result = {
        'bundle_json': bundle_json,
        'bundle': bundle,
        'recommendations': None,
        'output_pst': None,
        'iteration': iteration,
    }

    # Step 3: Generate and apply parameter changes (if requested)
    if apply_changes and pst_file:
        sensitivity = {}
        if sen_file:
            sensitivity, _ = read_pest_sensitivity(sen_file, verbose=verbose)

        node_coords = {}
        if os.path.exists(node_file):
            node_coords = parse_node_coords(node_file)

        stream_nodes = list(range(1, model_config['n_stream_nodes'] + 1))

        recs = suggest_parameter_changes(
            bundle, sensitivity, node_coords,
            stream_node_ids=stream_nodes,
            n_reps_per_group=25,
            pst_file=pst_file,
            diagnostic_weight=0.3,
            verbose=verbose,
        )

        # Write new .pst (backup original first)
        base, _ = os.path.splitext(pst_file)
        new_pst = f'{base}_iter{iteration:03d}.pst'
        write_pest_control(pst_file, new_pst, recs, verbose=verbose)

        # Save recommendations
        recs_path = os.path.join(pest_dir,
                                 f'recommendations_iter_{iteration:03d}.json')
        recs_serializable = {
            'phase': recs['phase'],
            'summary': recs['summary'],
            'bound_changes': recs['bound_changes'][:20],
            'param_groups': {
                k: {'n_reps': v['n_reps'], 'n_tied': v['n_tied'],
                     'representatives': v['representatives'][:10]}
                for k, v in recs['param_groups'].items()
            },
        }
        with open(recs_path, 'w', encoding='utf-8') as f:
            json.dump(recs_serializable, f, indent=2)

        result['recommendations'] = recs
        result['output_pst'] = new_pst

        if verbose:
            print(f'\n{recs["summary"]}')
            print(f'New PST: {new_pst}')
            print(f'Recommendations: {recs_path}')

    return result


def _find_file(directory, extension, prefix=None):
    """Find a file by extension and optional prefix."""
    for entry in os.listdir(directory):
        if entry.endswith(extension):
            if prefix is None or entry.startswith(prefix):
                return os.path.join(directory, entry)
    return None


def _find_latest(directory, extension):
    """Find the most recently modified file with given extension."""
    candidates = []
    for entry in os.listdir(directory):
        if entry.endswith(extension):
            path = os.path.join(directory, entry)
            candidates.append((os.path.getmtime(path), path))

    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


# Command-line interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='PEST iteration diagnostic callback')
    parser.add_argument('pest_dir',
                        help='PEST run directory')
    parser.add_argument('--iteration', type=int, default=None,
                        help='Iteration number (auto-detect if omitted)')
    parser.add_argument('--apply-changes', action='store_true',
                        help='Generate and write parameter recommendations')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print progress')

    args = parser.parse_args()

    result = iteration_callback(
        args.pest_dir,
        iteration=args.iteration,
        apply_changes=args.apply_changes,
        verbose=args.verbose,
    )

    # Print bundle JSON to stdout
    print(result['bundle_json'])
