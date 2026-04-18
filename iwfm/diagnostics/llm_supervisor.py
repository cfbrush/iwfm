# llm_supervisor.py
# Outer-loop LLM supervisor for PEST calibration
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

"""
LLM Supervisor for IWFM/PEST calibration.

Runs an outer loop around the pypest optimizer. After each epoch (a short
optimizer run with noptmax iterations), the supervisor:

  1. Assembles a diagnostic bundle from HDF5 diagnostics + PEST state
  2. Sends it to Claude for analysis
  3. Receives structured decisions (fix/unfix params, adjust bounds, etc.)
  4. Writes a modified PST and launches the next epoch

Usage:
    from iwfm.diagnostics.llm_supervisor import LLMSupervisor

    supervisor = LLMSupervisor(
        pest_dir='/path/to/pest/run',
        pst_file='model.pst',
        max_epochs=5,
        noptmax_per_epoch=3,
    )
    result = supervisor.run()
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger('iwfm.diagnostics.supervisor')


# ── Dataclasses ─────────────────────────────────────────────────────────

@dataclass
class SupervisorDecision:
    """Structured decision from the LLM supervisor."""
    reasoning: str = ''
    diagnosis: str = ''  # 'parameter' | 'structural' | 'numerical' | 'converged'

    # PST modifications (applied between epochs)
    fix_params: List[str] = field(default_factory=list)
    unfix_params: List[str] = field(default_factory=list)
    bound_changes: List[dict] = field(default_factory=list)
    perturbation_changes: List[dict] = field(default_factory=list)

    # Runtime hints for next epoch
    initial_lambda: Optional[float] = None
    numlam: Optional[int] = None
    noptmax: Optional[int] = None

    # Control
    stop: bool = False
    human_review_flags: List[str] = field(default_factory=list)
    message: str = ''


@dataclass
class EpochResult:
    """Result from one optimizer epoch."""
    epoch: int = 0
    phi_start: float = 0.0
    phi_end: float = 0.0
    n_iterations: int = 0
    converged: bool = False
    bundle_json: str = ''
    pst_file: str = ''
    n_crashed_params: int = 0
    elapsed_seconds: float = 0.0


@dataclass
class SupervisorResult:
    """Result from the full supervisor run."""
    epochs: List[EpochResult] = field(default_factory=list)
    decisions: List[SupervisorDecision] = field(default_factory=list)
    final_phi: float = 0.0
    total_elapsed_seconds: float = 0.0
    stop_reason: str = ''


# ── System prompt ───────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are an expert groundwater model calibration supervisor for the C2VSimCG \
(California Central Valley Groundwater-Surface Water Simulation Model, Coarse Grid).

You receive a diagnostic bundle (JSON) after each calibration epoch and must \
decide how to modify the PEST parameter estimation setup for the next epoch.

## Model Structure

C2VSimCG is an IWFM finite-element groundwater model:
- 1393 GW nodes, 1392 elements, 4 aquifer layers, 663 stream nodes
- 504 monthly timesteps (WY1974–2015)
- Parameter types:
  - PKH: horizontal hydraulic conductivity (per node, per layer)
  - PL:  leakance between layers (per node, per layer)
  - PN:  specific yield / porosity (per node, per layer)
  - PS:  specific storage (per node, per layer)
  - c_sn: stream-aquifer conductance (per stream node)

## Diagnostic Signals

The bundle contains:
- **convergence**: mean/max iterations, trouble timesteps (high DIFFMAX or max iterations)
- **residuals**: RHS L2 norms by layer, worst nodes
- **mass_balance**: hotspot elements with high residuals, by layer
- **streams**: stream-GW flow anomalies, gaining/losing reach counts
- **pest_state**: phi, RMSE, bias, obs group stats, params at bounds
- **structural_signals**: co-located patterns and rule-based hypothesis
- **stability_jacobian**: params that destabilize convergence when perturbed

## Decision Taxonomy

1. **Parameter problem**: Bounds too tight, wrong initial values, too many params \
   at bounds → widen bounds, unfix promising params, fix insensitive params
2. **Structural problem**: Persistent mass balance hotspots, convergence trouble \
   at same nodes regardless of params → flag for human review, fix params in \
   problem zones to avoid wasting iterations
3. **Numerical problem**: Model crashes on perturbation, convergence failure → \
   reduce perturbation step, fix crash-prone params, or tighten bounds
4. **Converged**: phi stable, no improvement possible → stop

## Actions You Can Take

Return a JSON object with these fields (omit or set null for no change):

```json
{
  "reasoning": "Your analysis of the diagnostic bundle",
  "diagnosis": "parameter|structural|numerical|converged",
  "fix_params": ["param_name", ...],
  "unfix_params": ["param_name", ...],
  "bound_changes": [{"name": "param_name", "lower": 0.1, "upper": 100.0}, ...],
  "perturbation_changes": [{"group": "fackh", "derinc": 0.005}, ...],
  "initial_lambda": null,
  "numlam": null,
  "noptmax": null,
  "stop": false,
  "human_review_flags": [],
  "message": ""
}
```

## Rules

- Be conservative: make 5-15 changes per epoch, not 50. Watch the effect.
- If >15% of params crash the model, fix the crash-prone ones — they waste compute.
- If phi hasn't improved >1% over 2 epochs, consider structural diagnosis.
- Params at bounds with high sensitivity should get wider bounds.
- Params at bounds with low sensitivity should be fixed (save compute).
- Stream conductance params (c_sn_*) are structurally sensitive — fix crash-prone \
  ones rather than widening bounds.
- When unfixing params, start with high-sensitivity ones near calibration targets.
- Always explain your reasoning.
- Set "stop": true when further iteration is unlikely to improve phi.
- Use "human_review_flags" for issues you cannot resolve (mesh problems, data errors).
"""


