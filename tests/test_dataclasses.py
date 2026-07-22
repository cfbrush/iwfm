# test_dataclasses.py
# Tests for dataclass definitions used throughout the iwfm package
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
from dataclasses import fields

from iwfm.iwfm_dataclasses import (
    _DictAccessMixin,
    PreprocessorFiles,
    SimulationFiles,
    WellInfo,
    RootzoneFiles,
    GroundwaterFiles,
)


# ===== _DictAccessMixin tests (via PreprocessorFiles as concrete class) =====

class TestDictAccessMixin:
    '''Tests for _DictAccessMixin backward-compatible dict-style access.'''

    def test_getitem(self):
        '''Test bracket-style read access.'''
        pf = PreprocessorFiles(prename='test.in', preout='test.bin')
        assert pf['prename'] == 'test.in'
        assert pf['preout'] == 'test.bin'

    def test_getitem_missing_key_raises_keyerror(self):
        '''Test that accessing a nonexistent key raises KeyError.'''
        pf = PreprocessorFiles()
        with pytest.raises(KeyError):
            _ = pf['nonexistent_field']

    def test_setitem(self):
        '''Test bracket-style write access.'''
        pf = PreprocessorFiles()
        pf['prename'] = 'updated.in'
        assert pf.prename == 'updated.in'
        assert pf['prename'] == 'updated.in'

    def test_setitem_missing_key_raises_keyerror(self):
        '''Test that setting a nonexistent key raises KeyError.'''
        pf = PreprocessorFiles()
        with pytest.raises(KeyError):
            pf['nonexistent_field'] = 'value'

    def test_contains(self):
        '''Test "in" operator for field membership.'''
        pf = PreprocessorFiles()
        assert 'prename' in pf
        assert 'preout' in pf
        assert 'nonexistent_field' not in pf

    def test_len(self):
        '''Test len() returns number of fields.'''
        pf = PreprocessorFiles()
        assert len(pf) == 7  # prename, preout, elem_file, node_file, strat_file, stream_file, lake_file

    def test_iter(self):
        '''Test iteration yields field names.'''
        pf = PreprocessorFiles()
        field_names = list(pf)
        assert field_names == ['prename', 'preout', 'elem_file', 'node_file',
                               'strat_file', 'stream_file', 'lake_file']

    def test_get_existing_key(self):
        '''Test get() returns field value for existing key.'''
        pf = PreprocessorFiles(prename='test.in')
        assert pf.get('prename') == 'test.in'

    def test_get_missing_key_returns_default(self):
        '''Test get() returns default for missing key.'''
        pf = PreprocessorFiles()
        assert pf.get('nonexistent', 'fallback') == 'fallback'
        assert pf.get('nonexistent') is None

    def test_keys(self):
        '''Test keys() returns all field names.'''
        pf = PreprocessorFiles()
        assert pf.keys() == ['prename', 'preout', 'elem_file', 'node_file',
                              'strat_file', 'stream_file', 'lake_file']

    def test_values(self):
        '''Test values() returns all field values.'''
        pf = PreprocessorFiles(prename='a', preout='b')
        vals = pf.values()
        assert vals[0] == 'a'
        assert vals[1] == 'b'
        # remaining fields default to ''
        assert all(v == '' for v in vals[2:])

    def test_items(self):
        '''Test items() returns (name, value) pairs.'''
        pf = PreprocessorFiles(prename='x', preout='y')
        items = pf.items()
        assert ('prename', 'x') in items
        assert ('preout', 'y') in items
        assert len(items) == 7

    def test_dict_and_attr_access_equivalent(self):
        '''Test that bracket access and attribute access return same values.'''
        pf = PreprocessorFiles(
            prename='pre.in', preout='pre.bin', elem_file='elem.dat',
            node_file='node.dat', strat_file='strat.dat',
            stream_file='stream.dat', lake_file='lake.dat',
        )
        for name in pf.keys():
            assert pf[name] == getattr(pf, name)


# ===== PreprocessorFiles tests =====

