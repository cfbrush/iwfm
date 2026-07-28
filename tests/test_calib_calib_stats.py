# test_calib_calib_stats.py
# Test calib/calib_stats functions
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
from unittest.mock import patch
from pathlib import Path
import numpy as np
from datetime import datetime

from iwfm.iwfm_dataclasses import WellInfo


def test_calib_stats_imports():
    '''Test that calib_stats imports are clean (verifies fix).'''
    calib_stats_path = Path(__file__).parent.parent / 'iwfm' / 'calib' / 'calib_stats.py'
    source = calib_stats_path.read_text()

    # Should have 'import iwfm' not 'import iwfm as iwfm'
    assert 'import iwfm as iwfm' not in source
    assert 'import iwfm' in source


def test_calib_stats_gw_hyd_dict_usage():
    '''Test that gw_hyd_dict is used correctly as local variable (verifies fix).'''
    calib_stats_path = Path(__file__).parent.parent / 'iwfm' / 'calib' / 'calib_stats.py'
    source = calib_stats_path.read_text()

    # Should NOT have 'iwfm.hyd_dict' or 'iwfm.gw_hyd_dict' anywhere
    assert 'iwfm.hyd_dict' not in source
    assert 'iwfm.gw_hyd_dict' not in source
    # Should have local variable access
    assert 'gw_hyd_dict.get' in source or 'gw_hyd_dict[' in source


def test_calib_stats_no_redundant_assignment():
    '''Test that redundant assignment was removed (verifies fix).'''
    calib_stats_path = Path(__file__).parent.parent / 'iwfm' / 'calib' / 'calib_stats.py'
    source = calib_stats_path.read_text()

    # Should NOT have the redundant assignment pattern
    lines = source.split('\n')
    for line in lines:
        # Check for pattern like 'x[i][j] = x[i][j]' where both sides are identical
        stripped = line.strip()
        if '=' in stripped and not stripped.startswith('#'):
            parts = stripped.split('=')
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                # They shouldn't be exactly the same (redundant)
                if left and right and left == right:
                    pytest.fail(f"Found redundant assignment: {line}")


def test_calib_stats_spacing_fixed():
    '''Test that spacing issue was fixed (verifies fix).'''
    calib_stats_path = Path(__file__).parent.parent / 'iwfm' / 'calib' / 'calib_stats.py'
    source = calib_stats_path.read_text()

    # Should have proper spacing around '='
    # Check the specific line that had the issue
    lines = source.split('\n')
    for i, line in enumerate(lines):
        if 'items=' in line and 'gwhyd_lines' in line:
            pytest.fail(f"Found spacing issue at line {i+1}: {line}")


def test_read_sim_hyd_function_signature():
    '''Test that read_sim_hyd has correct function signature.'''
    from iwfm.read_sim_hyd import read_sim_hyd
    import inspect

    sig = inspect.signature(read_sim_hyd)
    params = list(sig.parameters.keys())

    assert 'gwhyd_file' in params
    assert 'head_divisor' in params
    assert sig.parameters['head_divisor'].default == 1.0


def test_read_sim_hyd_basic(tmp_path):
    '''Test basic functionality of read_sim_hyd.'''
    from iwfm.read_sim_hyd import read_sim_hyd

    # Create a mock hydrograph file
    hyd_file = tmp_path / 'test_hyd.out'
    content = [
        '# Header line 1',
        '# Header line 2',
        '# Header line 3',
        '# Header line 4',
        '# Header line 5',
        '# Header line 6',
        '# Header line 7',
        '# Header line 8',
        '# Header line 9',
        '01/01/2020  100.5  200.3  150.7',
        '01/02/2020  101.2  201.5  151.3',
        '01/03/2020  102.0  202.1  152.0',
    ]
    hyd_file.write_text('\n'.join(content))

    result = read_sim_hyd(str(hyd_file))

    # Should return numpy array
    assert isinstance(result, np.ndarray)
    # Should have 3 data rows
    assert len(result) == 3
    # Each row should have 4 elements (date + 3 values)
    assert len(result[0]) == 4


def test_read_sim_hyd_handles_24_00_time(tmp_path):
    '''Test that read_sim_hyd handles _24:00 time format.'''
    from iwfm.read_sim_hyd import read_sim_hyd

    # Create a mock hydrograph file with _24:00 format
    hyd_file = tmp_path / 'test_hyd.out'
    content = [
        '# Header', '# Header', '# Header', '# Header', '# Header',
        '# Header', '# Header', '# Header', '# Header',
        '01/01/2020_24:00  100.5  200.3',
        '01/02/2020_24:00  101.2  201.5',
    ]
    hyd_file.write_text('\n'.join(content))

    # Should not raise an error
    result = read_sim_hyd(str(hyd_file))
    assert len(result) == 2


def test_calib_stats_function_signature():
    '''Test that calib_stats has correct function signature.'''
    from iwfm.calib.calib_stats import calib_stats
    import inspect

    sig = inspect.signature(calib_stats)
    params = list(sig.parameters.keys())

    assert 'pest_smp_file' in params
    assert 'gwhyd_info_file' in params
    assert 'gwhyd_file' in params
    assert 'verbose' in params
    assert sig.parameters['verbose'].default is False


