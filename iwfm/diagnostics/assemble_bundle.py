# assemble_bundle.py
# Orchestrate readers and detectors into a DiagnosticBundle
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

import os
from datetime import datetime
from iwfm.diagnostics.diag_dataclasses import (
    DiagnosticBundle, StructuralSignals, PestStateSummary,
)
from iwfm.diagnostics.read_convergence_hdf import read_convergence_hdf
from iwfm.diagnostics.read_elemmb_hdf import read_elemmb_hdf
from iwfm.diagnostics.read_stream_hdf import read_stream_hdf
from iwfm.diagnostics.read_residual_hdf import read_residual_hdf
from iwfm.diagnostics.read_pest_state import read_pest_state
from iwfm.diagnostics.detect_residual_clusters import detect_residual_clusters
from iwfm.diagnostics.detect_params_at_bounds import detect_params_at_bounds
from iwfm.diagnostics.detect_convergence_trouble import detect_convergence_trouble
from iwfm.diagnostics.detect_stream_gw_anomalies import detect_stream_gw_anomalies
from iwfm.diagnostics.detect_mass_balance_hotspots import detect_mass_balance_hotspots


def assemble_bundle(diagnostics_dir, model_name='IWFM', pest_iteration=0,
                    n_gw_nodes=0, n_elements=0, n_layers=4,
                    n_stream_nodes=0, max_iter_store=50,
                    convergence_file=None, elemmb_file=None,
                    stream_file=None, residual_file=None,
                    pest_res_file=None, pest_rec_file=None,
                    pest_par_file=None, pest_pst_file=None,
                    pest_sen_file=None, param_bounds=None,
                    node_coords=None, last_n_timesteps=12,
                    verbose=False):
    """Assemble a complete DiagnosticBundle from HDF5 files and PEST state.

    Parameters
    ----------
    diagnostics_dir : str
        Directory containing diagnostic HDF5 files.
    model_name : str
        Model identifier for the bundle.
    pest_iteration : int
        Current PEST iteration number.
    n_gw_nodes : int
        Number of groundwater nodes per layer.
    n_elements : int
        Number of model elements.
    n_layers : int
        Number of model layers.
    n_stream_nodes : int
        Number of stream nodes.
    max_iter_store : int
        Max N-R iterations stored per timestep in residual file.
    convergence_file : str, optional
        Override filename for convergence HDF5.
    elemmb_file : str, optional
        Override filename for element mass balance HDF5.
    stream_file : str, optional
        Override filename for stream diagnostics HDF5.
    residual_file : str, optional
        Override filename for residual history HDF5.
    pest_res_file : str, optional
        Path to PEST .res file.
    pest_rec_file : str, optional
        Path to PEST .rec file.
    pest_par_file : str, optional
        Path to PEST .par file.
    param_bounds : dict, optional
        Parameter bounds: {name: (lower, upper)}.
    node_coords : list of (float, float), optional
        XY coordinates per node for spatial clustering.
    last_n_timesteps : int
        Number of recent timesteps for residual/stream analysis.
    verbose : bool
        Print progress.

    Returns
    -------
    DiagnosticBundle
    """
    # Default file names
    conv_path = os.path.join(diagnostics_dir,
                             convergence_file or 'Diagnostics_Convergence.hdf')
    mb_path = os.path.join(diagnostics_dir,
                           elemmb_file or 'Diagnostics_ElemMB.hdf')
    strm_path = os.path.join(diagnostics_dir,
                             stream_file or 'Diagnostics_Stream.hdf')
    res_path = os.path.join(diagnostics_dir,
                            residual_file or 'Diagnostics_Residual.hdf')

    # Read convergence (always available if dir exists)
    convergence = None
    if os.path.exists(conv_path):
        if verbose:
            print('Reading convergence...')
        convergence = read_convergence_hdf(conv_path, verbose=verbose)

    # Read element mass balance
    mass_balance = None
    if os.path.exists(mb_path) and n_elements > 0:
        if verbose:
            print('Reading element mass balance...')
        mass_balance = read_elemmb_hdf(mb_path, n_elements, n_layers,
                                       verbose=verbose)

    # Read stream diagnostics
    streams = None
    if os.path.exists(strm_path):
        if verbose:
            print('Reading stream diagnostics...')
        streams = read_stream_hdf(strm_path,
                                  last_n_timesteps=last_n_timesteps,
                                  verbose=verbose)

    # Read residual history (chunked)
    residuals = None
    if os.path.exists(res_path) and n_gw_nodes > 0:
        if verbose:
            print('Reading residual history (chunked)...')
        residuals = read_residual_hdf(
            res_path, n_gw_nodes, n_layers,
            max_iter_store=max_iter_store,
            last_n_timesteps=last_n_timesteps,
            verbose=verbose,
        )

    # Read PEST state
    pest_state = read_pest_state(
        res_file=pest_res_file, rec_file=pest_rec_file,
        par_file=pest_par_file, pst_file=pest_pst_file,
        sen_file=pest_sen_file, param_bounds=param_bounds,
        iteration=pest_iteration, verbose=verbose,
    )

    # Run signal detectors
    signals = StructuralSignals()

    if residuals:
        signals.residual_cluster_nodes = detect_residual_clusters(
            residuals, node_coords=node_coords)

    if convergence:
        signals.convergence_trouble_timesteps = detect_convergence_trouble(
            convergence)

    if streams:
        signals.stream_gw_anomalies = detect_stream_gw_anomalies(streams)

    if mass_balance:
        signals.mass_balance_hotspots = detect_mass_balance_hotspots(
            mass_balance)

    if pest_state:
        signals.params_at_bounds = detect_params_at_bounds(pest_state)

    # Generate rule-based hypothesis
    signals.hypothesis = _generate_hypothesis(signals, convergence,
                                              mass_balance, residuals)

    # Get n_timesteps from convergence HDF5 if available
    n_timesteps = 0
    if os.path.exists(conv_path):
        import h5py
        with h5py.File(conv_path, 'r') as f:
            n_timesteps = f['/ConvergenceSummary'].shape[0]

    bundle = DiagnosticBundle(
        model_name=model_name,
        pest_iteration=pest_iteration,
        timestamp=datetime.now().isoformat(timespec='seconds'),
        model_dimensions={
            'n_nodes': n_gw_nodes,
            'n_elements': n_elements,
            'n_layers': n_layers,
            'n_timesteps': n_timesteps,
            'n_stream_nodes': n_stream_nodes,
        },
        convergence=convergence,
        residuals=residuals,
        mass_balance=mass_balance,
        streams=streams,
        pest_state=pest_state,
        structural_signals=signals,
    )

    return bundle


