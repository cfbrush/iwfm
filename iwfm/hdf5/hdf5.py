# hdf5.py
# Typer subapp for `iwfm hdf5 ...` subcommands
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
Typer subapp for IWFM HDF5 budget conversion commands.

The wrapped functions (``hdf2bud_gw``, ``hdf2bud_stream``, ``hdf2xlsx_gw``,
``hdf2xlsx_stream``) all share the same conversion-factor signature, so the
typer commands expose the same Options for unit overrides.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="hdf5",
    help="HDF5 budget conversion utilities (HDF5 → text/Excel).",
    no_args_is_help=True,
)


_LEN_FACT_DEFAULT = 1.0
_AREA_FACT_DEFAULT = 0.000022957  # sq ft → acres (1/43560)
_VOL_FACT_DEFAULT = 0.000022957   # cu ft → acre-ft (1/43560)


# Each command duplicates the same conversion-factor Options because typer
# resolves option help/types from each command's signature individually.
# When editing the option help text, update every command (or grep for the
# string) to keep the docs consistent.


@app.command("bud-gw")
def bud_gw(
    hdf_file: str = typer.Argument(..., help="Input groundwater budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact", help="Length conversion factor (multiplier)."),
    len_units: str = typer.Option("FEET", "--len-units", help="Length units for output (e.g. FEET, METERS)."),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact", help="Area conversion factor (default: sq ft → acres)."),
    area_units: str = typer.Option("AC", "--area-units", help="Area units for output (e.g. AC, HA)."),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact", help="Volume conversion factor (default: cu ft → acre-ft)."),
    vol_units: str = typer.Option("ACFT", "--vol-units", help="Volume units for output (e.g. ACFT, M3)."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM groundwater budget HDF5 to text format."""
    from iwfm.hdf5.hdf2bud_gw import hdf2bud_gw
    hdf2bud_gw(hdf_file, output_file,
               len_fact=len_fact, len_units=len_units,
               area_fact=area_fact, area_units=area_units,
               vol_fact=vol_fact, vol_units=vol_units,
               verbose=verbose, debug=debug)


@app.command("bud-stream")
def bud_stream(
    hdf_file: str = typer.Argument(..., help="Input stream budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM stream budget HDF5 to text format."""
    from iwfm.hdf5.hdf2bud_stream import hdf2bud_stream
    hdf2bud_stream(hdf_file, output_file,
                   len_fact=len_fact, len_units=len_units,
                   area_fact=area_fact, area_units=area_units,
                   vol_fact=vol_fact, vol_units=vol_units,
                   verbose=verbose, debug=debug)


@app.command("xlsx-gw")
def xlsx_gw(
    hdf_file: str = typer.Argument(..., help="Input groundwater budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM groundwater budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_gw import hdf2xlsx_gw
    hdf2xlsx_gw(hdf_file, output_file,
                len_fact=len_fact, len_units=len_units,
                area_fact=area_fact, area_units=area_units,
                vol_fact=vol_fact, vol_units=vol_units,
                verbose=verbose, debug=debug)


@app.command("xlsx-stream")
def xlsx_stream(
    hdf_file: str = typer.Argument(..., help="Input stream budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM stream budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_stream import hdf2xlsx_stream
    hdf2xlsx_stream(hdf_file, output_file,
                    len_fact=len_fact, len_units=len_units,
                    area_fact=area_fact, area_units=area_units,
                    vol_fact=vol_fact, vol_units=vol_units,
                    verbose=verbose, debug=debug)


# -- additional bud-* commands (lw, rz, unsat, swat, diversions, snodes) ----

@app.command("bud-lw")
def bud_lw(
    hdf_file: str = typer.Argument(..., help="Input land/water-use budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM land/water-use budget HDF5 to text format."""
    from iwfm.hdf5.hdf2bud_lw import hdf2bud_lw
    hdf2bud_lw(hdf_file, output_file,
               len_fact=len_fact, len_units=len_units,
               area_fact=area_fact, area_units=area_units,
               vol_fact=vol_fact, vol_units=vol_units,
               verbose=verbose, debug=debug)


@app.command("bud-rz")
def bud_rz(
    hdf_file: str = typer.Argument(..., help="Input root-zone budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM root-zone budget HDF5 to text format."""
    from iwfm.hdf5.hdf2bud_rz import hdf2bud_rz
    hdf2bud_rz(hdf_file, output_file,
               len_fact=len_fact, len_units=len_units,
               area_fact=area_fact, area_units=area_units,
               vol_fact=vol_fact, vol_units=vol_units,
               verbose=verbose, debug=debug)


@app.command("bud-unsat")
def bud_unsat(
    hdf_file: str = typer.Argument(..., help="Input unsaturated-zone budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM unsaturated-zone budget HDF5 to text format."""
    from iwfm.hdf5.hdf2bud_unsat import hdf2bud_unsat
    hdf2bud_unsat(hdf_file, output_file,
                  len_fact=len_fact, len_units=len_units,
                  area_fact=area_fact, area_units=area_units,
                  vol_fact=vol_fact, vol_units=vol_units,
                  verbose=verbose, debug=debug)


@app.command("bud-swat")
def bud_swat(
    hdf_file: str = typer.Argument(..., help="Input small-watersheds budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM small-watersheds budget HDF5 to text format."""
    from iwfm.hdf5.hdf2bud_swat import hdf2bud_swat
    hdf2bud_swat(hdf_file, output_file,
                 len_fact=len_fact, len_units=len_units,
                 area_fact=area_fact, area_units=area_units,
                 vol_fact=vol_fact, vol_units=vol_units,
                 verbose=verbose, debug=debug)


@app.command("bud-diversions")
def bud_diversions(
    hdf_file: str = typer.Argument(..., help="Input stream-diversions budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM stream-diversions budget HDF5 to text format."""
    # Note: the underlying function name is `hdf2bud_diverions` (typo in source);
    # CLI command spelling is correct.
    from iwfm.hdf5.hdf2bud_diversions import hdf2bud_diverions
    hdf2bud_diverions(hdf_file, output_file,
                      len_fact=len_fact, len_units=len_units,
                      area_fact=area_fact, area_units=area_units,
                      vol_fact=vol_fact, vol_units=vol_units,
                      verbose=verbose, debug=debug)


@app.command("bud-snodes")
def bud_snodes(
    hdf_file: str = typer.Argument(..., help="Input stream-nodes budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM stream-nodes budget HDF5 to text format."""
    from iwfm.hdf5.hdf2bud_snodes import hdf2bud_snodes
    hdf2bud_snodes(hdf_file, output_file,
                   len_fact=len_fact, len_units=len_units,
                   area_fact=area_fact, area_units=area_units,
                   vol_fact=vol_fact, vol_units=vol_units,
                   verbose=verbose, debug=debug)


# -- additional xlsx-* commands (lw, rz, unsat, swat, diversions, snodes) ---

@app.command("xlsx-lw")
def xlsx_lw(
    hdf_file: str = typer.Argument(..., help="Input land/water-use budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM land/water-use budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_lw import hdf2xlsx_lw
    hdf2xlsx_lw(hdf_file, output_file,
                len_fact=len_fact, len_units=len_units,
                area_fact=area_fact, area_units=area_units,
                vol_fact=vol_fact, vol_units=vol_units,
                verbose=verbose, debug=debug)


@app.command("xlsx-rz")
def xlsx_rz(
    hdf_file: str = typer.Argument(..., help="Input root-zone budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM root-zone budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_rz import hdf2xlsx_rz
    hdf2xlsx_rz(hdf_file, output_file,
                len_fact=len_fact, len_units=len_units,
                area_fact=area_fact, area_units=area_units,
                vol_fact=vol_fact, vol_units=vol_units,
                verbose=verbose, debug=debug)


@app.command("xlsx-unsat")
def xlsx_unsat(
    hdf_file: str = typer.Argument(..., help="Input unsaturated-zone budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM unsaturated-zone budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_unsat import hdf2xlsx_unsat
    hdf2xlsx_unsat(hdf_file, output_file,
                   len_fact=len_fact, len_units=len_units,
                   area_fact=area_fact, area_units=area_units,
                   vol_fact=vol_fact, vol_units=vol_units,
                   verbose=verbose, debug=debug)


@app.command("xlsx-swat")
def xlsx_swat(
    hdf_file: str = typer.Argument(..., help="Input small-watersheds budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM small-watersheds budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_swat import hdf2xlsx_swat
    hdf2xlsx_swat(hdf_file, output_file,
                  len_fact=len_fact, len_units=len_units,
                  area_fact=area_fact, area_units=area_units,
                  vol_fact=vol_fact, vol_units=vol_units,
                  verbose=verbose, debug=debug)


@app.command("xlsx-diversions")
def xlsx_diversions(
    hdf_file: str = typer.Argument(..., help="Input stream-diversions budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM stream-diversions budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_diversions import hdf2xlsx_diversions
    hdf2xlsx_diversions(hdf_file, output_file,
                        len_fact=len_fact, len_units=len_units,
                        area_fact=area_fact, area_units=area_units,
                        vol_fact=vol_fact, vol_units=vol_units,
                        verbose=verbose, debug=debug)


@app.command("xlsx-snodes")
def xlsx_snodes(
    hdf_file: str = typer.Argument(..., help="Input stream-nodes budget HDF5 file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM stream-nodes budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2xlsx_snodes import hdf2xlsx_snodes
    hdf2xlsx_snodes(hdf_file, output_file,
                    len_fact=len_fact, len_units=len_units,
                    area_fact=area_fact, area_units=area_units,
                    vol_fact=vol_fact, vol_units=vol_units,
                    verbose=verbose, debug=debug)


# -- zonal budget commands (require a zone definition file) ----------------

@app.command("zbud-gw")
def zbud_gw(
    hdf_file: str = typer.Argument(..., help="Input zone-budget HDF5 file."),
    zone_file: str = typer.Argument(..., help="Zone definition file."),
    output_file: str = typer.Argument(..., help="Output text file."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM groundwater zone-budget HDF5 to text format."""
    from iwfm.hdf5.hdf2zbud_gw import hdf2zbud_gw
    hdf2zbud_gw(hdf_file, zone_file, output_file,
                len_fact=len_fact, len_units=len_units,
                area_fact=area_fact, area_units=area_units,
                vol_fact=vol_fact, vol_units=vol_units,
                verbose=verbose, debug=debug)


@app.command("zxlsx-gw")
def zxlsx_gw(
    hdf_file: str = typer.Argument(..., help="Input zone-budget HDF5 file."),
    zone_file: str = typer.Argument(..., help="Zone definition file."),
    output_file: str = typer.Argument(..., help="Output Excel file (.xlsx)."),
    len_fact: float = typer.Option(_LEN_FACT_DEFAULT, "--len-fact"),
    len_units: str = typer.Option("FEET", "--len-units"),
    area_fact: float = typer.Option(_AREA_FACT_DEFAULT, "--area-fact"),
    area_units: str = typer.Option("AC", "--area-units"),
    vol_fact: float = typer.Option(_VOL_FACT_DEFAULT, "--vol-fact"),
    vol_units: str = typer.Option("ACFT", "--vol-units"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Convert IWFM groundwater zone-budget HDF5 to Excel workbook."""
    from iwfm.hdf5.hdf2zxlsx_gw import hdf2zxlsx_gw
    hdf2zxlsx_gw(hdf_file, zone_file, output_file,
                 len_fact=len_fact, len_units=len_units,
                 area_fact=area_fact, area_units=area_units,
                 vol_fact=vol_fact, vol_units=vol_units,
                 verbose=verbose, debug=debug)
