# iwfm/diagnostics/__init__.py
# IWFM Structural Diagnostics Module
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

from iwfm.diagnostics.diag_dataclasses import (
    DiagnosticBundle,
    ConvergenceSummary,
    ResidualSummary,
    MassBalanceSummary,
    StreamSummary,
    PestStateSummary,
    StructuralSignals,
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
from iwfm.diagnostics.assemble_bundle import assemble_bundle
from iwfm.diagnostics.serialize_bundle import serialize_bundle
from iwfm.diagnostics.read_pest_sensitivity import read_pest_sensitivity
from iwfm.diagnostics.select_parameters import select_parameters
from iwfm.diagnostics.build_tied_groups import build_tied_groups
from iwfm.diagnostics.suggest_parameter_changes import suggest_parameter_changes
from iwfm.diagnostics.write_pest_control import write_pest_control
from iwfm.diagnostics.setup_pest_run import setup_pest_run
from iwfm.diagnostics.parse_model_geometry import (
    parse_node_coords, parse_pst_param_nodes, parse_stream_nodes,
)
from iwfm.diagnostics.iteration_callback import iteration_callback
