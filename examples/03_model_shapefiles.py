#!/usr/bin/env python
# 03_model_shapefiles.py
# Generate node + element shapefiles from a preproc file
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
03_model_shapefiles.py — Generate node + element shapefiles from a preproc file.

Usage:
    python 03_model_shapefiles.py <preprocessor.in> <output_dir> [--epsg 26910]

Reads the IWFM Preprocessor main file, follows its references to node /
element / (optional) lake files, and writes two shapefiles into
<output_dir>:

    nodes.shp     point shapefile of every model node (with node id field)
    elements.shp  polygon shapefile of every element (with element id and
                  subregion fields, plus a lake_no field if any element
                  belongs to a lake)

EPSG defaults to 26910 (NAD 83 / UTM zone 10N — California). Override
with the optional `--epsg <code>` flag.

Demonstrates: `iwfm.iwfm_read_preproc`, `iwfm.iwfm_read_nodes`,
`iwfm.iwfm_read_elements`, `iwfm.iwfm_read_lake`, plus the GIS writers
`iwfm.gis.nodes2shp_csv` and `iwfm.gis.elem2shp`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import iwfm
from iwfm.gis.nodes2shp_csv import nodes2shp_csv
from iwfm.gis.elem2shp import elem2shp


def _parse_epsg(argv: list[str]) -> tuple[list[str], int]:
    """Strip optional `--epsg N` from argv. Default 26910."""
    epsg = 26910
    rest = []
    i = 0
    while i < len(argv):
        if argv[i] == '--epsg' and i + 1 < len(argv):
            epsg = int(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    return rest, epsg


def main(pre_file: str, out_dir: str, epsg: int) -> None:
    iwfm.file_test(pre_file)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    pre_files, have_lake = iwfm.iwfm_read_preproc(pre_file)

    # Read nodes; build {id: (x, y)} dict that the GIS writers expect.
    node_coord, node_list, _factor = iwfm.iwfm_read_nodes(pre_files.node_file)
    node_coord_dict = {row[0]: (row[1], row[2]) for row in node_coord}
    print(f"  {len(node_coord_dict):,} nodes")

    # Read elements (returns ids, per-element node lists, per-element subregion).
    elem_ids, elem_nodes, elem_sub = iwfm.iwfm_read_elements(pre_files.elem_file)
    print(f"  {len(elem_ids):,} elements")

    # Read lakes if the preprocessor declares a lake file. elem2shp accepts
    # an empty list when there are none.
    lakes: list = []
    if have_lake and pre_files.lake_file:
        try:
            _lake_elems, lakes = iwfm.iwfm_read_lake(pre_files.lake_file)
            print(f"  {len(lakes):,} lake(s)")
        except Exception as e:
            print(f"  warning: failed to read lake file ({e}); skipping")

    nodes_shp = str(out / 'nodes.shp')
    elements_shp = str(out / 'elements')  # elem2shp appends .shp internally

    nodes2shp_csv(node_coord_dict, shapename=nodes_shp, epsg=epsg, verbose=True)
    elem2shp(elem_ids, elem_nodes, node_coord_dict, elem_sub, lakes,
             shape_name=elements_shp, epsg=epsg, verbose=True)

    print(f"wrote {nodes_shp} and {elements_shp}.shp")


if __name__ == "__main__":
    rest, epsg = _parse_epsg(sys.argv[1:])
    if len(rest) != 2:
        print(__doc__)
        sys.exit(2)
    main(rest[0], rest[1], epsg)