def test_calib_stats_basic(tmp_path):
    '''Test basic functionality of calib_stats.'''
    from iwfm.calib.calib_stats import calib_stats

    # Create mock files
    pest_smp_file = tmp_path / 'test.smp'
    gwhyd_info_file = tmp_path / 'gwhyd.dat'
    gwhyd_file = tmp_path / 'gwhyd.out'

    # Create PEST SMP file content
    smp_content = [
        'WELL001  01/01/2020  12:00:00  100.5',
        'WELL002  01/01/2020  12:00:00  200.3',
    ]
    pest_smp_file.write_text('\n'.join(smp_content))
    gwhyd_info_file.write_text('dummy')
    gwhyd_file.write_text('dummy')

    # Mock simulated hydrograph data
    mock_simhyd = np.array([
        [datetime(2020, 1, 1), 100.0, 200.0],
    ])

    # Mock gw_hyd_dict with proper structure: WellInfo instances
    mock_gw_hyd_dict = {
        'WELL001': WellInfo(column=1, x=100.5, y=200.3, layer=1, name='well001'),
        'WELL002': WellInfo(column=2, x=150.7, y=250.9, layer=2, name='well002'),
    }

    with patch('iwfm.safe_parse_date', side_effect=lambda d, _: datetime.strptime(d.split()[0], '%m/%d/%Y')):
        with patch('iwfm.read_hyd_dict', return_value=mock_gw_hyd_dict):
            with patch('iwfm.calib.sim_equiv', return_value=100.5):
                with patch('iwfm.calib.rmse_calc', return_value=1.5):
                    with patch('iwfm.calib.bias_calc', return_value=0.5):
                        with patch('iwfm.calib.calib_stats.read_sim_hyd', return_value=mock_simhyd):
                            # Should not raise any errors
                            calib_stats(str(pest_smp_file), str(gwhyd_info_file), str(gwhyd_file), verbose=False)

    # Verify output files were created
    assert (tmp_path / 'gwhyd_sim_obs.txt').exists()
    assert (tmp_path / 'gwhyd_rmse.txt').exists()
    assert (tmp_path / 'gwhyd_rmse_all.txt').exists()


def test_calib_stats_uses_local_gw_hyd_dict(tmp_path):
    '''Test that calib_stats correctly uses local gw_hyd_dict variable (verifies fix).'''
    from iwfm.calib.calib_stats import calib_stats

    # Create mock files
    pest_smp_file = tmp_path / 'test.smp'
    gwhyd_info_file = tmp_path / 'gwhyd.dat'
    gwhyd_file = tmp_path / 'gwhyd.out'

    smp_content = ['WELL001  01/01/2020  12:00:00  100.5']
    pest_smp_file.write_text('\n'.join(smp_content))
    gwhyd_info_file.write_text('dummy')
    gwhyd_file.write_text('dummy')

    # Mock gw_hyd_dict with proper structure: WellInfo instances
    mock_gw_hyd_dict = {'WELL001': WellInfo(column=1, x=100.5, y=200.3, layer=1, name='well001')}
    mock_simhyd = np.array([[datetime(2020, 1, 1), 100.0]])

    with patch('iwfm.safe_parse_date', return_value=datetime(2020, 1, 1)):
        with patch('iwfm.read_hyd_dict', return_value=mock_gw_hyd_dict):
            with patch('iwfm.calib.sim_equiv', return_value=100.5):
                with patch('iwfm.calib.rmse_calc', return_value=1.5):
                    with patch('iwfm.calib.bias_calc', return_value=0.5):
                        with patch('iwfm.calib.calib_stats.read_sim_hyd', return_value=mock_simhyd):
                            # This should work without AttributeError about iwfm.gw_hyd_dict
                            try:
                                calib_stats(str(pest_smp_file), str(gwhyd_info_file), str(gwhyd_file))
                            except AttributeError as e:
                                if 'hyd_dict' in str(e) or 'gw_hyd_dict' in str(e):
                                    pytest.fail(f"Still trying to access module attribute: {e}")
                                raise


def test_calib_stats_verbose_mode(tmp_path, capsys):
    '''Test that calib_stats verbose mode produces output.'''
    from iwfm.calib.calib_stats import calib_stats

    # Create mock files
    pest_smp_file = tmp_path / 'test.smp'
    gwhyd_info_file = tmp_path / 'gwhyd.dat'
    gwhyd_file = tmp_path / 'gwhyd.out'

    smp_content = ['WELL001  01/01/2020  12:00:00  100.5']
    pest_smp_file.write_text('\n'.join(smp_content))
    gwhyd_info_file.write_text('dummy')
    gwhyd_file.write_text('dummy')

    mock_simhyd = np.array([[datetime(2020, 1, 1), 100.0]])

    # Mock gw_hyd_dict with proper structure: WellInfo instances
    mock_gw_hyd_dict = {'WELL001': WellInfo(column=1, x=100.5, y=200.3, layer=1, name='well001')}

    with patch('iwfm.safe_parse_date', return_value=datetime(2020, 1, 1)):
        with patch('iwfm.read_hyd_dict', return_value=mock_gw_hyd_dict):
            with patch('iwfm.calib.sim_equiv', return_value=100.5):
                with patch('iwfm.calib.rmse_calc', return_value=1.5):
                    with patch('iwfm.calib.bias_calc', return_value=0.5):
                        with patch('iwfm.calib.calib_stats.read_sim_hyd', return_value=mock_simhyd):
                            calib_stats(str(pest_smp_file), str(gwhyd_info_file), str(gwhyd_file), verbose=True)

    # Capture output
    captured = capsys.readouterr()
    # Verbose mode should print file names
    assert str(pest_smp_file) in captured.out


