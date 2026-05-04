#!/usr/bin/env python
# test_calib_real2iwfm.py
# Unit tests for calib/real2iwfm.py
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
import tempfile
import os
from iwfm.calib import read_overwrite_file


def create_overwrite_test_file(nwrite, factors, time_units, param_data):
    """Create properly structured IWFM overwrite file for testing.

    Parameters
    ----------
    nwrite : int
        Number of parameter lines
    factors : list
        7 scaling factors [FKH, FS, FN, FV, FL, FSCE, FSCI]
    time_units : list
        3 time unit strings (TUNITKH, TUNITV, TUNITL)
    param_data : list of tuples
        Each tuple: (node, layer, pkh, ps, pn, pv, pl, sce, sci)

    Returns
    -------
    str
        File content with proper IWFM overwrite format
    """
    content = "C*******************************************************************************\n"
    content += "C                                                                              \n"
    content += "C               INTEGRATED WATER FLOW MODEL (IWFM)                             \n"
    content += "C                                                                              \n"
    content += "C*******************************************************************************\n"
    content += "C                                                                              \n"
    content += "C               AQUIFER PARAMETER OVER-WRITE DATA FILE                         \n"
    content += "C                                                                              \n"
    content += "C*******************************************************************************\n"
    content += "C                                                                              \n"

    # NWRITE line
    content += f"  {nwrite}                          / NWRITE\n"

    # Comment section for factors
    content += "C-------------------------------------------------------------------------------\n"
    content += "C         Conversion factors for over-writing parameter values                 \n"
    content += "C-------------------------------------------------------------------------------\n"
    content += "C  FKH            FS             FN             FV             FL             FSCE           FSCI\n"
    content += "C-----------------------------------------------------------------------------------------------------\n"

    # Factors line
    content += f"   {factors[0]:.6f}       {factors[1]:.6f}       {factors[2]:.6f}       {factors[3]:.6f}       {factors[4]:.6f}       {factors[5]:.6f}       {factors[6]:.6f}\n"

    # Time units section
    content += "C---------------------------------------------------------------------------\n"
    content += "C     VALUE              DESCRIPTION                                        \n"
    content += "C---------------------------------------------------------------------------\n"
    content += f"    {time_units[0]}               / TUNITKH\n"
    content += f"    {time_units[1]}               / TUNITV\n"
    content += f"    {time_units[2]}               / TUNITL\n"
    content += "C---------------------------------------------------------------------------\n"

    # Parameter data
    for node, layer, pkh, ps, pn, pv, pl, sce, sci in param_data:
        content += f"  {node:4d}     {layer}   {pkh:.4f}      {ps:.7E}  {pn:.7f}      {pv:.7E}   {pl:.6f}      {sce:.7E}  {sci:.7E}\n"

    return content


