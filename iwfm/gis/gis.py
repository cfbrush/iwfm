# gis.py
# Typer subapp for `iwfm gis ...` subcommands
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
Typer subapp for IWFM GIS utilities.

The map_param2shp_rz_* commands wrap the existing 3-argument scripts
(rootzone main file + elements shapefile + output shapefile) and run the
same `iwfm.iwfm_read_rz_*` preprocessing that their __main__ blocks do.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="gis",
    help="GIS-related utilities (parameter mapping, shapefile reprojection).",
    no_args_is_help=True,
)


# Parameter type lists must match the lists in each script's __main__ block.
_NPC_PARAM_TYPES = ["cn", "et", "wsp", "ip", "ms", "ts", "rf", "ru", "ic"]
_PC_PARAM_TYPES = ["cn", "et", "wsp", "ip", "pd", "ad", "rf", "ru", "ic"]
_URBAN_PARAM_TYPES = [
    "perv", "cnurb", "icpopul", "icwtruse", "fracdm",
    "iceturb", "icrtfurb", "icrufurb", "icurbspec", "ic",
]


@app.command("map-param2shp-npc")
def map_param2shp_npc(
    rz_file: str = typer.Argument(..., help="IWFM root zone main file."),
    elem_shp: str = typer.Argument(..., help="IWFM elements shapefile."),
    out_shp: str = typer.Argument(..., help="Output shapefile name."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Map non-ponded crop parameters onto an elements shapefile."""
    import iwfm
    from iwfm.gis.map_param2shp_rz_npc import map_param2shp_rz_npc

    iwfm.file_test(rz_file)
    iwfm.file_test(elem_shp)

    crops, param_vals, _files = iwfm.iwfm_read_rz_npc(rz_file)
    map_param2shp_rz_npc(_NPC_PARAM_TYPES, param_vals, crops, elem_shp,
                         out_shp_name=out_shp, verbose=verbose)


@app.command("map-param2shp-pc")
def map_param2shp_pc(
    rz_file: str = typer.Argument(..., help="IWFM root zone main file."),
    elem_shp: str = typer.Argument(..., help="IWFM elements shapefile."),
    out_shp: str = typer.Argument(..., help="Output shapefile name."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Map ponded crop parameters onto an elements shapefile."""
    import iwfm
    from iwfm.gis.map_param2shp_rz_pc import map_param2shp_rz_pc

    iwfm.file_test(rz_file)
    iwfm.file_test(elem_shp)

    crops, param_vals, _files = iwfm.iwfm_read_rz_pc(rz_file)
    map_param2shp_rz_pc(_PC_PARAM_TYPES, param_vals, crops, elem_shp,
                       out_shp_name=out_shp, verbose=verbose)


@app.command("map-param2shp-urban")
def map_param2shp_urban(
    rz_file: str = typer.Argument(..., help="IWFM root zone main file."),
    elem_shp: str = typer.Argument(..., help="IWFM elements shapefile."),
    out_shp: str = typer.Argument(..., help="Output shapefile name."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Map urban-area parameters onto an elements shapefile."""
    import iwfm
    from iwfm.gis.map_param2shp_rz_urban import map_param2shp_rz_urban

    iwfm.file_test(rz_file)
    iwfm.file_test(elem_shp)

    _crops, param_vals, _files = iwfm.iwfm_read_rz_urban(rz_file)
    map_param2shp_rz_urban(_URBAN_PARAM_TYPES, param_vals, elem_shp,
                          out_shp_name=out_shp, verbose=verbose)


@app.command("shp-reproject")
def shp_reproject_cmd(
    src: str = typer.Argument(..., help="Source shapefile."),
    tgt: str = typer.Argument(..., help="Target shapefile path (will be created/overwritten)."),
    epsg: int = typer.Option(26910, "--epsg", help="Target EPSG code (default 26910 = NAD83 / UTM zone 10N)."),
) -> None:
    """Reproject a shapefile to the given EPSG code."""
    import iwfm
    from iwfm.gis.shp_reproject import shp_reproject

    iwfm.file_test(src)
    shp_reproject(src, tgt, epsg=epsg)