# ── LLMSupervisor ──────────────────────────────────────────────────────

class LLMSupervisor:
    """Outer-loop LLM supervisor for PEST calibration.

    Parameters
    ----------
    pest_dir : str
        Root PEST run directory.
    pst_file : str
        Path to initial PST file.
    model : str
        Anthropic model ID (default: claude-sonnet-4-6).
    max_epochs : int
        Maximum number of supervisor epochs.
    noptmax_per_epoch : int
        PEST iterations per optimizer epoch.
    n_workers : int
        Parallel Jacobian workers.
    n_lambda_workers : int
        Parallel lambda trial workers.
    model_config : dict, optional
        Model dimensions override (default: C2VSimCG).
    verbose : bool
        Print progress.
    log_dir : str, optional
        Directory for supervisor logs (default: pest_dir/supervisor/).
    """

    def __init__(self, pest_dir, pst_file, model='claude-sonnet-4-6',
                 max_epochs=5, noptmax_per_epoch=3,
                 n_workers=10, n_lambda_workers=5,
                 model_config=None, verbose=True, log_dir=None):
        self.pest_dir = pest_dir
        self.pst_file = pst_file
        self.model = model
        self.max_epochs = max_epochs
        self.noptmax_per_epoch = noptmax_per_epoch
        self.n_workers = n_workers
        self.n_lambda_workers = n_lambda_workers
        self.verbose = verbose

        self.model_config = model_config or {
            'model_name': 'C2VSimCG',
            'n_gw_nodes': 1393,
            'n_elements': 1392,
            'n_layers': 4,
            'n_stream_nodes': 663,
            'max_iter_store': 50,
            'last_n_timesteps': 12,
        }

        self.log_dir = log_dir or os.path.join(pest_dir, 'supervisor')
        os.makedirs(self.log_dir, exist_ok=True)

        self._client = None
        self._epoch_history = []

    def run(self):
        """Run the supervisor loop.

        Returns
        -------
        SupervisorResult
        """
        t0 = time.perf_counter()
        current_pst = self.pst_file
        epochs = []
        decisions = []

        for epoch in range(self.max_epochs):
            if self.verbose:
                print(f'\n{"="*60}')
                print(f'SUPERVISOR EPOCH {epoch}')
                print(f'{"="*60}')
                print(f'PST: {current_pst}')

            # Run optimizer epoch
            epoch_result = self._run_one_epoch(current_pst, epoch)
            epochs.append(epoch_result)

            if self.verbose:
                pct = 0.0
                if epoch > 0 and epochs[epoch - 1].phi_end > 0:
                    pct = ((epoch_result.phi_end - epochs[epoch - 1].phi_end)
                           / epochs[epoch - 1].phi_end * 100)
                print(f'\nEpoch {epoch}: phi {epoch_result.phi_start:.2e} → '
                      f'{epoch_result.phi_end:.2e} ({pct:+.1f}%), '
                      f'{epoch_result.n_crashed_params} crashed params, '
                      f'{epoch_result.elapsed_seconds/60:.1f} min')

            # Query LLM for decision
            decision = self._query_llm(epoch_result.bundle_json, epochs)
            decisions.append(decision)

            # Log
            self._log_epoch(epoch, epoch_result, decision)

            if self.verbose:
                print(f'\nLLM diagnosis: {decision.diagnosis}')
                print(f'LLM reasoning: {decision.reasoning}')
                if decision.fix_params:
                    print(f'  Fix: {decision.fix_params}')
                if decision.unfix_params:
                    print(f'  Unfix: {decision.unfix_params}')
                if decision.bound_changes:
                    print(f'  Bound changes: {len(decision.bound_changes)}')
                if decision.human_review_flags:
                    print(f'  HUMAN REVIEW: {decision.human_review_flags}')

            # Check stop
            if decision.stop:
                if self.verbose:
                    print(f'\nSupervisor stopping: {decision.message}')
                return SupervisorResult(
                    epochs=epochs, decisions=decisions,
                    final_phi=epoch_result.phi_end,
                    total_elapsed_seconds=time.perf_counter() - t0,
                    stop_reason=decision.message or 'LLM stop signal',
                )

            # Apply decision — write new PST
            if epoch < self.max_epochs - 1:
                new_pst = self._apply_decision(decision, current_pst, epoch)
                if new_pst:
                    current_pst = new_pst

        final_phi = epochs[-1].phi_end if epochs else 0.0
        return SupervisorResult(
            epochs=epochs, decisions=decisions,
            final_phi=final_phi,
            total_elapsed_seconds=time.perf_counter() - t0,
            stop_reason=f'Reached max epochs ({self.max_epochs})',
        )

    def _run_one_epoch(self, pst_file, epoch):
        """Run one optimizer epoch."""
        import sys
        sys.path.insert(0, '/Users/cfbrush/BitTorrent Sync/Programing/repos/pypest/pypest/src')

        from pypest.io.reader import PESTReader
        from pypest.optimization.optimizer import Optimizer
        from pypest.optimization.solver import GLMSolver
        from iwfm.diagnostics.stability_jacobian import StabilityCollector
        from iwfm.diagnostics.assemble_bundle import assemble_bundle
        from iwfm.diagnostics.serialize_bundle import serialize_bundle

        pest = PESTReader().read_file(pst_file)
        noptmax = self.noptmax_per_epoch
        pest.control_data.noptmax = noptmax

        casename = f'c2vsim_epoch_{epoch:03d}'

        collector = StabilityCollector(
            diagnostics_subdir='model/diagnostics',
            convergence_filename='Diagnostics_Convergence.hdf',
            iter_threshold=40,
            diffmax_threshold=0.1,
            verbose=self.verbose,
        )

        n_crashed = [0]
        phi_values = [None, None]  # [start, end]

        def epoch_callback(result):
            it = result.iteration
            phi = result.phi
            if phi_values[0] is None:
                phi_values[0] = phi
            phi_values[1] = phi

            stab = result.stability_jacobian
            if self.verbose:
                tag = 'initial' if it == 0 else f'iter {it}'
                print(f'  [{tag}] phi={phi:.2e}', end='')
                if stab and stab.n_params > 0:
                    print(f' | stability: {stab.n_destabilizing} destab', end='')
                print()

            return None  # no ControlAction from supervisor callback

        t0 = time.perf_counter()
        opt_result = Optimizer(
            pest=pest,
            working_dir=self.pest_dir,
            casename=casename,
            solver=GLMSolver(),
            n_workers=self.n_workers,
            n_lambda_workers=self.n_lambda_workers,
            keep_run_dirs=False,
            cleanup_after_run=True,
            callback=epoch_callback,
            stability_collector=collector,
            verbose_model=False,
        ).run()
        elapsed = time.perf_counter() - t0

        # Count crashed params from optimizer warnings (logged by solver)
        # We detect this from the Jacobian health check

        # Assemble diagnostic bundle
        diag_dir = os.path.join(self.pest_dir, 'Diagnostics')
        try:
            bundle = assemble_bundle(
                diagnostics_dir=diag_dir,
                pest_iteration=epoch,
                pest_res_file=self._find_latest('.res'),
                pest_par_file=self._find_latest('.par'),
                pest_pst_file=pst_file,
                verbose=False,
                **self.model_config,
            )
            bundle_json = serialize_bundle(bundle)
        except Exception as e:
            logger.warning(f'Bundle assembly failed: {e}')
            bundle_json = json.dumps({'error': str(e)})

        # Save bundle
        bundle_path = os.path.join(self.log_dir,
                                    f'bundle_epoch_{epoch:03d}.json')
        with open(bundle_path, 'w') as f:
            f.write(bundle_json)

        return EpochResult(
            epoch=epoch,
            phi_start=phi_values[0] or 0.0,
            phi_end=phi_values[1] or 0.0,
            n_iterations=opt_result.n_iterations if hasattr(opt_result, 'n_iterations') else 0,
            converged=opt_result.converged if hasattr(opt_result, 'converged') else False,
            bundle_json=bundle_json,
            pst_file=pst_file,
            elapsed_seconds=elapsed,
        )

    def _query_llm(self, bundle_json, epoch_history):
        """Send diagnostic bundle to Claude and parse decision.

        Parameters
        ----------
        bundle_json : str
            Serialized diagnostic bundle from this epoch.
        epoch_history : list of EpochResult
            All previous epoch results for context.

        Returns
        -------
        SupervisorDecision
        """
        # Build history summary
        history_lines = []
        for er in epoch_history:
            pct = ''
            if len(epoch_history) > 1:
                prev = epoch_history[epoch_history.index(er) - 1]
                if prev.phi_end > 0 and er is not epoch_history[0]:
                    pct = f' ({(er.phi_end - prev.phi_end) / prev.phi_end * 100:+.1f}%)'
            history_lines.append(
                f'Epoch {er.epoch}: phi {er.phi_start:.2e} → {er.phi_end:.2e}{pct}, '
                f'{er.n_iterations} iters, {er.n_crashed_params} crashes, '
                f'{er.elapsed_seconds/60:.0f} min'
            )

        user_message = f"""\
## Epoch History
{chr(10).join(history_lines)}

## Current Diagnostic Bundle
```json
{bundle_json}
```

Analyze the diagnostic bundle and decide what changes to make for the next \
calibration epoch. Return your decision as a JSON object."""

        try:
            response_text = self._call_api(user_message)
            decision = self._parse_decision(response_text)
        except Exception as e:
            logger.error(f'LLM query failed: {e}')
            decision = SupervisorDecision(
                reasoning=f'LLM query failed: {e}',
                diagnosis='numerical',
                message=f'API error: {e}',
            )

        return decision

    def _call_api(self, user_message):
        """Call the Anthropic API."""
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic()

        response = self._client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': user_message}],
            temperature=0.1,
        )
        return response.content[0].text

    def _parse_decision(self, response_text):
        """Parse LLM response into SupervisorDecision."""
        # Extract JSON from response (may be wrapped in markdown code fence)
        text = response_text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f'Failed to parse LLM JSON: {e}')
            return SupervisorDecision(
                reasoning=f'Parse error: {response_text[:500]}',
                diagnosis='numerical',
                message='Failed to parse LLM response',
            )

        return SupervisorDecision(
            reasoning=data.get('reasoning', ''),
            diagnosis=data.get('diagnosis', ''),
            fix_params=data.get('fix_params', []),
            unfix_params=data.get('unfix_params', []),
            bound_changes=data.get('bound_changes', []),
            perturbation_changes=data.get('perturbation_changes', []),
            initial_lambda=data.get('initial_lambda'),
            numlam=data.get('numlam'),
            noptmax=data.get('noptmax'),
            stop=data.get('stop', False),
            human_review_flags=data.get('human_review_flags', []),
            message=data.get('message', ''),
        )

    def _apply_decision(self, decision, current_pst, epoch):
        """Apply LLM decision to PST, return path to new PST.

        Returns None if no modifications needed.
        """
        from iwfm.diagnostics.write_pest_control import modify_pst

        has_changes = (decision.fix_params or decision.unfix_params
                       or decision.bound_changes
                       or decision.perturbation_changes)
        if not has_changes:
            if self.verbose:
                print('  No PST modifications requested')
            return None

        # Validate param names against PST
        from iwfm.diagnostics.write_pest_control import _parse_pst
        sections = _parse_pst(current_pst)
        valid_names = {p['name'] for p in sections['param_data']}

        fix_valid = [p for p in decision.fix_params if p in valid_names]
        unfix_valid = [p for p in decision.unfix_params if p in valid_names]
        bounds_valid = [b for b in decision.bound_changes
                        if b.get('name') in valid_names]

        invalid = (set(decision.fix_params) - valid_names |
                   set(decision.unfix_params) - valid_names)
        if invalid:
            logger.warning(f'LLM referenced invalid param names: {invalid}')

        modifications = {
            'fix_params': fix_valid,
            'unfix_params': unfix_valid,
            'bound_changes': bounds_valid,
            'perturbation_changes': decision.perturbation_changes,
            'initial_values': {},
        }

        # Read current .par values to carry forward
        par_file = self._find_latest('.par')
        if par_file:
            par_values = self._read_par_file(par_file)
            modifications['initial_values'] = par_values

        new_pst = os.path.join(
            self.pest_dir, f'c2vsim_epoch_{epoch + 1:03d}.pst')
        summary = modify_pst(current_pst, new_pst, modifications,
                             verbose=self.verbose)

        if self.verbose:
            print(f'  New PST: {new_pst}')

        return new_pst

    def _log_epoch(self, epoch, epoch_result, decision):
        """Write epoch log entry."""
        log_entry = {
            'epoch': epoch,
            'timestamp': datetime.now().isoformat(),
            'phi_start': epoch_result.phi_start,
            'phi_end': epoch_result.phi_end,
            'n_iterations': epoch_result.n_iterations,
            'n_crashed_params': epoch_result.n_crashed_params,
            'elapsed_min': epoch_result.elapsed_seconds / 60,
            'diagnosis': decision.diagnosis,
            'reasoning': decision.reasoning,
            'fix_params': decision.fix_params,
            'unfix_params': decision.unfix_params,
            'n_bound_changes': len(decision.bound_changes),
            'stop': decision.stop,
            'human_review_flags': decision.human_review_flags,
        }

        log_path = os.path.join(self.log_dir, 'supervisor_log.jsonl')
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        # Save full decision
        decision_path = os.path.join(
            self.log_dir, f'decision_epoch_{epoch:03d}.json')
        with open(decision_path, 'w') as f:
            json.dump(asdict(decision), f, indent=2)

    def _find_latest(self, extension):
        """Find most recently modified file with extension."""
        candidates = []
        for entry in os.listdir(self.pest_dir):
            if entry.endswith(extension):
                path = os.path.join(self.pest_dir, entry)
                candidates.append((os.path.getmtime(path), path))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1]

    @staticmethod
    def _read_par_file(par_path):
        """Read PEST .par file, return {name: value}."""
        values = {}
        with open(par_path) as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        values[parts[0]] = float(parts[1])
                    except ValueError:
                        continue
        return values