def test_calib_stats_output_file_format(tmp_path):
    '''Test that calib_stats creates correctly formatted output files.'''
    from iwfm.calib.calib_stats import calib_stats

    pest_smp_file = tmp_path / 'test.smp'
    gwhyd_info_file = tmp_path / 'gwhyd.dat'
    gwhyd_file = tmp_path / 'gwhyd.out'

    smp_content = ['WELL001  01/01/2020  12:00:00  100.5']
    pest_smp_file.write_text('\n'.join(smp_content))
    gwhyd_info_file.write_text('dummy')
    gwhyd_file.write_text('dummy')

    # Mock gw_hyd_dict with proper structure: WellInfo instances
    mock_gw_hyd_dict = {'WELL001': WellInfo(column=1, x=100.5, y=200.3, layer=1, name='well001')}

    with patch('iwfm.safe_parse_date', return_value=datetime(2020, 1, 1)):
        with patch('iwfm.read_hyd_dict', return_value=mock_gw_hyd_dict):
            with patch('iwfm.calib.sim_equiv', return_value=100.5):
                with patch('iwfm.calib.rmse_calc', return_value=1.5):
                    with patch('iwfm.calib.bias_calc', return_value=0.5):
                        with patch('iwfm.calib.calib_stats.read_sim_hyd', return_value=np.array([[datetime(2020, 1, 1), 100.0]])):
                            calib_stats(str(pest_smp_file), str(gwhyd_info_file), str(gwhyd_file))

    # Check sim_obs file format
    sim_obs_file = tmp_path / 'gwhyd_sim_obs.txt'
    content = sim_obs_file.read_text()
    assert 'Well Name\tDate\tSimulated\tObserved' in content

    # Check rmse_all file format
    rmse_all_file = tmp_path / 'gwhyd_rmse_all.txt'
    content = rmse_all_file.read_text()
    assert 'Filename\tRMSE\tBIAS' in content


def test_calib_stats_handles_multiple_wells(tmp_path):
    '''Test that calib_stats handles multiple wells correctly.'''
    from iwfm.calib.calib_stats import calib_stats

    pest_smp_file = tmp_path / 'test.smp'
    gwhyd_info_file = tmp_path / 'gwhyd.dat'
    gwhyd_file = tmp_path / 'gwhyd.out'

    # Multiple wells with multiple observations
    smp_content = [
        'WELL001  01/01/2020  12:00:00  100.5',
        'WELL001  01/02/2020  12:00:00  101.2',
        'WELL002  01/01/2020  12:00:00  200.3',
        'WELL002  01/02/2020  12:00:00  201.5',
    ]
    pest_smp_file.write_text('\n'.join(smp_content))
    gwhyd_info_file.write_text('dummy')
    gwhyd_file.write_text('dummy')

    mock_simhyd = np.array([
        [datetime(2020, 1, 1), 100.0, 200.0],
        [datetime(2020, 1, 2), 101.0, 201.0],
    ])

    # Mock gw_hyd_dict with proper structure: WellInfo instances
    mock_gw_hyd_dict = {
        'WELL001': WellInfo(column=1, x=100.5, y=200.3, layer=1, name='well001'),
        'WELL002': WellInfo(column=2, x=150.7, y=250.9, layer=2, name='well002'),
    }

    with patch('iwfm.safe_parse_date', side_effect=lambda d, _: datetime.strptime(d.split()[0], '%m/%d/%Y')):
        with patch('iwfm.read_hyd_dict', return_value=mock_gw_hyd_dict):
            with patch('iwfm.calib.sim_equiv', return_value=100.5):
                with patch('iwfm.calib.rmse_calc', return_value=1.5):
                    with patch('iwfm.calib.bias_calc', return_value=0.5):
                        with patch('iwfm.calib.calib_stats.read_sim_hyd', return_value=mock_simhyd):
                            calib_stats(str(pest_smp_file), str(gwhyd_info_file), str(gwhyd_file))

    # Verify all output files exist
    assert (tmp_path / 'gwhyd_sim_obs.txt').exists()
    assert (tmp_path / 'gwhyd_rmse.txt').exists()
    assert (tmp_path / 'gwhyd_rmse_all.txt').exists()

    # Verify sim_obs file contains data for both wells
    sim_obs_content = (tmp_path / 'gwhyd_sim_obs.txt').read_text()
    assert 'WELL001' in sim_obs_content
    assert 'WELL002' in sim_obs_content
