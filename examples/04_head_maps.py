#!/usr/bin/env python
# 04_head_maps.py
# Map simulated heads over the model domain at one timestep
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
04_head_maps.py — Map simulated heads over the model domain at one timestep.

Usage:
    python 04_head_maps.py <headall.out> <preprocessor.in> <boundary.csv> \\
                           <date MM/DD/YYYY> <output_basename>

For each model layer, writes three TIFF images:
    <basename>_Layer_<n>_nodes.tiff      point/scatter map
    <basename>_Layer_<n>_contour.tiff    contour lines
    <basename>_Layer_<n>_contourf.tiff   filled contour

Inputs:
    headall.out        IWFM groundwater head output (all nodes, all layers,
                       all timesteps).
    preprocessor.in    IWFM preprocessor main file (used to locate node
                       and stratigraphy files).
    boundary.csv       2-column CSV: ordered list of boundary node IDs.
    date               One of the timestep dates printed in headall.out
                       (must match exactly, including format).

Demonstrates `iwfm.headall2map` — a one-call wrapper that handles
preproc parsing, head extraction, and matplotlib rendering. For more
control over the styling, call `iwfm.plot.map_to_nodes` /
`map_to_nodes_contour` directly.
"""
from __future__ import annotations

import sys

import iwfm


def main(heads_file: str,
         pre_file: str,
         bnds_file: str,
         out_date: str,
         basename: str) -> None:
    iwfm.file_test(heads_file)
    iwfm.file_test(pre_file)
    iwfm.file_test(bnds_file)

    iwfm.headall2map(
        heads_file, pre_file, bnds_file,
        out_date=out_date,
        basename=basename,
        label='Head',
        units='ft',
        verbose=True,
    )

    print(f"wrote head maps with basename {basename!r}")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