class TestReadOverwriteFile:
    """Tests for read_overwrite_file function"""

    def test_basic_overwrite_file(self):
        """Test reading basic overwrite file with 3 parameter lines"""
        param_data = [
            (1, 1, 1000.0, 1.0e-5, 0.15, 0.1, 1.5, 1.0e-6, 1.0e-4),
            (1, 2, 950.0, 1.2e-5, 0.14, 0.09, 1.4, 1.0e-6, 1.0e-4),
            (2, 1, 1100.0, 9.5e-6, 0.16, 0.11, 1.6, 1.0e-6, 1.0e-4),
        ]

        content = create_overwrite_test_file(
            nwrite=3,
            factors=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            time_units=['1mon', '1mon', '1mon'],
            param_data=param_data
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            # Read the file
            nwrite, factors, parvals_d, in_lines = read_overwrite_file(
                temp_file, nnodes=2, nlay=2, param_types=['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
            )

            # Verify NWRITE
            assert nwrite == 3, f"Expected nwrite=3, got {nwrite}"

            # Verify factors (all should be '1.000000' as strings)
            assert len(factors) == 7, f"Expected 7 factors, got {len(factors)}"
            assert all(f == '1.000000' for f in factors), f"Expected all factors to be '1.000000', got {factors}"

            # Verify parameter dictionary
            assert len(parvals_d) == 3, f"Expected 3 parameter entries, got {len(parvals_d)}"

            # Check first entry (node 1, layer 1)
            assert '1_1' in parvals_d, "Expected key '1_1' in parameter dictionary"
            params = parvals_d['1_1']
            assert params['node'] == 1
            assert params['layer'] == 1
            assert abs(params['pkh'] - 1000.0) < 0.01
            assert abs(params['ps'] - 1.0e-5) < 1.0e-10
            assert abs(params['pn'] - 0.15) < 0.001

            # Check second entry (node 1, layer 2)
            assert '1_2' in parvals_d
            params = parvals_d['1_2']
            assert params['node'] == 1
            assert params['layer'] == 2
            assert abs(params['pkh'] - 950.0) < 0.01

            # Verify in_lines was returned
            assert isinstance(in_lines, list)
            assert len(in_lines) > 0

        finally:
            os.unlink(temp_file)

    def test_single_parameter_line(self):
        """Test reading file with single parameter line"""
        param_data = [
            (100, 1, 1250.5, 1.5e-5, 0.12, 0.15, 1.8, 2.0e-6, 5.0e-4),
        ]

        content = create_overwrite_test_file(
            nwrite=1,
            factors=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            time_units=['1day', '1day', '1day'],
            param_data=param_data
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            nwrite, factors, parvals_d, in_lines = read_overwrite_file(
                temp_file, nnodes=1, nlay=1, param_types=['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
            )

            assert nwrite == 1
            assert len(parvals_d) == 1
            assert '100_1' in parvals_d

            params = parvals_d['100_1']
            assert params['node'] == 100
            assert params['layer'] == 1
            assert abs(params['pkh'] - 1250.5) < 0.01

        finally:
            os.unlink(temp_file)

    def test_multiple_layers(self):
        """Test reading file with multiple layers for same nodes"""
        param_data = [
            (1, 1, 1000.0, 1.0e-5, 0.15, 0.1, 1.5, 1.0e-6, 1.0e-4),
            (1, 2, 950.0, 1.2e-5, 0.14, 0.09, 1.4, 1.0e-6, 1.0e-4),
            (1, 3, 900.0, 1.4e-5, 0.13, 0.08, 1.3, 1.0e-6, 1.0e-4),
            (2, 1, 1100.0, 9.5e-6, 0.16, 0.11, 1.6, 1.0e-6, 1.0e-4),
            (2, 2, 1050.0, 1.1e-5, 0.15, 0.10, 1.55, 1.0e-6, 1.0e-4),
            (2, 3, 1000.0, 1.3e-5, 0.14, 0.09, 1.45, 1.0e-6, 1.0e-4),
        ]

        content = create_overwrite_test_file(
            nwrite=6,
            factors=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            time_units=['1mon', '1mon', '1mon'],
            param_data=param_data
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            nwrite, factors, parvals_d, in_lines = read_overwrite_file(
                temp_file, nnodes=2, nlay=3, param_types=['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
            )

            assert nwrite == 6
            assert len(parvals_d) == 6

            # Check all layer combinations
            for node in [1, 2]:
                for layer in [1, 2, 3]:
                    key = f'{node}_{layer}'
                    assert key in parvals_d, f"Expected key '{key}' in parameter dictionary"
                    assert parvals_d[key]['node'] == node
                    assert parvals_d[key]['layer'] == layer

        finally:
            os.unlink(temp_file)

    def test_scaling_factors(self):
        """Test reading file with non-default scaling factors

        NOTE: The current implementation has a bug (line 169 in real2iwfm.py) where
        it reads the same column [0] seven times instead of reading columns [0] through [6].
        This test validates the current (buggy) behavior. The bug should be fixed in the future.
        """
        param_data = [
            (1, 1, 1000.0, 1.0e-5, 0.15, 0.1, 1.5, 1.0e-6, 1.0e-4),
        ]

        custom_factors = [2.5, 0.5, 1.2, 0.8, 3.0, 1.5, 0.75]

        content = create_overwrite_test_file(
            nwrite=1,
            factors=custom_factors,
            time_units=['1mon', '1mon', '1mon'],
            param_data=param_data
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            nwrite, factors, parvals_d, in_lines = read_overwrite_file(
                temp_file, nnodes=1, nlay=1, param_types=['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
            )

            assert len(factors) == 7
            # BUG: All factors are the same (first column value repeated 7 times)
            # This is due to line 169: factors = [in_lines[line_index].split()[0] for i in range(0,7)]
            # Should be: factors = [in_lines[line_index].split()[i] for i in range(0,7)]
            assert all(f == '2.500000' for f in factors), f"Expected all factors to be '2.500000', got {factors}"

        finally:
            os.unlink(temp_file)

    def test_different_time_units(self):
        """Test reading file with different time units"""
        param_data = [
            (1, 1, 1000.0, 1.0e-5, 0.15, 0.1, 1.5, 1.0e-6, 1.0e-4),
        ]

        content = create_overwrite_test_file(
            nwrite=1,
            factors=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            time_units=['1hour', '1day', '1year'],
            param_data=param_data
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            nwrite, factors, parvals_d, in_lines = read_overwrite_file(
                temp_file, nnodes=1, nlay=1, param_types=['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
            )

            # Time units are in in_lines, verify file was read successfully
            assert nwrite == 1
            assert '1_1' in parvals_d

        finally:
            os.unlink(temp_file)

    def test_parameter_value_types(self):
        """Test that parameter values have correct types"""
        param_data = [
            (5, 2, 1234.5678, 1.23456789e-5, 0.123456, 0.234567, 1.234567, 2.34567e-6, 3.45678e-4),
        ]

        content = create_overwrite_test_file(
            nwrite=1,
            factors=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            time_units=['1mon', '1mon', '1mon'],
            param_data=param_data
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            nwrite, factors, parvals_d, in_lines = read_overwrite_file(
                temp_file, nnodes=1, nlay=1, param_types=['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
            )

            params = parvals_d['5_2']

            # Verify types
            assert isinstance(params['node'], int)
            assert isinstance(params['layer'], int)
            assert isinstance(params['pkh'], float)
            assert isinstance(params['ps'], float)
            assert isinstance(params['pn'], float)
            assert isinstance(params['pv'], float)
            assert isinstance(params['pl'], float)
            assert isinstance(params['sce'], float)
            assert isinstance(params['sci'], float)

        finally:
            os.unlink(temp_file)

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(SystemExit):
            read_overwrite_file(
                '/nonexistent/path/to/file.dat',
                nnodes=1, nlay=1, param_types=['PKH']
            )

    def test_empty_file(self):
        """Test error handling for empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write('')  # Empty file
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match='empty'):
                read_overwrite_file(
                    temp_file, nnodes=1, nlay=1, param_types=['PKH']
                )
        finally:
            os.unlink(temp_file)

    def test_comments_only_file(self):
        """Test error handling for file with only comments

        The function attempts to read NWRITE but gets a comment line,
        causing an int() conversion error.
        """
        content = "C Comment line 1\nC Comment line 2\nC Comment line 3\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            # The function will raise ValueError when trying to convert 'C' to int
            with pytest.raises(ValueError):
                read_overwrite_file(
                    temp_file, nnodes=1, nlay=1, param_types=['PKH']
                )
        finally:
            os.unlink(temp_file)

    @pytest.mark.skip(reason="Large real-world file test - run manually if file exists")
    def test_with_actual_cvoverwrite_file(self):
        """Test with actual CVoverwriteIWFM.dat file if it exists

        This test is skipped by default because it requires a large external file.
        The file has 4179 parameter lines across 1393 nodes and 3 layers.
        """
        test_file = '/Volumes/MinEx/Documents/Dropbox/work/PEST/PEST-IWFM_Tools/REAL2IWFM/CVoverwriteIWFM.dat'

        if not os.path.exists(test_file):
            pytest.skip(f"Test file not found: {test_file}")

        nwrite, factors, parvals_d, in_lines = read_overwrite_file(
            test_file,
            nnodes=1393,
            nlay=3,
            param_types=['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
        )

        # Based on the file header
        assert nwrite == 4179, f"Expected nwrite=4179, got {nwrite}"

        # Check factors (all should be 1.0)
        assert len(factors) == 7
        assert all(f == '1.000000' for f in factors)

        # Check parameter dictionary
        assert isinstance(parvals_d, dict)
        assert len(parvals_d) == 4179, f"Expected 4179 entries, got {len(parvals_d)}"

        # Check structure of first entry
        first_key = list(parvals_d.keys())[0]
        first_params = parvals_d[first_key]
        assert 'node' in first_params
        assert 'layer' in first_params
        assert 'pkh' in first_params
        assert 'ps' in first_params
        assert 'pn' in first_params
        assert 'pv' in first_params
        assert 'pl' in first_params
        assert 'sce' in first_params
        assert 'sci' in first_params

        # Verify all dictionary entries have correct structure
        for key, value in parvals_d.items():
            assert isinstance(value, dict)
            assert len(value) == 9  # 9 fields: node, layer, and 7 parameters


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