class TestPreprocessorFiles:
    '''Tests for PreprocessorFiles dataclass.'''

    def test_default_construction(self):
        '''Test that all fields default to empty string.'''
        pf = PreprocessorFiles()
        for f in fields(pf):
            assert getattr(pf, f.name) == ''

    def test_keyword_construction(self):
        '''Test construction with keyword arguments.'''
        pf = PreprocessorFiles(
            prename='C2VSimFG_Preprocessor.in',
            preout='C2VSimFG_Preprocessor.bin',
            elem_file='C2VSimFG_Elements.dat',
            node_file='C2VSimFG_Nodes.dat',
            strat_file='C2VSimFG_Stratigraphy.dat',
            stream_file='C2VSimFG_StreamSpec.dat',
            lake_file='C2VSimFG_Lakes.dat',
        )
        assert pf.prename == 'C2VSimFG_Preprocessor.in'
        assert pf.lake_file == 'C2VSimFG_Lakes.dat'

    def test_field_count(self):
        '''Test that PreprocessorFiles has exactly 7 fields.'''
        assert len(fields(PreprocessorFiles)) == 7

    def test_mutable(self):
        '''Test that fields can be modified after creation.'''
        pf = PreprocessorFiles()
        pf.prename = 'new_value.in'
        assert pf.prename == 'new_value.in'

    def test_inherits_dict_access(self):
        '''Test that PreprocessorFiles supports dict-style access.'''
        pf = PreprocessorFiles(prename='test.in')
        assert pf['prename'] == 'test.in'
        assert 'prename' in pf


# ===== SimulationFiles tests =====

class TestSimulationFiles:
    '''Tests for SimulationFiles dataclass.'''

    def test_default_construction(self):
        '''Test that all fields default to empty string.'''
        sf = SimulationFiles()
        for f in fields(sf):
            assert getattr(sf, f.name) == ''

    def test_field_count(self):
        '''Test that SimulationFiles has the expected number of fields.'''
        sf = SimulationFiles()
        expected_fields = [
            'preout', 'sim_name', 'gw_file', 'bc_file', 'spfl_file',
            'sphd_file', 'ghd_file', 'cghd_file', 'tsbc_file',
            'pump_file', 'epump_file', 'well_file', 'prate_file',
            'sub_file', 'drain_file', 'stream_file', 'stin_file',
            'divspec_file', 'bp_file', 'div_file', 'lake_file',
            'lmax_file', 'root_file', 'np_file', 'pc_file', 'ur_file',
            'nv_file', 'dest_file', 'nva_file', 'npa_file', 'pca_file', 'ura_file',
            'swshed_file', 'unsat_file', 'irrfrac', 'supplyadj',
            'precip', 'et', 'start', 'step', 'end',
        ]
        actual_fields = [f.name for f in fields(sf)]
        assert actual_fields == expected_fields

    def test_keyword_construction_subset(self):
        '''Test construction with a subset of keyword arguments.'''
        sf = SimulationFiles(
            preout='sim_Preprocessor.bin',
            sim_name='sim_Simulation.in',
            gw_file='sim_Groundwater.dat',
            start='10/01/1973',
            end='09/30/2015',
            step='1MON',
        )
        assert sf.preout == 'sim_Preprocessor.bin'
        assert sf.start == '10/01/1973'
        assert sf.end == '09/30/2015'
        assert sf.step == '1MON'
        # unset fields remain ''
        assert sf.bc_file == ''

    def test_inherits_dict_access(self):
        '''Test that SimulationFiles supports dict-style access.'''
        sf = SimulationFiles(gw_file='gw.dat')
        assert sf['gw_file'] == 'gw.dat'
        sf['gw_file'] = 'updated_gw.dat'
        assert sf.gw_file == 'updated_gw.dat'

    def test_iteration_order(self):
        '''Test that iteration yields fields in definition order.'''
        sf = SimulationFiles()
        names = list(sf)
        assert names[0] == 'preout'
        assert names[1] == 'sim_name'
        assert names[-1] == 'end'


# ===== WellInfo tests =====

