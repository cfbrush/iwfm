# test_diagnostics_read_pest_state.py
# Unit tests for diagnostics/read_pest_state.py
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

from iwfm.diagnostics.read_pest_state import read_pest_state


# Synthetic .res file content (PEST residual output)
RES_CONTENT = """\
 Name                    Group           Measured         Modelled         Residual         Weight
 obs_001                 gwhead          100.000          102.500          -2.500           1.000
 obs_002                 gwhead          110.000          108.000           2.000           1.000
 obs_003                 gwhead          120.000          119.500           0.500           1.000
 obs_004                 swflow          50.000           48.000            2.000           0.500
 obs_005                 swflow          60.000           55.000            5.000           0.500
"""

# Synthetic .rec file content (PEST record)
REC_CONTENT = """\
 PEST run record --------
 Case: test_model

   Iteration  1   phi:  1234.567
   Iteration  2   phi:  987.654
   Iteration  3   phi:  876.543
"""

# Synthetic .par file content
PAR_CONTENT = """\
 single point
  PKH001_L1     10.05
  PKH002_L1     0.101
  PKH003_L1     99.9
"""

# Synthetic .pst param section (for bounds extraction)
PST_BOUNDS_CONTENT = """\
pcf
* control data
  restart estimation
  3    5     1       0        1
  1       1         single  point    1        0      0
  10.0   -3.       0.3     0.01     10       30
  3.0     3.0       0.001
  0.1
  30  0.01  3  3  0.005  4  100  1  1e+25
  0       0         0       0
* parameter groups
  fackh    relative   0.01   0.0   switch   2.0   parabolic
* parameter data
  PKH001_L1      none    factor      10.0            1.0             100.0           fackh       1 0 1
  PKH002_L1      none    factor      5.0             0.1             50.0            fackh       1 0 1
  PKH003_L1      none    factor      50.0            5.0             100.0           fackh       1 0 1
* observation groups
  gwhead
* observation data
  obs001  100.0  1.0  gwhead
"""


def _write_temp(content, suffix):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


class TestReadPestState:

    def test_reads_res_file(self):
        res_path = _write_temp(RES_CONTENT, '.res')
        try:
            result = read_pest_state(res_file=res_path)
            assert result.n_observations == 5
            assert result.rmse > 0
            assert len(result.obs_group_stats) == 2
            groups = {g['group'] for g in result.obs_group_stats}
            assert 'gwhead' in groups
            assert 'swflow' in groups
        finally:
            os.unlink(res_path)

    def test_group_stats_values(self):
        res_path = _write_temp(RES_CONTENT, '.res')
        try:
            result = read_pest_state(res_file=res_path)
            gw = [g for g in result.obs_group_stats
                  if g['group'] == 'gwhead'][0]
            assert gw['n'] == 3
            assert gw['rmse'] > 0
        finally:
            os.unlink(res_path)

    def test_no_files_returns_defaults(self):
        result = read_pest_state()
        assert result.iteration == 0
        assert result.phi == 0.0
        assert result.n_observations == 0

    def test_params_at_bounds_detection(self):
        par_path = _write_temp(PAR_CONTENT, '.par')
        pst_path = _write_temp(PST_BOUNDS_CONTENT, '.pst')
        try:
            result = read_pest_state(par_file=par_path, pst_file=pst_path)
            # PKH002_L1 value=0.101, lower=0.1, pct ~0.0002 → at lower bound
            # PKH003_L1 value=99.9, upper=100.0, pct ~0.9989 → at upper bound
            names_at_bounds = [p['name'] for p in result.params_at_bounds]
            assert 'PKH002_L1' in names_at_bounds
            assert 'PKH003_L1' in names_at_bounds
        finally:
            os.unlink(par_path)
            os.unlink(pst_path)
