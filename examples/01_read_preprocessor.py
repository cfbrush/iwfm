#!/usr/bin/env python
# 01_read_preprocessor.py
# Read an IWFM Preprocessor file and print summary
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
01_read_preprocessor.py — Read an IWFM Preprocessor file and print summary.

Usage:
    python 01_read_preprocessor.py <preprocessor.in>

Expects a real IWFM preprocessor input file. The file lists paths to the
node, element, stratigraphy, and stream files; this script opens it and
reports how many of each.
"""
from __future__ import annotations

import sys
from pathlib import Path

import iwfm


def main(pre_file: str) -> None:
    iwfm.file_test(pre_file)

    pre_files, have_lake = iwfm.iwfm_read_preproc(pre_file)
    pre_dir = Path(pre_file).parent

    nodes_path = pre_files.node_file
    elem_path = pre_files.elem_file
    strat_path = pre_files.strat_file

    node_coords, node_list, _factor = iwfm.iwfm_read_nodes(nodes_path)
    elem_ids, elem_nodes, elem_sub = iwfm.iwfm_read_elements(elem_path)
    strat, nlayers = iwfm.iwfm_read_strat(strat_path, node_coords)

    print(f"preprocessor : {pre_file}")
    print(f"  nodes      : {len(node_list):,}")
    print(f"  elements   : {len(elem_ids):,}")
    print(f"  layers     : {nlayers}")
    print(f"  has lake   : {have_lake}")
    print(f"  files dir  : {pre_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
