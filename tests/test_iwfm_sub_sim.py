#!/usr/bin/env python
# test_iwfm_sub_sim.py
# Unit tests for iwfm_sub_sim.py orchestration (optional-file handling)
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

"""Tests for the iwfm_sub_sim() orchestrator.

The component handlers (sub_gw_file etc.) have their own tests; here they
are replaced with recorders so the tests exercise only the orchestration:
which handlers run, and how optional files (small watersheds, unsaturated
zone) are skipped when the model does not use them.

Regression (2026-07-21, KernIWFM): a blank SWSHEDFL/UNSATFL entry reads as
'' — the path-resolution loop must leave it blank. Resolving '' produced
the Simulation *directory* path, which exists, so the skip guard passed a
directory to sub_swhed_file and crashed.
"""

import pickle

import pytest

import iwfm
import iwfm.gis


def make_sim_file(tmp_path, swshed='', unsat=''):
    """Write a minimal simulation main file; '' marks an unused optional file."""
    def entry(name, tag):
        val = f' {name}' if name else '                    '
        return f'{val}                    / {tag}'

    lines = [
        'C IWFM Simulation Main File',
        ' Test model title',
        ' Somewhere, California',
        ' v1.0',
        entry('PreprocessorOut.bin', '1: PREPROCESSOR OUTPUT'),
        entry('Groundwater.dat', '2: GROUNDWATER'),
        entry('Streams.dat', '3: STREAMS'),
        entry('', '4: LAKES (none)'),
        entry('RootZone.dat', '5: ROOT ZONE'),
        entry(swshed, '6: SMALL WATERSHEDS'),
        entry(unsat, '7: UNSATURATED ZONE'),
        entry('IrrFrac.dat', '8: IRRIGATION FRACTIONS'),
        entry('SupplyAdj.dat', '9: SUPPLY ADJUSTMENT'),
        entry('Precip.dat', '10: PRECIPITATION'),
        entry('ET.dat', '11: EVAPOTRANSPIRATION'),
    ]
    sim_file = tmp_path / 'Simulation.in'
    sim_file.write_text('\n'.join(lines) + '\n')
    # the one hard-required component file must exist
    (tmp_path / 'Groundwater.dat').write_text('C dummy\n')
    return sim_file


@pytest.fixture
def sub_sim_env(tmp_path, monkeypatch):
    """Pickles + recorder handlers; returns (tmp_path, calls dict)."""
    monkeypatch.chdir(tmp_path)
    pickles = {
        'Sub_elems.bin': [[1, 1], [2, 2]],
        'Sub_nodes.bin': [1, 2, 3],
        'Sub_elemnodes.bin': [[1, 2, 3]],
        'Sub_node_coords.bin': [[1, 0.0, 0.0], [2, 1.0, 0.0], [3, 0.0, 1.0]],
        'Sub_snodes.bin': {101: 1},
        'Sub_sub_snodes.bin': [101],
    }
    for name, obj in pickles.items():
        with open(tmp_path / name, 'wb') as f:
            pickle.dump(obj, f)

    calls = {}
    for handler in ('sub_swhed_file', 'sub_unsat_file', 'sub_gw_file',
                    'sub_streams_file', 'sub_rootzone_file', 'sub_sim_file'):
        def record(*a, _h=handler, **k):
            calls.setdefault(_h, []).append(a)
        monkeypatch.setattr(iwfm, handler, record)
    monkeypatch.setattr(iwfm.gis, 'elem2boundingpoly', lambda *a, **k: None)
    return tmp_path, calls


class TestOptionalFileSkipping:

    def test_blank_optional_entries_are_skipped(self, sub_sim_env, capsys):
        """Blank SWSHEDFL/UNSATFL must skip their handlers, not resolve to
        the simulation directory (which exists, defeating the guard)."""
        tmp_path, calls = sub_sim_env
        sim_file = make_sim_file(tmp_path, swshed='', unsat='')

        iwfm.iwfm_sub_sim(str(sim_file), 'unused_pairs.txt', 'Sub', verbose=True)

        assert 'sub_swhed_file' not in calls
        assert 'sub_unsat_file' not in calls
        for handler in ('sub_gw_file', 'sub_streams_file',
                        'sub_rootzone_file', 'sub_sim_file'):
            assert handler in calls
        out = capsys.readouterr().out
        assert 'No small watersheds file' in out
        assert 'No unsaturated zone file' in out

    def test_present_optional_files_are_processed(self, sub_sim_env):
        """When the optional files exist, their handlers run with the
        resolved absolute paths."""
        tmp_path, calls = sub_sim_env
        (tmp_path / 'SWatersheds.dat').write_text('C dummy\n')
        (tmp_path / 'Unsat.dat').write_text('C dummy\n')
        sim_file = make_sim_file(tmp_path, swshed='SWatersheds.dat',
                                 unsat='Unsat.dat')

        iwfm.iwfm_sub_sim(str(sim_file), 'unused_pairs.txt', 'Sub')

        assert calls['sub_swhed_file'][0][0] == str(tmp_path / 'SWatersheds.dat')
        assert calls['sub_unsat_file'][0][0] == str(tmp_path / 'Unsat.dat')

    def test_missing_gw_file_raises(self, sub_sim_env):
        """The groundwater main file is hard-required."""
        tmp_path, calls = sub_sim_env
        sim_file = make_sim_file(tmp_path)
        (tmp_path / 'Groundwater.dat').unlink()

        with pytest.raises(FileNotFoundError, match='gw_file'):
            iwfm.iwfm_sub_sim(str(sim_file), 'unused_pairs.txt', 'Sub')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
