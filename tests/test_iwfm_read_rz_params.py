#!/usr/bin/env python
# test_iwfm_read_rz_params.py
# Unit tests for iwfm_read_rz_params.py
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


def create_rz_params_file(factk, factcp, tkunit, elements_data):
    """Create properly structured IWFM Root Zone parameters file for testing.

    IWFM File Format Convention:
    - Comment lines start with 'C', 'c', '*', or '#' in column 1
    - Data lines MUST start with whitespace (space or tab)

    Parameters
    ----------
    factk : float
        Conversion factor for root zone hydraulic conductivity
    factcp : float
        Conversion factor for capillary rise
    tkunit : str
        Time unit of root zone hydraulic conductivity (e.g., '1day')
    elements_data : list of tuples
        Each tuple: (IE, WP, FC, TN, LAMBDA, K, RHC, CPRISE, IRNE, FRNE, IMSRC, TYPDEST, DEST, PondedK)
        Note: The function reads 13 values after skipping IE

    Returns
    -------
    str
        File contents
    """
    # Header comment
    content = "C IWFM Root Zone Parameters Data File\n"

    # 4 control parameters (RZCONV, RZITERMX, FACTCN, GWUPTK)
    content += "      0.00000001                                     / RZCONV\n"
    content += "      2000                                           / RZITERMX\n"
    content += "      0.083333                                       / FACTCN\n"
    content += "      0                                              / GWUPTK\n"

    # 15 file names (some can be blank)
    content += "      file1.dat                                      / AGNPFL\n"
    content += "      file2.dat                                      / PFL\n"
    content += "      file3.dat                                      / URBFL\n"
    content += "      file4.dat                                      / NVRVFL\n"
    content += "      file5.dat                                      / RFFL\n"
    content += "      file6.dat                                      / RUFL\n"
    content += "      file7.dat                                      / IPFL\n"
    content += "                                                     / MSRCFL\n"
    content += "                                                     / AGWDFL\n"
    content += "      results1.hdf                                   / LWUBUDFL\n"
    content += "      results2.hdf                                   / RZBUDFL\n"
    content += "      results3.hdf                                   / ZLWUBUDFL\n"
    content += "      results4.hdf                                   / ZRZBUDFL\n"
    content += "      results5.out                                   / FNSMFL\n"

    # Conversion factors section
    content += "C Conversion factors\n"
    content += f"          {factk}                                        / FACTK\n"
    content += f"          {factcp}                                        / FACTCPRISE\n"
    content += f"          {tkunit}                                       / TUNITK\n"

    # Element parameters header
    content += "C Element parameters\n"

    # Element data - MUST start with whitespace (tab used here like real file)
    for elem in elements_data:
        ie, wp, fc, tn, lam, k, rhc, cprise, irne, frne, imsrc, typdest, dest, pondedk = elem
        content += f"\t{ie}\t{wp}\t{fc}\t{tn}\t{lam}\t{k}\t{rhc}\t{cprise}\t{irne}\t{frne}\t{imsrc}\t{typdest}\t{dest}\t{pondedk}\n"

    return content


