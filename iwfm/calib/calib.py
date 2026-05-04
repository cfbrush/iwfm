# calib.py
# Typer subapp for `iwfm calib ...` subcommands
# Copyright (C) 2026 University of California
# -----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# -----------------------------------------------------------------------------

"""
Typer subapp for IWFM calibration utilities.

Each command here mirrors a script that already exposes a runnable
``__main__`` block under ``iwfm/calib/`` — both entry points keep working.
The typer wrappers exist to make the unified ``iwfm`` CLI useful and to
keep parameter help text in one place.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="calib",
    help="Model calibration commands (PEST/SMP utilities).",
    no_args_is_help=True,
)


@app.command("divshort")
def divshort(
    budget_file: str = typer.Argument(..., help="IWFM stream budget file (e.g. C2VSimCG_Streams_Budget.bud)."),
    reach_file: str = typer.Argument(..., help="Reach groups file (e.g. stgwgroups.in)."),
    output_file: str = typer.Argument(..., help="Output SMP file. A matching .ins file is written alongside."),
) -> None:
    """Convert IWFM diversion shortages to PEST SMP/INS format."""
    import iwfm
    from iwfm.calib.divshort2obs import divshort2obs

    iwfm.file_test(budget_file)
    iwfm.file_test(reach_file)

    divshort_lines, ins_lines = divshort2obs(budget_file, reach_file)
    outins_file = output_file.replace('.smp', '.ins')

    with open(output_file, 'w') as f:
        for item in divshort_lines:
            f.write(f'{item}\n')
    with open(outins_file, 'w') as f:
        f.write('pif #\n')
        for item in ins_lines:
            f.write(f'{item}\n')

    typer.echo(f'  Read {budget_file} and wrote {output_file} and {outins_file}.')


@app.command("stacdep")
def stacdep(
    budget_file: str = typer.Argument(..., help="IWFM stream budget file."),
    reach_file: str = typer.Argument(..., help="Reach groups file (e.g. stgwgroups.in)."),
    output_file: str = typer.Argument(..., help="Output SMP file. A matching .ins file is written alongside."),
) -> None:
    """Convert IWFM stream-groundwater (depletion) flows to PEST SMP/INS format."""
    import iwfm
    from iwfm.calib.stacdep2obs import stacdep2obs

    iwfm.file_test(budget_file)
    iwfm.file_test(reach_file)

    stacdep_lines, ins_lines = stacdep2obs(budget_file, reach_file)
    outins_file = output_file.replace('.smp', '.ins')

    with open(output_file, 'w') as f:
        for item in stacdep_lines:
            f.write(f'{item}\n')
    with open(outins_file, 'w') as f:
        f.write('pif #\n')
        for item in ins_lines:
            f.write(f'{item}\n')

    typer.echo(f'  Read {budget_file} and wrote {output_file} and {outins_file}.')


@app.command("fac2iwfm")
def fac2iwfm_cmd(
    pp_file: str = typer.Argument(..., help="Pilot-point interpolation factor file."),
    param_file: str = typer.Argument(..., help="Parameter values file."),
    output_file: str = typer.Argument(..., help="Output file name."),
    rlow: float = typer.Argument(..., help="Lower interpolation limit."),
    rhigh: float = typer.Argument(..., help="Upper interpolation limit."),
    empty: float = typer.Argument(..., help="Default value for nodes with no parameter value."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print progress messages."),
) -> None:
    """Convert PEST factor file to IWFM parameter values."""
    from iwfm.calib.fac2iwfm import fac2iwfm
    fac2iwfm(pp_file, param_file, output_file, rlow, rhigh, empty, verbose=verbose)


@app.command("iwfm2obs")
def iwfm2obs_cmd(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print progress messages."),
) -> None:
    """Convert IWFM hydrograph output to PEST observation files.

    iwfm2obs prompts interactively for paths (it has no positional args
    in its current form). This command just hands off to that function.
    """
    from iwfm.calib.iwfm2obs import iwfm2obs
    iwfm2obs(verbose=verbose)


# -- additional wrappers ----------------------------------------------------

@app.command("calib-stats")
def calib_stats_cmd(
    pest_smp_file: str = typer.Argument(..., help="PEST SMP file with observed values."),
    gwhyd_info_file: str = typer.Argument(..., help="IWFM Groundwater.dat file."),
    gwhyd_file: str = typer.Argument(..., help="Simulated hydrographs file."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Compute calibration statistics (RMSE/bias) per observation well."""
    from iwfm.calib.calib_stats import calib_stats
    calib_stats(pest_smp_file, gwhyd_info_file, gwhyd_file, verbose=verbose)


@app.command("ltbud")
def ltbud_cmd(
    budget_file: str = typer.Argument(..., help="Input IWFM budget file."),
    output_file: str = typer.Argument(..., help="Output (log-transformed) budget file."),
    zero_offset: float = typer.Option(2.0, "--zero-offset", help="Offset added before log to avoid log(0)."),
    neg_val: float = typer.Option(1.0e-7, "--neg-val", help="Replacement for negative values pre-log."),
) -> None:
    """Log-transform an IWFM budget file."""
    from iwfm.calib.ltbud import ltbud
    ltbud(budget_file, output_file, zero_offset=zero_offset, neg_val=neg_val)