def _generate_hypothesis(signals, convergence, mass_balance, residuals):
    """Build a rule-based hypothesis string from co-location patterns."""
    parts = []

    # Check mass balance + convergence co-location
    if signals.mass_balance_hotspots and signals.convergence_trouble_timesteps:
        mb_elems = [h['element_id'] for h in signals.mass_balance_hotspots[:3]]
        trouble_nodes = [t['node'] for t in signals.convergence_trouble_timesteps[:3]]
        parts.append(
            f'Mass balance hotspots at elements {mb_elems} co-occur with '
            f'convergence trouble at nodes {trouble_nodes}.'
        )

    # Check params at bounds + high residuals
    if signals.params_at_bounds and residuals and residuals.worst_nodes:
        param_names = [p['name'] for p in signals.params_at_bounds[:3]]
        worst = residuals.worst_nodes[0]
        parts.append(
            f'Parameters {param_names} pinned at bounds while node '
            f'{worst["node_id"]} L{worst["layer"]} has high residuals.'
        )

    # Check stream anomalies + convergence
    if signals.stream_gw_anomalies and signals.convergence_trouble_timesteps:
        strm_nodes = [a['node_id'] for a in signals.stream_gw_anomalies[:3]]
        parts.append(
            f'Stream-GW anomalies at nodes {strm_nodes} may indicate '
            f'stream conductance or geometry issues.'
        )

    if not parts:
        if convergence and convergence.pct_timesteps_at_max > 10:
            parts.append(
                f'{convergence.pct_timesteps_at_max:.0f}% of timesteps hit '
                f'max iterations — general convergence difficulty.'
            )

    return ' '.join(parts) if parts else 'No strong structural signals detected.'
