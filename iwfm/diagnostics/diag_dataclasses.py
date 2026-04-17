# diag_dataclasses.py
# Dataclass definitions for IWFM diagnostic bundle
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class ConvergenceSummary:
    """Per-timestep convergence statistics from Diagnostics_Convergence.hdf."""
    mean_iterations: float = 0.0
    max_iterations: int = 0
    pct_timesteps_at_max: float = 0.0
    mean_diffmax: float = 0.0
    max_diffmax: float = 0.0
    mean_rhs_l2_ratio: float = 0.0
    trouble_timesteps: List[Dict] = field(default_factory=list)


@dataclass
class ResidualSummary:
    """Per-node residual statistics from Diagnostics_Residual.hdf."""
    rhs_l2_by_layer: List[float] = field(default_factory=list)
    hdelta_l2_by_layer: List[float] = field(default_factory=list)
    worst_nodes: List[Dict] = field(default_factory=list)
    mean_iterations_to_converge: float = 0.0


@dataclass
class MassBalanceSummary:
    """Element mass balance statistics from Diagnostics_ElemMB.hdf."""
    mean_abs_residual_by_layer: List[float] = field(default_factory=list)
    max_abs_residual: float = 0.0
    hotspot_elements: List[Dict] = field(default_factory=list)
    pct_elements_above_threshold: float = 0.0


@dataclass
class StreamSummary:
    """Stream node diagnostics from Diagnostics_Stream.hdf."""
    mean_stream_gw_flow: float = 0.0
    max_abs_stream_gw_flow: float = 0.0
    gaining_reach_count: int = 0
    losing_reach_count: int = 0
    anomaly_nodes: List[Dict] = field(default_factory=list)


@dataclass
class PestStateSummary:
    """PEST iteration state from .res/.rec/.par files."""
    iteration: int = 0
    phi: float = 0.0
    n_observations: int = 0
    rmse: float = 0.0
    bias: float = 0.0
    obs_group_stats: List[Dict] = field(default_factory=list)
    params_at_bounds: List[Dict] = field(default_factory=list)


@dataclass
class StructuralSignals:
    """Derived structural diagnostic indicators."""
    residual_cluster_nodes: List[Dict] = field(default_factory=list)
    convergence_trouble_timesteps: List[Dict] = field(default_factory=list)
    stream_gw_anomalies: List[Dict] = field(default_factory=list)
    mass_balance_hotspots: List[Dict] = field(default_factory=list)
    params_at_bounds: List[Dict] = field(default_factory=list)
    hypothesis: str = ''


@dataclass
class StabilityJacobianSummary:
    """Per-parameter stability impact from Jacobian perturbation runs.

    Identifies parameters that destabilize model convergence when
    perturbed — structural hotspots that wreck calibration.
    """
    n_params: int = 0
    n_timesteps: int = 0
    base_max_iter: int = 0
    base_mean_iter: float = 0.0
    base_max_diffmax: float = 0.0
    base_n_trouble: int = 0
    param_scores: List[Dict] = field(default_factory=list)
    top_destabilizers: List[Dict] = field(default_factory=list)
    n_destabilizing: int = 0
    mean_stability_score: float = 0.0
    max_stability_score: float = 0.0


@dataclass
class DiagnosticBundle:
    """Complete diagnostic bundle for one PEST iteration."""
    model_name: str = ''
    pest_iteration: int = 0
    timestamp: str = ''
    model_dimensions: Dict = field(default_factory=dict)
    convergence: Optional[ConvergenceSummary] = None
    residuals: Optional[ResidualSummary] = None
    mass_balance: Optional[MassBalanceSummary] = None
    streams: Optional[StreamSummary] = None
    pest_state: Optional[PestStateSummary] = None
    structural_signals: Optional[StructuralSignals] = None
    stability_jacobian: Optional[StabilityJacobianSummary] = None

    def to_dict(self):
        """Convert to plain dict for JSON serialization."""
        return asdict(self)
