# test_diagnostics_write_pest_control.py
# Unit tests for diagnostics/write_pest_control.py
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

from iwfm.diagnostics.write_pest_control import (
    write_pest_control,
    _make_param_name,
    _parse_pst,
)


# Minimal PST content for testing
MINIMAL_PST = """\
pcf
* control data
  restart estimation
  10    100     2       0        1
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
  PKH002_L1      none    factor      20.0            2.0             200.0           fackh       1 0 1
  PKH003_L1      tied    factor      15.0            1.5             150.0           fackh       1 0 1
  PKH004_L1      tied    factor      12.0            1.2             120.0           fackh       1 0 1
  PKH005_L1      fixed   factor      8.0             0.8             80.0            fackh       1 0 1
  PKH001_L2      fixed   factor      5.0             0.5             50.0            fackh       1 0 1
  PKH002_L2      fixed   factor      6.0             0.6             60.0            fackh       1 0 1
  c_sn_001       none    factor      0.5             0.05            5.0             stcond      1 0 1
  c_sn_002       tied    factor      0.3             0.03            3.0             stcond      1 0 1
  c_sn_003       fixed   factor      0.1             0.01            1.0             stcond      1 0 1
PKH003_L1\tPKH001_L1
PKH004_L1\tPKH002_L1
c_sn_002\tc_sn_001
* observation groups
  gwhead
* observation data
  obs001  100.0  1.0  gwhead
"""


def _write_pst(content):
    """Write PST content to a temp file and return path."""
    fd, path = tempfile.mkstemp(suffix='.pst')
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


class TestMakeParamName:

    def test_pkh_format(self):
        assert _make_param_name('PKH', 1, 1) == 'PKH001_L1'
        assert _make_param_name('PKH', 42, 2) == 'PKH042_L2'
        assert _make_param_name('PL', 100, 1) == 'PL100_L1'

    def test_stream_format(self):
        assert _make_param_name('c_sn', 1, 0) == 'c_sn_001'
        assert _make_param_name('c_sn', 663, 0) == 'c_sn_663'


class TestParsePst:

    def test_parses_all_params(self):
        path = _write_pst(MINIMAL_PST)
        try:
            sections = _parse_pst(path)
            assert len(sections['param_data']) == 10
            names = [p['name'] for p in sections['param_data']]
            assert 'PKH001_L1' in names
            assert 'c_sn_003' in names
        finally:
            os.unlink(path)

    def test_parses_transforms(self):
        path = _write_pst(MINIMAL_PST)
        try:
            sections = _parse_pst(path)
            by_name = {p['name']: p for p in sections['param_data']}
            assert by_name['PKH001_L1']['transform'] == 'none'
            assert by_name['PKH003_L1']['transform'] == 'tied'
            assert by_name['PKH005_L1']['transform'] == 'fixed'
        finally:
            os.unlink(path)

    def test_skips_tied_data_lines(self):
        """Two-column tied data lines should not appear in param_data."""
        path = _write_pst(MINIMAL_PST)
        try:
            sections = _parse_pst(path)
            for p in sections['param_data']:
                # All parsed params should have 7+ fields (name not 2-col)
                assert p['transform'] in ('none', 'tied', 'fixed', 'log')
        finally:
            os.unlink(path)

    def test_obs_section_preserved(self):
        path = _write_pst(MINIMAL_PST)
        try:
            sections = _parse_pst(path)
            obs_text = ''.join(sections['obs_section'])
            assert '* observation groups' in obs_text
            assert 'gwhead' in obs_text
        finally:
            os.unlink(path)


class TestWritePestControl:

    def _make_recommendations(self):
        """Build minimal recommendations dict."""
        return {
            'param_groups': {
                'PKH_L1': {
                    'prefix': 'PKH',
                    'layer': 1,
                    'pest_group': 'fackh',
                    'transform': 'none',
                    'change_type': 'factor',
                    'representatives': [1],       # PKH001_L1 adjustable
                    'tied_map': {2: 1},            # PKH002_L1 tied to PKH001_L1
                    'n_reps': 1,
                    'n_tied': 1,
                },
            },
            'bound_changes': [],
        }

    def test_writes_valid_pst(self):
        pst_path = _write_pst(MINIMAL_PST)
        try:
            fd, out_path = tempfile.mkstemp(suffix='.pst')
            os.close(fd)
            recs = self._make_recommendations()
            summary = write_pest_control(pst_path, out_path, recs)
            assert summary['n_adjustable'] == 1
            assert summary['n_tied'] == 1
            assert summary['n_fixed'] == 8  # everything else
            assert summary['n_total'] == 10
            assert os.path.exists(out_path)
        finally:
            os.unlink(pst_path)
            os.unlink(out_path)

    def test_tied_params_have_mapping_lines(self):
        pst_path = _write_pst(MINIMAL_PST)
        try:
            fd, out_path = tempfile.mkstemp(suffix='.pst')
            os.close(fd)
            recs = self._make_recommendations()
            write_pest_control(pst_path, out_path, recs)
            with open(out_path) as f:
                content = f.read()
            # PKH002_L1 should be tied to PKH001_L1
            assert 'PKH002_L1\tPKH001_L1' in content
            # Old tied mappings should NOT appear (regenerated)
            assert 'PKH003_L1\tPKH001_L1' not in content
        finally:
            os.unlink(pst_path)
            os.unlink(out_path)

    def test_fixed_params_no_tied_lines(self):
        """Fixed params should not have tied mapping lines."""
        pst_path = _write_pst(MINIMAL_PST)
        try:
            fd, out_path = tempfile.mkstemp(suffix='.pst')
            os.close(fd)
            recs = self._make_recommendations()
            write_pest_control(pst_path, out_path, recs)
            with open(out_path) as f:
                content = f.read()
            # c_sn_003 is fixed, should not appear in tied section
            lines = content.split('\n')
            for line in lines:
                parts = line.split('\t')
                if len(parts) == 2:
                    assert parts[0].strip() != 'c_sn_003'
        finally:
            os.unlink(pst_path)
            os.unlink(out_path)

    def test_validation_rejects_tied_to_fixed(self):
        """Tied param referencing non-adjustable parent raises ValueError."""
        pst_path = _write_pst(MINIMAL_PST)
        try:
            fd, out_path = tempfile.mkstemp(suffix='.pst')
            os.close(fd)
            # Bad recs: PKH002_L1 tied to PKH003_L1, but PKH003_L1
            # is not in representatives
            recs = {
                'param_groups': {
                    'PKH_L1': {
                        'prefix': 'PKH',
                        'layer': 1,
                        'pest_group': 'fackh',
                        'transform': 'none',
                        'change_type': 'factor',
                        'representatives': [1],
                        'tied_map': {2: 3},  # 2 tied to 3, but 3 not a rep
                        'n_reps': 1,
                        'n_tied': 1,
                    },
                },
                'bound_changes': [],
            }
            with pytest.raises(ValueError, match='not adjustable'):
                write_pest_control(pst_path, out_path, recs)
        finally:
            os.unlink(pst_path)
            if os.path.exists(out_path):
                os.unlink(out_path)
