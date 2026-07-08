# test_sub_gw_bc_node_file.py
# Unit tests for sub_gw_bc_node_file in the iwfm package
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

import os
import tempfile

import pytest

from iwfm.sub.gw_bc_node_file import sub_gw_bc_node_file


def _run(content, nodes):
    with tempfile.TemporaryDirectory() as d:
        old = os.path.join(d, 'old_bc.dat')
        new = os.path.join(d, 'new_bc.dat')
        with open(old, 'w') as f:
            f.write(content)
        n = sub_gw_bc_node_file(old, new, nodes)
        return n, open(new).read()


def test_specified_head_style_one_factor():
    """One factor line between count and BC table."""
    content = (
        "C specified head BC file\n"
        "     3                        / NHB\n"
        "     1.0                      / FACTHB\n"
        "C   IB   IL   ITSCOL\n"
        "\t10\t1\t1\n"
        "\t11\t1\t2\n"
        "\t20\t2\t3\n"
    )
    n, out = _run(content, nodes=[10, 11])

    assert n == 2
    assert '2' in out.splitlines()[1]          # count updated
    assert 'NHB' in out                        # description preserved
    assert '\t20\t2\t3' not in out            # node 20 removed
    assert '\t10\t1\t1' in out


def test_general_head_style_three_factors():
    """Multiple factor lines are skipped before the BC table."""
    content = (
        "C general head BC file\n"
        "     2                        / NGB\n"
        "     1.0                      / FACTH\n"
        "     1.0                      / FACTC\n"
        "     1MON                     / TUNITC\n"
        "C   IB   IL   H   C   ITSCOL\n"
        "\t10\t1\t100.0\t5.0\t1\n"
        "\t99\t1\t90.0\t4.0\t2\n"
    )
    n, out = _run(content, nodes=[10])

    assert n == 1
    assert 'NGB' in out
    assert '\t99\t' not in out


def test_all_removed():
    content = (
        "     1                        / NQB\n"
        "     1.0                      / FACT\n"
        "\t50\t1\t1\n"
    )
    n, out = _run(content, nodes=[1, 2])

    assert n == 0
    assert '\t50\t' not in out
