#!/usr/bin/env python
# test_sub_lake_file.py
# Unit tests for sub/lake_file.py
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


# Simulation lake main file (formats from the IWFM-2015.1.1443 templates):
# v4.0: '#4.0' version line; MXLKELVFL/LKBUDFL/FNLKELVFL file names;
#       FACTK/TUNITK/FACTL; parameter rows `IL CLAKE DLAKE ICHLMAX ICETLK
#       ICPCPLK NAMELK`; FACT + `ILAKE HLAKE` initial elevations.
# v5.0: '#5.0'; LKBUDFL/FNLKELVFL (no MXLKELVFL); parameter rows without
#       ICHLMAX; outflow rating tables (FACTLKL/FACTLKQ/TUNITLKQ, then per
#       lake `IL NPOINTS LKL LKQ` + NPOINTS-1 continuation rows); FACT +
#       initial elevations.
# sub_lake_file() keeps only the rows of lakes in lake_info, verbatim.

LAKE_V40 = """#4.0
C lake main file v4.0 fixture
C-----------------------------------------------
  MaxLakeElev.dat                                    / MXLKELVFL
  ..\\Results\\LakeBud.hdf                           / LKBUDFL
                                                     / FNLKELVFL
C-----------------------------------------------
  1.0                       / FACTK
  1DAY                      / TUNITK
  1.0                       / FACTL
C   IL   CLAKE   DLAKE  ICHLMAX  ICETLK  ICPCPLK  NAMELK
  1\t0.5\t1.0\t1\t10\t11\tLake One
  2\t0.6\t2.0\t2\t20\t21\tLake Two
  3\t0.7\t3.0\t3\t30\t31\tLake Three
C-----------------------------------------------
  1.0                       / FACT
C   ILAKE   HLAKE
  1\t400.0
  2\t410.0
  3\t420.0
"""

LAKE_V50 = """#5.0
C lake main file v5.0 fixture
C-----------------------------------------------
  ..\\Results\\LakeBud.hdf                           / LKBUDFL
                                                     / FNLKELVFL
C-----------------------------------------------
  1.0                       / FACTK
  1DAY                      / TUNITK
  1.0                       / FACTL
C   IL   CLAKE   DLAKE  ICETLK  ICPCPLK  NAMELK
  1\t0.5\t1.0\t10\t11\tLake One
  2\t0.6\t2.0\t20\t21\tLake Two
C-----------------------------------------------
  1.0                       / FACTLKL
  1.0                       / FACTLKQ
  1MON                      / TUNITLKQ
C   IL   NPOINTS   LKL   LKQ
  1\t3\t400.0\t0.0
  405.0\t100.0
  410.0\t500.0
  2\t2\t300.0\t0.0
  305.0\t50.0
C-----------------------------------------------
  1.0                       / FACT
C   ILAKE   HLAKE
  1\t400.0
  2\t300.0
"""


def make_files(tmp_path, content):
    old = tmp_path / 'Lake.dat'
    old.write_text(content)
    sim_files = SimulationFiles(lake_file=str(old))
    sim_files_new = SimulationFiles(lake_file=str(tmp_path / 'Sub_Lake.dat'))
    return sim_files, sim_files_new


def lake_info_for(ids):
    """Minimal sub_pp_lakes()-shaped lake_info: first item is the lake ID."""
    return [[str(i), '1', '2', '1', f'Lake {i}', [i * 10]] for i in ids]


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


class TestSubLakeFileV40:

    def test_subset_of_lakes_kept(self, tmp_path):
        sim_files, sim_files_new = make_files(tmp_path, LAKE_V40)
        iwfm.sub_lake_file(sim_files, sim_files_new, lake_info_for([1, 3]))

        lines = read_lines(sim_files_new.lake_file)
        text = '\n'.join(lines)
        # lake 2 parameter and initial-elevation rows removed
        assert '  2\t0.6\t2.0\t2\t20\t21\tLake Two' not in lines
        assert '  2\t410.0' not in lines
        # lakes 1 and 3 kept verbatim
        assert '  1\t0.5\t1.0\t1\t10\t11\tLake One' in lines
        assert '  3\t0.7\t3.0\t3\t30\t31\tLake Three' in lines
        assert '  1\t400.0' in lines
        assert '  3\t420.0' in lines
        # file-name lines and version line unchanged
        assert lines[0] == '#4.0'
        assert 'MaxLakeElev.dat' in text
        # exactly two rows were removed
        assert len(lines) == len(LAKE_V40.splitlines()) - 2

    def test_all_lakes_kept_is_identical(self, tmp_path):
        sim_files, sim_files_new = make_files(tmp_path, LAKE_V40)
        iwfm.sub_lake_file(sim_files, sim_files_new, lake_info_for([1, 2, 3]))
        assert read_lines(sim_files_new.lake_file) == LAKE_V40.splitlines()


class TestSubLakeFileV50:

    def test_rating_table_blocks_filtered(self, tmp_path):
        sim_files, sim_files_new = make_files(tmp_path, LAKE_V50)
        iwfm.sub_lake_file(sim_files, sim_files_new, lake_info_for([2]))

        lines = read_lines(sim_files_new.lake_file)
        # lake 1 parameter row, 3-row rating block, and initial elevation removed
        assert '  1\t0.5\t1.0\t10\t11\tLake One' not in lines
        assert '  1\t3\t400.0\t0.0' not in lines
        assert '  405.0\t100.0' not in lines
        assert '  410.0\t500.0' not in lines
        assert '  1\t400.0' not in lines
        # lake 2 rows all kept verbatim
        assert '  2\t0.6\t2.0\t20\t21\tLake Two' in lines
        assert '  2\t2\t300.0\t0.0' in lines
        assert '  305.0\t50.0' in lines
        assert '  2\t300.0' in lines
        # 6 rows removed (1 param + 3 rating + 1 init + ... )
        assert len(lines) == len(LAKE_V50.splitlines()) - 5

    def test_all_lakes_kept_is_identical(self, tmp_path):
        sim_files, sim_files_new = make_files(tmp_path, LAKE_V50)
        iwfm.sub_lake_file(sim_files, sim_files_new, lake_info_for([1, 2]))
        assert read_lines(sim_files_new.lake_file) == LAKE_V50.splitlines()


class TestSubLakeFileGeneral:

    def test_verbose_output(self, tmp_path, capsys):
        sim_files, sim_files_new = make_files(tmp_path, LAKE_V40)
        iwfm.sub_lake_file(
            sim_files, sim_files_new, lake_info_for([1]), verbose=True)
        captured = capsys.readouterr()
        assert 'Wrote submodel lake file' in captured.out
        assert sim_files_new.lake_file in captured.out
