#!/usr/bin/env python
# test_hdf5_zbud_gw.py
# Unit tests for hdf5/zbud_gw_core.py, hdf2zbud_gw.py and hdf2zxlsx_gw.py
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

import numpy as np
import pytest

h5py = pytest.importorskip('h5py')

from iwfm.hdf5.zbud_gw_core import read_zone_definition, zbud_gw_aggregate
from iwfm.hdf5.hdf2zbud_gw import hdf2zbud_gw
from iwfm.hdf5.hdf2zxlsx_gw import hdf2zxlsx_gw


# Synthetic IWFM GW zone-budget HDF5: raw per-element data in Layer_N groups
# (one dataset per component, '_Inflow (+)' / '_Outflow (-)' suffixes),
# LayerN_ElemDataColumns element-to-column maps (1-based, 0 = no data), and
# metadata in Attributes. Zone aggregation is driven by a zone definition
# file (ZEXTENT, ZID/ZNAME section, IE/ZONE section).

COMPS = ['GW Storage_Inflow (+)', 'GW Storage_Outflow (-)',
         'Streams_Inflow (+)', 'Streams_Outflow (-)']
N_ELEM, N_LAY, N_TS = 4, 2, 3
# inverse of the default vol_fact/area_fact (0.000022957), NOT exactly 43560,
# so converted values round-trip exactly in assertions
CUFT_PER_ACFT = 1.0 / 0.000022957


def elem_value(lay, ci, elem, t):
    """Deterministic per-cell value in acre-feet (stored in cu ft)."""
    return float(lay * 1000 + ci * 100 + elem * 10 + t)


def make_hdf(path):
    with h5py.File(path, 'w') as f:
        attrs_grp = f.create_group('Attributes')
        a = attrs_grp.attrs
        a['SystemData%NElements'] = N_ELEM
        a['NTimeSteps'] = N_TS
        a['SystemData%NLayers'] = N_LAY
        a['TimeStep%BeginDateAndTime'] = np.bytes_('09/30/1990_24:00')
        a['TimeStep%DeltaT'] = 1
        a['TimeStep%Unit'] = np.bytes_('1MON')
        a['Descriptor'] = np.bytes_('IWFM ZONE BUDGET FIXTURE')

        # element areas: 1..4 acres, stored in sq ft
        attrs_grp.create_dataset(
            'SystemData%ElementAreas',
            data=np.array([1, 2, 3, 4], dtype=float) * CUFT_PER_ACFT)

        attrs_grp.create_dataset(
            'FullDataNames', data=np.array([c.encode() for c in COMPS]))

        # element->column maps, shape (n_comps, n_elements)
        # Layer 1: every element has every component, column = element number
        l1 = np.tile(np.arange(1, N_ELEM + 1), (len(COMPS), 1))
        attrs_grp.create_dataset('Layer1_ElemDataColumns', data=l1)
        # Layer 2: only the GW Storage components have data
        l2 = np.zeros((len(COMPS), N_ELEM), dtype=int)
        l2[0, :] = np.arange(1, N_ELEM + 1)
        l2[1, :] = np.arange(1, N_ELEM + 1)
        attrs_grp.create_dataset('Layer2_ElemDataColumns', data=l2)

        for lay in range(1, N_LAY + 1):
            grp = f.create_group(f'Layer_{lay}')
            for ci, comp in enumerate(COMPS):
                if lay == 2 and ci >= 2:
                    continue    # no Streams data in layer 2
                data = np.zeros((N_TS, N_ELEM))
                for e in range(1, N_ELEM + 1):
                    for t in range(N_TS):
                        data[t, e - 1] = elem_value(lay, ci, e, t) * CUFT_PER_ACFT
                grp.create_dataset(comp, data=data)
    return path


ZONE_FILE_ZEXTENT1 = """C zone definition fixture
C ZEXTENT: 1 = horizontal zones
1
C   ZID   ZNAME
1  North Zone
2  South Zone
C   IE   ZONE
1  1
2  1
3  2
"""


@pytest.fixture
def fixture_files(tmp_path):
    hdf = make_hdf(str(tmp_path / 'zbud.hdf'))
    zones = tmp_path / 'zones.dat'
    zones.write_text(ZONE_FILE_ZEXTENT1)
    return hdf, str(zones)


class TestReadZoneDefinition:

    def test_zextent1(self, tmp_path):
        zf = tmp_path / 'zones.dat'
        zf.write_text(ZONE_FILE_ZEXTENT1)
        zextent, zone_info, element_zones = read_zone_definition(str(zf))
        assert zextent == 1
        assert zone_info == {1: 'North Zone', 2: 'South Zone'}
        assert element_zones == {1: 1, 2: 1, 3: 2}

    def test_zextent0_layer_zones(self, tmp_path):
        zf = tmp_path / 'zones.dat'
        zf.write_text(
            'C fixture\n0\nC   ZID   ZNAME\n1  Zone A\nC   IE   ZONE\n'
            '1  1  1\n1  2  1\n2  1  1\n')
        zextent, zone_info, element_zones = read_zone_definition(str(zf))
        assert zextent == 0
        assert element_zones == {(1, 1): 1, (1, 2): 1, (2, 1): 1}

    def test_missing_zextent_raises(self, tmp_path):
        zf = tmp_path / 'zones.dat'
        zf.write_text('C only comments\nC nothing else\n')
        with pytest.raises(ValueError, match='ZEXTENT'):
            read_zone_definition(str(zf))


