#!/usr/bin/env python
# 05_hdf_to_csv.py
# Convert an IWFM groundwater budget HDF5 file to text
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
05_hdf_to_csv.py — IWFM groundwater budget HDF5 → text format.

Usage:
    python 05_hdf_to_csv.py <input.hdf> <output.txt>

Same as `iwfm hdf5 bud-gw <input.hdf> <output.txt>` from the unified CLI,
just shown as a Python call. Default conversion factors:
    area : sq ft → acres
    vol  : cu ft → acre-ft

Override with the keyword args of `hdf2bud_gw` or by using flags on the
CLI form.
"""
from __future__ import annotations

import sys

from iwfm.hdf5.hdf2bud_gw import hdf2bud_gw


def main(hdf_file: str, output_file: str) -> None:
    hdf2bud_gw(
        hdf_file,
        output_file,
        len_fact=1.0, len_units='FEET',
        area_fact=0.000022957, area_units='AC',
        vol_fact=0.000022957, vol_units='ACFT',
        verbose=True,
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