class TestWellInfo:
    '''Tests for WellInfo dataclass.'''

    def test_construction(self):
        '''Test construction with all fields.'''
        wi = WellInfo(column=3, x=1234.5, y=6789.0, layer=2, name='well_001')
        assert wi.column == 3
        assert wi.x == 1234.5
        assert wi.y == 6789.0
        assert wi.layer == 2
        assert wi.name == 'well_001'

    def test_default_construction(self):
        '''Test that WellInfo fields have defaults.'''
        wi = WellInfo()
        assert wi.column == 0
        assert wi.x == 0.0
        assert wi.y == 0.0
        assert wi.layer == 0
        assert wi.name == ''

    def test_field_count(self):
        '''Test that WellInfo has exactly 5 fields.'''
        assert len(fields(WellInfo)) == 5

    def test_field_names(self):
        '''Test WellInfo field names.'''
        names = [f.name for f in fields(WellInfo)]
        assert names == ['column', 'x', 'y', 'layer', 'name']

    def test_mutable(self):
        '''Test that WellInfo fields can be updated.'''
        wi = WellInfo(column=1, x=100.0, y=200.0, layer=1, name='old')
        wi.name = 'new'
        wi.layer = 3
        assert wi.name == 'new'
        assert wi.layer == 3

    def test_no_dict_access(self):
        '''Test that WellInfo does NOT support dict-style bracket access.'''
        wi = WellInfo(column=1, x=0.0, y=0.0, layer=1, name='test')
        with pytest.raises(TypeError):
            _ = wi['column']

    def test_equality(self):
        '''Test that two WellInfo with same values are equal.'''
        wi1 = WellInfo(column=1, x=100.0, y=200.0, layer=2, name='well_a')
        wi2 = WellInfo(column=1, x=100.0, y=200.0, layer=2, name='well_a')
        assert wi1 == wi2

    def test_inequality(self):
        '''Test that two WellInfo with different values are not equal.'''
        wi1 = WellInfo(column=1, x=100.0, y=200.0, layer=2, name='well_a')
        wi2 = WellInfo(column=2, x=100.0, y=200.0, layer=2, name='well_a')
        assert wi1 != wi2

    def test_hydtyp0_pattern(self):
        '''Test WellInfo construction mimicking HYDTYP=0 (X-Y coords).'''
        wi = WellInfo(column=5, x=6543210.0, y=1234567.0, layer=1, name='01s01e08a001s')
        assert wi.x != 0.0
        assert wi.y != 0.0

    def test_hydtyp1_pattern(self):
        '''Test WellInfo construction mimicking HYDTYP=1 (node number, no coords).'''
        wi = WellInfo(column=5, x=0.0, y=0.0, layer=1, name='01s01e08a001s')
        assert wi.x == 0.0
        assert wi.y == 0.0


# ===== RootzoneFiles tests =====

class TestRootzoneFiles:
    '''Tests for RootzoneFiles dataclass.'''

    def test_default_construction(self):
        '''Test that all fields default to empty string.'''
        rz = RootzoneFiles()
        for f in fields(rz):
            assert getattr(rz, f.name) == ''

    def test_field_count(self):
        '''Test that RootzoneFiles has exactly 7 fields.'''
        assert len(fields(RootzoneFiles)) == 7

    def test_field_names(self):
        '''Test RootzoneFiles field names.'''
        names = [f.name for f in fields(RootzoneFiles)]
        assert names == ['np_file', 'p_file', 'ur_file', 'nr_file',
                         'rf_file', 'ru_file', 'ir_file']

    def test_keyword_construction(self):
        '''Test construction with keyword arguments.'''
        rz = RootzoneFiles(
            np_file='NonPondedCrop.dat',
            p_file='PondedCrop.dat',
            ur_file='Urban.dat',
            nr_file='NativeVeg.dat',
            rf_file='ReturnFlow.dat',
            ru_file='Reuse.dat',
            ir_file='IrrigPeriod.dat',
        )
        assert rz.np_file == 'NonPondedCrop.dat'
        assert rz.ir_file == 'IrrigPeriod.dat'

    def test_inherits_dict_access(self):
        '''Test that RootzoneFiles supports dict-style access.'''
        rz = RootzoneFiles(np_file='np.dat')
        assert rz['np_file'] == 'np.dat'
        assert 'np_file' in rz
        assert 'nonexistent' not in rz


# ===== GroundwaterFiles tests =====

class TestGroundwaterFiles:
    '''Tests for GroundwaterFiles dataclass.'''

    def test_default_construction(self):
        '''Test that all fields default to "none".'''
        gw = GroundwaterFiles()
        for f in fields(gw):
            assert getattr(gw, f.name) == 'none'

    def test_field_count(self):
        '''Test that GroundwaterFiles has exactly 5 fields.'''
        assert len(fields(GroundwaterFiles)) == 5

    def test_field_names(self):
        '''Test GroundwaterFiles field names.'''
        names = [f.name for f in fields(GroundwaterFiles)]
        assert names == ['bc_file', 'drain_file', 'pump_file', 'subs_file', 'headall']

    def test_keyword_construction(self):
        '''Test construction with keyword arguments.'''
        gw = GroundwaterFiles(
            bc_file='BC.dat',
            drain_file='TileDrain.dat',
            pump_file='Pumping.dat',
            subs_file='Subsidence.dat',
            headall='GW_HeadAll.out',
        )
        assert gw.bc_file == 'BC.dat'
        assert gw.headall == 'GW_HeadAll.out'

    def test_inherits_dict_access(self):
        '''Test that GroundwaterFiles supports dict-style access.'''
        gw = GroundwaterFiles(bc_file='bc.dat')
        assert gw['bc_file'] == 'bc.dat'
        assert len(gw) == 5

    def test_none_defaults_differ_from_empty(self):
        '''Test that GroundwaterFiles defaults are "none", not empty string.'''
        gw = GroundwaterFiles()
        assert gw.bc_file == 'none'
        assert gw.bc_file != ''


