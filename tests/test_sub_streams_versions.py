#!/usr/bin/env python
# test_sub_streams_versions.py
# Version-support tests (4.0/4.1/4.2/5.0) for sub/streams_file.py
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

import pytest

import iwfm
from iwfm.iwfm_dataclasses import SimulationFiles


# Simulation stream main file, formats from the IWFM-2015.1.1443 templates.
# Version differences exercised here:
# - v5.0 adds a FNSTRMFL line after DIVDTLBUDFL
# - stream bed factor lines: 3 for v4.x, 4 for v5.0 (INTRCTYPE moves up)
# - bed rows: `IR CSTRM DSTRM WETPR` (4.0), `IR CSTRM DSTRM` (4.1, 5.0),
#   `IR WETPR IRGW CSTRM DSTRM` + 4-value continuation rows (4.2)
# - v4.x has a separate INTRCTYPE section after the bed rows
# - v5.0 has cross-section and initial-condition rows (one per stream node)
# - all versions end with STARFL + optional `IR ICETST ICARST` evaporation rows

BLANK_FILES = """                                                / INFLOWFL
                                                / DIVSPECFL
                                                / BYPSPECFL
                                                / DIVFL
    Results\\Streams_Budget.hdf                 / STRMRCHBUDFL
    Results\\Diversions.hdf                     / DIVDTLBUDFL"""

HYD_BUD = """C*******************************************************************************
       3                                        / NOUTR
       0                                        / IHSQR
       1.0                                      / FACTVROU
       AC-FT/MON                                / UNITVROU
       1                                        / FACTLTOU
       FEET                                     / UNITLTOU
    Results\\Stream_Hydrographs.out             / STHYDOUTFL
C-------------------------------------------------------------------------------
\t101\t\tNode101
\t102\t\tNode102
\t103\t\tNode103
C*******************************************************************************
        3                                       / NBUDR
    Results\\StreamNode_Budget.hdf              / STNDBUDFL
C-------------------------------------------------------------------------------
\t101
\t102
\t103"""

EVAP = """C*******************************************************************************
                                                / STARFL
C-------------------------------------------------------------------------------
\t101\t5\t1
\t102\t6\t2
\t103\t7\t3
"""


def make_v4(version, bed_rows):
    return (f"""#{version}
C Stream parameters data file
C
{BLANK_FILES}
{HYD_BUD}
C*******************************************************************************
    1.0                                         / FACTK
    1MON                                        / TUNITSK
    1.0                                         / FACTL
C-------------------------------------------------------------------------------
{bed_rows}
C*******************************************************************************
    1                                           / INTRCTYPE
{EVAP}""")


V40 = make_v4('4.0', '\t101\t2.0\t1.0\t300\n\t102\t2.1\t1.1\t310\n\t103\t2.2\t1.2\t320')

V41 = make_v4('4.1', '\t101\t2.0\t1.0\n\t102\t2.1\t1.1\n\t103\t2.2\t1.2')

# v4.2: node 101 spans two groundwater nodes (one 5-value row + one 4-value
# continuation row); nodes 102 and 103 have one row each; 103 also has a
# continuation row that must be removed with it
V42 = make_v4('4.2', '\t101\t300\t1001\t2.0\t1.0\n'
                     '\t150\t1002\t2.5\t1.5\n'
                     '\t102\t310\t1003\t2.1\t1.1\n'
                     '\t103\t320\t1004\t2.2\t1.2\n'
                     '\t160\t1005\t2.6\t1.6')

V50 = f"""#5.0
C Stream parameters data file
C
{BLANK_FILES}
                                                / FNSTRMFL
{HYD_BUD}
C*******************************************************************************
    1.0                                         / FACTK
    1MON                                        / TUNITSK
    1.0                                         / FACTL
    1                                           / INTRCTYPE
C-------------------------------------------------------------------------------
\t101\t2.0\t1.0
\t102\t2.1\t1.1
\t103\t2.2\t1.2
C*******************************************************************************
    1.0                                         / FACTN
    1.0                                         / FACTLT
C-------------------------------------------------------------------------------
\t101\t10.0\t50.0\t0.5\t0.04\t20.0
\t102\t11.0\t51.0\t0.5\t0.04\t21.0
\t103\t12.0\t52.0\t0.5\t0.04\t22.0
C*******************************************************************************
    0                                           / ICTYPE
    1MON                                        / TUNITQ
    1.0                                         / FACTHQ
C-------------------------------------------------------------------------------
\t101\t5.0
\t102\t5.1
\t103\t5.2
{EVAP}"""