class TestZbudGwAggregate:

    def test_zone_aggregation(self, fixture_files):
        hdf, zones = fixture_files
        z = zbud_gw_aggregate(hdf, zones)

        assert z.zextent == 1
        assert z.full_headers == ['GW Storage', 'Streams']
        assert z.n_timesteps == N_TS
        assert z.descriptor == 'IWFM ZONE BUDGET FIXTURE'
        assert sorted(z.zone_data.keys()) == [1, 2]

        # zone areas: zone 1 = elems 1+2 = 3 AC; zone 2 = elem 3 = 3 AC
        assert z.zone_areas[1] == pytest.approx(3.0)
        assert z.zone_areas[2] == pytest.approx(3.0)

        # GW Storage inflow (comp 0) sums layers 1 and 2;
        # zone 1 = elements 1+2, at timestep t:
        expected = sum(elem_value(lay, 0, e, 0) for lay in (1, 2) for e in (1, 2))
        assert z.zone_data[1][0]['in'][0] == pytest.approx(expected)

        # Streams (comp 2/3) has layer 1 data only; zone 2 = element 3
        expected_str_in = elem_value(1, 2, 3, 1)
        assert z.zone_data[2][1]['in'][1] == pytest.approx(expected_str_in)

        # element 4 is in no zone: totals exclude it entirely
        all_in = sum(z.zone_data[zid][0]['in'][0] for zid in (1, 2))
        with_elem4 = sum(elem_value(lay, 0, e, 0) for lay in (1, 2) for e in (1, 2, 3, 4))
        assert all_in < with_elem4

    def test_missing_files_raise(self, tmp_path, fixture_files):
        hdf, zones = fixture_files
        with pytest.raises(FileNotFoundError):
            zbud_gw_aggregate(str(tmp_path / 'nope.hdf'), zones)
        with pytest.raises(FileNotFoundError):
            zbud_gw_aggregate(hdf, str(tmp_path / 'nope.dat'))


class TestHdf2ZbudGw:

    def test_text_output(self, fixture_files, tmp_path):
        hdf, zones = fixture_files
        out = tmp_path / 'out.bud'
        hdf2zbud_gw(hdf, zones, str(out))

        text = out.read_text()
        assert 'GROUNDWATER ZONE BUDGET IN AF FOR ZONE 1 (North Zone)' in text
        assert 'GROUNDWATER ZONE BUDGET IN AF FOR ZONE 2 (South Zone)' in text
        assert 'ZONE AREA: 3.00 AC' in text
        assert 'GW Storage' in text and 'Streams' in text
        # one time-stamped data row per timestep per zone
        assert text.count('09/30/1990_24:00') == 2

        # spot-check a value: zone 1 GW Storage IN at t=0
        expected = sum(elem_value(lay, 0, e, 0) for lay in (1, 2) for e in (1, 2))
        first_data = next(line for line in text.splitlines()
                          if line.strip().startswith('09/30/1990'))
        assert f'{expected:.2f}' in first_data

    def test_verbose(self, fixture_files, tmp_path, capsys):
        hdf, zones = fixture_files
        hdf2zbud_gw(hdf, zones, str(tmp_path / 'out.bud'), verbose=True)
        assert 'Output written to' in capsys.readouterr().out


class TestHdf2ZxlsxGw:

    def test_xlsx_output(self, fixture_files, tmp_path):
        openpyxl = pytest.importorskip('openpyxl')
        hdf, zones = fixture_files
        out = tmp_path / 'out.xlsx'
        hdf2zxlsx_gw(hdf, zones, str(out))

        wb = openpyxl.load_workbook(str(out))
        assert wb.sheetnames == ['Sheet1', 'Zone1_North Zone', 'Zone2_South Zone']

        ws = wb['Zone1_North Zone']
        assert ws['A2'].value == 'GROUNDWATER ZONE BUDGET IN ac.ft. FOR ZONE 1 (North Zone)'
        assert ws['A3'].value == 'ZONE AREA: 3.00 acres'
        assert ws.cell(row=5, column=2).value == 'GW Storage'
        assert ws.cell(row=6, column=2).value == 'IN (+)'

        # data starts at row 7: col 2 = GW Storage IN at t=0
        expected = sum(elem_value(lay, 0, e, 0) for lay in (1, 2) for e in (1, 2))
        assert ws.cell(row=7, column=2).value == pytest.approx(expected)
        # 3 timestep rows
        assert ws.cell(row=9, column=1).value is not None
        assert ws.cell(row=10, column=1).value is None