# ===== Cross-dataclass integration tests =====

class TestDataclassIntegration:
    '''Integration tests across dataclass types.'''

    def test_preprocessor_in_dict(self):
        '''Test using PreprocessorFiles as a dict value (common pattern).'''
        d = {'model_a': PreprocessorFiles(prename='a.in'),
             'model_b': PreprocessorFiles(prename='b.in')}
        assert d['model_a'].prename == 'a.in'
        assert d['model_b'].prename == 'b.in'

    def test_wellinfo_as_dict_value(self):
        '''Test using WellInfo as dict values (the primary use pattern).'''
        well_dict = {}
        well_dict['well_001'] = WellInfo(column=1, x=100.0, y=200.0, layer=1, name='well_001')
        well_dict['well_002'] = WellInfo(column=2, x=300.0, y=400.0, layer=2, name='well_002')
        assert well_dict['well_001'].column == 1
        assert well_dict['well_002'].x == 300.0
        assert len(well_dict) == 2

    def test_simulation_files_path_iteration(self):
        '''Test iterating over SimulationFiles to resolve file paths.'''
        sf = SimulationFiles(
            gw_file='Groundwater.dat',
            stream_file='Streams.dat',
            root_file='Rootzone.dat',
        )
        # Mimic path resolution pattern from iwfm_sub_sim.py
        base = '/model/input/'
        for name in sf:
            val = sf[name]
            if isinstance(val, str) and val and val != '':
                sf[name] = base + val
        assert sf.gw_file == '/model/input/Groundwater.dat'
        assert sf.stream_file == '/model/input/Streams.dat'

    def test_all_dict_access_classes_have_items(self):
        '''Test that all _DictAccessMixin subclasses support items().'''
        for cls in [PreprocessorFiles, SimulationFiles, RootzoneFiles, GroundwaterFiles]:
            obj = cls()
            items = obj.items()
            assert isinstance(items, list)
            assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in items)

    def test_all_dict_access_classes_have_keys(self):
        '''Test that all _DictAccessMixin subclasses support keys().'''
        for cls in [PreprocessorFiles, SimulationFiles, RootzoneFiles, GroundwaterFiles]:
            obj = cls()
            keys = obj.keys()
            assert isinstance(keys, list)
            assert all(isinstance(k, str) for k in keys)

    def test_all_dict_access_classes_have_values(self):
        '''Test that all _DictAccessMixin subclasses support values().'''
        for cls in [PreprocessorFiles, SimulationFiles, RootzoneFiles, GroundwaterFiles]:
            obj = cls()
            values = obj.values()
            assert isinstance(values, list)


# ===== Import tests =====

class TestDataclassImports:
    '''Test that dataclasses are properly importable from expected paths.'''

    def test_import_from_dataclasses_module(self):
        '''Test direct import from iwfm.dataclasses.'''
        from iwfm.iwfm_dataclasses import PreprocessorFiles, SimulationFiles
        from iwfm.iwfm_dataclasses import WellInfo, RootzoneFiles, GroundwaterFiles
        assert PreprocessorFiles is not None
        assert SimulationFiles is not None
        assert WellInfo is not None
        assert RootzoneFiles is not None
        assert GroundwaterFiles is not None

    def test_import_from_iwfm_package(self):
        '''Test import from top-level iwfm package.'''
        from iwfm import PreprocessorFiles, SimulationFiles
        from iwfm import WellInfo, RootzoneFiles, GroundwaterFiles
        assert PreprocessorFiles is not None
        assert SimulationFiles is not None
        assert WellInfo is not None
        assert RootzoneFiles is not None
        assert GroundwaterFiles is not None

    def test_import_mixin(self):
        '''Test that the mixin is importable (for advanced use cases).'''
        from iwfm.iwfm_dataclasses import _DictAccessMixin
        assert _DictAccessMixin is not None