SUB_SNODES = [101, 102]


def run(tmp_path, content):
    old = tmp_path / 'Streams.dat'
    old.write_text(content)
    sim_files = SimulationFiles(stream_file=str(old))
    sim_files_new = SimulationFiles(
        stream_file=str(tmp_path / 'Sub_Streams.dat'),
        stin_file=str(tmp_path / 'Sub_StreamInflow.dat'),
        divspec_file=str(tmp_path / 'Sub_DivSpec.dat'),
        bp_file=str(tmp_path / 'Sub_BypassSpec.dat'),
        div_file=str(tmp_path / 'Sub_Diversions.dat'),
    )
    iwfm.sub_streams_file(sim_files, sim_files_new, [], SUB_SNODES)
    with open(sim_files_new.stream_file, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


def assert_common_filtering(lines):
    """Hydrograph, budget and evaporation rows for node 103 removed;
    101/102 kept; counts updated."""
    text = '\n'.join(lines)
    assert '\t101\t\tNode101' in lines
    assert '\t102\t\tNode102' in lines
    assert '\t103\t\tNode103' not in lines
    assert any(line.split()[:2] == ['2', '/'] and 'NOUTR' in line for line in lines)
    assert any(line.split()[:2] == ['2', '/'] and 'NBUDR' in line for line in lines)
    # evaporation rows filtered
    assert '\t101\t5\t1' in lines
    assert '\t103\t7\t3' not in lines
    # factor lines untouched
    assert 'FACTK' in text and 'TUNITSK' in text


class TestStreamVersions:

    def test_v40_bed_rows(self, tmp_path):
        lines = run(tmp_path, V40)
        assert_common_filtering(lines)
        assert '\t101\t2.0\t1.0\t300' in lines
        assert '\t102\t2.1\t1.1\t310' in lines
        assert '\t103\t2.2\t1.2\t320' not in lines
        assert any('INTRCTYPE' in line for line in lines)

    def test_v41_bed_rows(self, tmp_path):
        lines = run(tmp_path, V41)
        assert_common_filtering(lines)
        assert '\t101\t2.0\t1.0' in lines
        assert '\t103\t2.2\t1.2' not in lines

    def test_v42_continuation_rows(self, tmp_path):
        lines = run(tmp_path, V42)
        assert_common_filtering(lines)
        # node 101 and its continuation row kept
        assert '\t101\t300\t1001\t2.0\t1.0' in lines
        assert '\t150\t1002\t2.5\t1.5' in lines
        # node 103 and its continuation row removed
        assert '\t103\t320\t1004\t2.2\t1.2' not in lines
        assert '\t160\t1005\t2.6\t1.6' not in lines

    def test_v50_sections(self, tmp_path):
        lines = run(tmp_path, V50)
        assert_common_filtering(lines)
        text = '\n'.join(lines)
        # FNSTRMFL line survives, INTRCTYPE stays with the bed factors
        assert 'FNSTRMFL' in text
        assert any('INTRCTYPE' in line for line in lines)
        # bed rows filtered
        assert '\t101\t2.0\t1.0' in lines
        assert '\t103\t2.2\t1.2' not in lines
        # cross-section rows filtered, factors kept
        assert 'FACTN' in text and 'FACTLT' in text
        assert '\t101\t10.0\t50.0\t0.5\t0.04\t20.0' in lines
        assert '\t103\t12.0\t52.0\t0.5\t0.04\t22.0' not in lines
        # initial-condition rows filtered, factors kept
        assert 'ICTYPE' in text and 'TUNITQ' in text and 'FACTHQ' in text
        assert '\t101\t5.0' in lines
        assert '\t103\t5.2' not in lines