class TestIwfmReadRzParams:
    """Tests for iwfm_read_rz_params function"""

    def test_single_element(self):
        """Test reading single element with default multipliers"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0.0, 1, 1.0, 0, 1, 100, 0.02)
        ]
        content = create_rz_params_file(1.0, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # Verify 13 parameter lists returned
            assert len(params) == 13

            # Each list should have 1 element
            for i in range(13):
                assert len(params[i]) == 1

            # Verify specific values (indices 0-12 correspond to WP, FC, TN, LAMBDA, K, RHC, CPRISE, IRNE, FRNE, IMSRC, TYPDEST, DEST, PondedK)
            assert params[0][0] == 0.1   # WP
            assert params[1][0] == 0.2   # FC
            assert params[2][0] == 0.3   # TN
            assert params[3][0] == 0.5   # LAMBDA
            assert params[4][0] == 0.4   # K (multiplied by factk=1.0)
            assert params[5][0] == 1.0   # RHC
            assert params[6][0] == 0.0   # CPRISE (multiplied by factcp=1.0)
            assert params[7][0] == 1.0   # IRNE
            assert params[8][0] == 1.0   # FRNE
            assert params[9][0] == 0.0   # IMSRC
            assert params[10][0] == 1.0  # TYPDEST
            assert params[11][0] == 100.0  # DEST
            assert params[12][0] == 0.02  # PondedK

        finally:
            os.unlink(temp_file)

    def test_multiple_elements(self):
        """Test reading multiple elements"""
        elements_data = [
            (1, 0.0995, 0.1934, 0.31, 0.6434, 0.4602, 1, 0, 1, 1, 0, 1, 313, 0.02915),
            (2, 0.1321, 0.2207, 0.3117, 0.4599, 0.2866, 1, 0, 2, 1, 0, 1, 316, 0.018),
            (3, 0.1399, 0.2371, 0.3235, 0.398, 0.1117, 1, 0, 3, 1, 0, 1, 317, 0.007)
        ]
        content = create_rz_params_file(1.0, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # Verify 13 parameter lists returned
            assert len(params) == 13

            # Each list should have 3 elements
            for i in range(13):
                assert len(params[i]) == 3

            # Verify WP values for all elements
            assert abs(params[0][0] - 0.0995) < 1e-6
            assert abs(params[0][1] - 0.1321) < 1e-6
            assert abs(params[0][2] - 0.1399) < 1e-6

            # Verify DEST values for all elements
            assert params[11][0] == 313.0
            assert params[11][1] == 316.0
            assert params[11][2] == 317.0

        finally:
            os.unlink(temp_file)

    def test_factk_multiplier(self):
        """Test that K values are multiplied by FACTK"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 2.0, 1, 0, 1, 1, 0, 1, 100, 0.02),
            (2, 0.1, 0.2, 0.3, 0.5, 3.0, 1, 0, 1, 1, 0, 1, 100, 0.02)
        ]
        factk = 0.5  # K should be multiplied by 0.5
        content = create_rz_params_file(factk, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # K is at index 4, should be multiplied by factk
            assert abs(params[4][0] - 1.0) < 1e-6  # 2.0 * 0.5 = 1.0
            assert abs(params[4][1] - 1.5) < 1e-6  # 3.0 * 0.5 = 1.5

        finally:
            os.unlink(temp_file)

    def test_factcp_multiplier(self):
        """Test that CPRISE values are multiplied by FACTCPRISE"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 4.0, 1, 1, 0, 1, 100, 0.02),
            (2, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 6.0, 1, 1, 0, 1, 100, 0.02)
        ]
        factcp = 2.0  # CPRISE should be multiplied by 2.0
        content = create_rz_params_file(1.0, factcp, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # CPRISE is at index 6, should be multiplied by factcp
            assert abs(params[6][0] - 8.0) < 1e-6   # 4.0 * 2.0 = 8.0
            assert abs(params[6][1] - 12.0) < 1e-6  # 6.0 * 2.0 = 12.0

        finally:
            os.unlink(temp_file)

    def test_both_multipliers(self):
        """Test that both FACTK and FACTCPRISE are applied correctly"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 10.0, 1, 5.0, 1, 1, 0, 1, 100, 0.02)
        ]
        factk = 0.1
        factcp = 0.2
        content = create_rz_params_file(factk, factcp, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # K at index 4: 10.0 * 0.1 = 1.0
            assert abs(params[4][0] - 1.0) < 1e-6

            # CPRISE at index 6: 5.0 * 0.2 = 1.0
            assert abs(params[6][0] - 1.0) < 1e-6

            # Other values should not be affected by multipliers
            assert abs(params[0][0] - 0.1) < 1e-6   # WP
            assert abs(params[3][0] - 0.5) < 1e-6   # LAMBDA

        finally:
            os.unlink(temp_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        # Create file with various comment formats interspersed
        content = "C Comment with C\n"
        content += "c Comment with lowercase c\n"
        content += "* Comment with asterisk\n"
        content += "# Comment with hash\n"
        # 4 control parameters
        content += "      0.00000001                                     / RZCONV\n"
        content += "C More comments\n"
        content += "      2000                                           / RZITERMX\n"
        content += "      0.083333                                       / FACTCN\n"
        content += "      0                                              / GWUPTK\n"
        # 14 file names
        for i in range(14):
            content += f"      file{i}.dat                                    / FILE{i}\n"
        # Conversion factors
        content += "C Conversion factors section\n"
        content += "          1.0                                        / FACTK\n"
        content += "          1.0                                        / FACTCPRISE\n"
        content += "          1day                                       / TUNITK\n"
        content += "C Element data\n"
        content += "\t1\t0.1\t0.2\t0.3\t0.5\t0.4\t1\t0\t1\t1\t0\t1\t100\t0.02\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # Verify data was read correctly despite comment lines
            assert len(params) == 13
            assert len(params[0]) == 1
            assert abs(params[0][0] - 0.1) < 1e-6  # WP

        finally:
            os.unlink(temp_file)

    def test_real_file_values(self):
        """Test with values from real C2VSimCG_RootZone.dat file"""
        # First few elements from actual file
        elements_data = [
            (1, 0.0995, 0.1934, 0.31, 0.6434, 0.4602, 1, 0, 1, 1, 0, 1, 313, 0.02915),
            (2, 0.1321, 0.2207, 0.3117, 0.4599, 0.2866, 1, 0, 2, 1, 0, 1, 316, 0.018146667),
            (3, 0.1399, 0.2371, 0.3235, 0.398, 0.1117, 1, 0, 3, 1, 0, 1, 317, 0.007075)
        ]
        content = create_rz_params_file(1.0, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # Verify specific values from real file
            assert abs(params[0][0] - 0.0995) < 1e-6   # WP element 1
            assert abs(params[1][0] - 0.1934) < 1e-6   # FC element 1
            assert abs(params[2][0] - 0.31) < 1e-6     # TN element 1
            assert abs(params[3][0] - 0.6434) < 1e-6   # LAMBDA element 1
            assert abs(params[4][0] - 0.4602) < 1e-6   # K element 1

            # Verify element 3 values
            assert abs(params[0][2] - 0.1399) < 1e-6   # WP element 3
            assert abs(params[4][2] - 0.1117) < 1e-6   # K element 3

        finally:
            os.unlink(temp_file)

    def test_different_rhc_values(self):
        """Test elements with different RHC values (Campbell vs van Genucten)"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1, 0, 1, 100, 0.02),  # RHC=1 Campbell
            (2, 0.1, 0.2, 0.3, 0.5, 0.4, 2, 0, 1, 1, 0, 1, 100, 0.02)   # RHC=2 van Genucten
        ]
        content = create_rz_params_file(1.0, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # RHC is at index 5
            assert params[5][0] == 1.0  # Campbell
            assert params[5][1] == 2.0  # van Genucten

        finally:
            os.unlink(temp_file)

    def test_different_destination_types(self):
        """Test elements with different surface flow destination types"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1, 0, 0, 0, 0.02),    # TYPDEST=0 outside model
            (2, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1, 0, 1, 100, 0.02),  # TYPDEST=1 stream node
            (3, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1, 0, 2, 50, 0.02),   # TYPDEST=2 another element
            (4, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1, 0, 3, 5, 0.02),    # TYPDEST=3 lake
            (5, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1, 0, 5, 0, 0.02)     # TYPDEST=5 groundwater
        ]
        content = create_rz_params_file(1.0, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # TYPDEST is at index 10
            assert params[10][0] == 0.0  # outside model
            assert params[10][1] == 1.0  # stream node
            assert params[10][2] == 2.0  # element
            assert params[10][3] == 3.0  # lake
            assert params[10][4] == 5.0  # groundwater

            # DEST is at index 11
            assert params[11][1] == 100.0  # stream node 100
            assert params[11][2] == 50.0   # element 50
            assert params[11][3] == 5.0    # lake 5

        finally:
            os.unlink(temp_file)

    def test_fractional_frne_values(self):
        """Test elements with fractional FRNE (rainfall factor) values"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1.0, 0, 1, 100, 0.02),
            (2, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 2, 0.8, 0, 1, 100, 0.02),
            (3, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 3, 1.2, 0, 1, 100, 0.02)
        ]
        content = create_rz_params_file(1.0, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            params = iwfm_read_rz_params(temp_file)

            # FRNE is at index 8
            assert abs(params[8][0] - 1.0) < 1e-6
            assert abs(params[8][1] - 0.8) < 1e-6
            assert abs(params[8][2] - 1.2) < 1e-6

        finally:
            os.unlink(temp_file)

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

        with pytest.raises(FileNotFoundError):
            iwfm_read_rz_params('nonexistent_file.dat')

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        elements_data = [
            (1, 0.1, 0.2, 0.3, 0.5, 0.4, 1, 0, 1, 1, 0, 1, 100, 0.02)
        ]
        content = create_rz_params_file(1.0, 1.0, '1day', elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_params import iwfm_read_rz_params

            # Should not raise an error with verbose=True
            params = iwfm_read_rz_params(temp_file, verbose=True)

            assert len(params) == 13

        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