@app.command("ltsmp")
def ltsmp_cmd(
    input_file: str = typer.Argument(..., help="Input SMP file."),
    output_file: str = typer.Argument(..., help="Output (log-transformed) SMP file."),
    zero_offset: float = typer.Option(36.0, "--zero-offset", help="Offset added before log to avoid log(0)."),
    neg_val: float = typer.Option(0.001, "--neg-val", help="Replacement for negative values pre-log."),
) -> None:
    """Log-transform an SMP file."""
    from iwfm.calib.ltsmp import ltsmp
    ltsmp(input_file, output_file, zero_offset=zero_offset, neg_val=neg_val)


@app.command("pest-res-stats")
def pest_res_stats_cmd(
    pest_res_file: str = typer.Argument(..., help="PEST residuals file."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Summarize PEST residuals (writes a *_stats.out file)."""
    from iwfm.calib.pest_res_stats import pest_res_stats
    pest_res_stats(pest_res_file, verbose=verbose)


@app.command("ppk2fac-trans")
def ppk2fac_trans_cmd(
    factors_file: str = typer.Argument(..., help="Input pilot-point factors file."),
    trans_file: str = typer.Argument(..., help="Translation file (node remapping)."),
    out_file: str = typer.Argument(..., help="Output factors file."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Translate a pilot-point factors file via a node-remap file."""
    from iwfm.calib.ppk2fac_trans import ppk2fac_trans
    ppk2fac_trans(factors_file, trans_file, out_file, verbose=verbose)


@app.command("real2iwfm")
def real2iwfm_cmd(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Apply a PEST realization back to an IWFM overwrite template.

    real2iwfm prompts interactively for paths (no positional args in its
    current form).
    """
    from iwfm.calib.real2iwfm import real2iwfm
    real2iwfm(verbose=verbose)


@app.command("res-stats")
def res_stats_cmd(
    pest_smp_file: str = typer.Argument(..., help="PEST SMP file with observed values."),
    gwhyd_info_file: str = typer.Argument(..., help="IWFM Groundwater.dat file."),
    gwhyd_file: str = typer.Argument(..., help="Simulated hydrographs file."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Compute residual statistics for a SMP/sim pair."""
    from iwfm.calib.res_stats import res_stats
    res_stats(pest_smp_file, gwhyd_info_file, gwhyd_file, verbose=verbose)


@app.command("simout2gw")
def simout2gw_cmd(
    simout_file: str = typer.Argument(..., help="IWFM SimulationMessages.out file."),
    gw_in_file: str = typer.Argument(..., help="Existing groundwater.dat template."),
    output_file: str = typer.Argument(..., help="New groundwater.dat with parameters injected."),
) -> None:
    """Inject parameters from SimulationMessages.out into a Groundwater.dat template."""
    from iwfm.calib.simout2gw import simout2gw
    simout2gw(simout_file, gw_in_file, output_file)


@app.command("smp-avg")
def smp_avg_cmd(
    smp_file: str = typer.Argument(..., help="Input SMP file."),
    output_file: str = typer.Argument(..., help="Output file (one averaged value per line)."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Average values per series in an SMP file."""
    from iwfm.calib.smp_avg import smp_avg
    averages = smp_avg(smp_file, verbose=verbose)
    with open(output_file, 'w') as f:
        for item in averages:
            f.write(f'{item}\n')
    typer.echo(f'  Wrote {len(averages):,} values to {output_file}')


@app.command("smp-format")
def smp_format_cmd(
    smp_file: str = typer.Argument(..., help="Input SMP file."),
    output_file: str = typer.Argument(..., help="Output (reformatted) SMP file."),
    nwidth: int = typer.Option(20, "--nwidth", help="Width of the name column."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Reformat an SMP file (e.g., normalize name-column width)."""
    from iwfm.calib.smp_format import smp_format
    smp_out = smp_format(smp_file, nwidth=nwidth, verbose=verbose)
    with open(output_file, 'w') as f:
        for item in smp_out:
            f.write(f'{item}\n')
    typer.echo(f'  Wrote {len(smp_out):,} values to {output_file}')


@app.command("well-pairs-to-obs")
def well_pairs_2_obs_list_cmd(
    well_pair_file: str = typer.Argument(..., help="File listing pairs of wells."),
    obs_file: str = typer.Argument(..., help="Observations file (SMP format)."),
    days: int = typer.Option(15, "--days", help="Pairing window in days."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Pair observations from related wells within a date window."""
    from iwfm.calib.well_pairs_2_obs_list import well_pairs_2_obs_list
    well_pairs_2_obs_list(well_pair_file, obs_file, days=days, verbose=verbose)
