#!/usr/bin/env python
# 02_hyd_diff.py
# Compute the difference between two hydrograph files
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
02_hyd_diff.py — Compute the difference between two hydrograph files.

Usage:
    python 02_hyd_diff.py <scenario.out> <base.out> <diff.out>

Writes a third hydrograph file containing scenario - base for each well
and timestep. Equivalent to `iwfm.hyd_diff(...)`. The CLI form via
the unified `iwfm` console_script is not yet wired (no calib subcommand
for hyd_diff at time of writing).
"""
from __future__ import annotations

import sys

import iwfm


def main(scenario: str, base: str, diff: str) -> None:
    iwfm.file_test(scenario)
    iwfm.file_test(base)
    iwfm.hyd_diff(scenario, base, diff)
    print(f"wrote {diff}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
