#!/usr/bin/env python
# test_new_sim_files.py
# Unit tests for new_sim_files.py
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

from iwfm.new_sim_files import new_sim_files
from iwfm.iwfm_dataclasses import SimulationFiles


class TestNewSimFiles:
    """Factory that builds a SimulationFiles dataclass from a basename."""

    def test_returns_simulationfiles_instance(self):
        result = new_sim_files('Model')
        assert isinstance(result, SimulationFiles)

    def test_basename_prefix_applied(self):
        result = new_sim_files('Foo')
        assert result.preout == 'Foo_Preprocessor.bin'
        assert result.sim_name == 'Foo_Simulation.in'
        assert result.gw_file == 'Foo_Groundwater.dat'

    def test_all_assigned_fields_have_basename_prefix(self):
        """Fields that new_sim_files() assigns all start with the basename. The
        SimulationFiles dataclass has additional fields (e.g. irrfrac) that
        new_sim_files() does not set; those default to '' and are not checked here."""
        base = 'X'
        result = new_sim_files(base)
        assigned_fields = [
            'preout', 'sim_name', 'gw_file', 'bc_file', 'spfl_file', 'sphd_file',
            'ghd_file', 'cghd_file', 'tsbc_file', 'pump_file', 'epump_file',
            'well_file', 'prate_file', 'sub_file', 'drain_file', 'stream_file',
            'stin_file', 'divspec_file', 'bp_file', 'div_file', 'lake_file',
            'lmax_file', 'root_file', 'np_file', 'pc_file', 'ur_file',
            'nv_file', 'nva_file', 'npa_file', 'pca_file', 'ura_file',
            'swshed_file', 'unsat_file',
        ]
        for field in assigned_fields:
            value = getattr(result, field)
            assert value.startswith(base + '_'), f"{field}={value!r} missing prefix"

    def test_extensions_match_expected(self):
        result = new_sim_files('M')
        assert result.preout.endswith('.bin')
        assert result.sim_name.endswith('.in')
        for f in (result.gw_file, result.bc_file, result.lake_file,
                  result.np_file, result.unsat_file):
            assert f.endswith('.dat')

    def test_empty_basename(self):
        """Edge: empty basename yields '_Foo.bin' style — function does not validate."""
        result = new_sim_files('')
        assert result.preout == '_Preprocessor.bin'

    def test_distinct_assigned_field_values(self):
        """Among fields the function assigns, no two map to the same filename."""
        result = new_sim_files('M')
        assigned = [
            result.preout, result.sim_name, result.gw_file, result.bc_file,
            result.spfl_file, result.sphd_file, result.ghd_file, result.cghd_file,
            result.tsbc_file, result.pump_file, result.epump_file, result.well_file,
            result.prate_file, result.sub_file, result.drain_file, result.stream_file,
            result.stin_file, result.divspec_file, result.bp_file, result.div_file,
            result.lake_file, result.lmax_file, result.root_file, result.np_file,
            result.pc_file, result.ur_file, result.nv_file, result.nva_file,
            result.npa_file, result.pca_file, result.ura_file, result.swshed_file,
            result.unsat_file,
        ]
        assert len(assigned) == len(set(assigned))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
