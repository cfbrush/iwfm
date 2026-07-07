#!/usr/bin/env python
# test_sub_gw_bc_cghd_file.py
# Unit tests for sub_gw_bc_cghd_file.py
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


def create_cghd_file(ngb, params, bc_lines):
    """Create properly structured IWFM Constrained General Head BC file for testing.

    IWFM File Format Convention:
    - Comment lines start with 'C', 'c', '*', or '#' in column 1
    - Data lines MUST start with whitespace (space or tab)

    Parameters
    ----------
    ngb : int
        Number of boundary conditions
    params : dict
        Dictionary with keys: facth, factvl, tunitvl, factc, tunitc
    bc_lines : list of tuples
        Each tuple: (inode, ilayer, itscol, bh, bc, lbh, itscolf, cflow)

    Returns
    -------
    str
        File contents
    """
    # Header comment
    content = "C IWFM Constrained General Head Boundary Conditions Data File\n"

    # NGB and parameters - data lines start with whitespace
    content += f"     {ngb}                          / NGB\n"
    content += f"     {params['facth']}                          / FACTH\n"
    content += f"     {params['factvl']}                          / FACTVL\n"
    content += f"     {params['tunitvl']}                       / TUNITVL\n"
    content += f"     {params['factc']}                          / FACTC\n"
    content += f"     {params['tunitc']}                       / TUNITC\n"

    # Boundary condition header comment
    content += "C     INODE   ILAYER  ITSCOL  BH         BC       LBH    ITSCOLF  CFLOW\n"

    # Boundary condition data lines
    for bc in bc_lines:
        inode, ilayer, itscol, bh, bc_val, lbh, itscolf, cflow = bc
        content += f"      {inode}     {ilayer}       {itscol}       {bh}    {bc_val}   {lbh}    {itscolf}        {cflow}\n"

    return content


class TestSubGwBcCghdFile:
    """Tests for sub_gw_bc_cghd_file function"""

    def test_keep_all_nodes(self):
        """Test when all nodes are in the submodel"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        bc_lines = [
            (123, 1, 1, 0.0, 5675.61, 371.96, 4, 0),
            (124, 1, 1, 0.0, 11809.24, 371.96, 4, 0),
            (134, 1, 1, 0.0, 20135.49, 371.96, 4, 0)
        ]
        content = create_cghd_file(3, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            # All nodes are in submodel
            nodes = [123, 124, 134, 200, 300]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            # All 3 boundary conditions should be kept
            assert new_ngb == 3

            # Verify output file
            with open(new_file) as f:
                new_lines = f.read().splitlines()

            # Check NGB line was updated (should still be 3)
            ngb_found = False
            for line in new_lines:
                if '/ NGB' in line:
                    assert '3' in line.split()[0]
                    ngb_found = True
                    break
            assert ngb_found

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_remove_some_nodes(self):
        """Test when some nodes are not in the submodel"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        bc_lines = [
            (123, 1, 1, 0.0, 5675.61, 371.96, 4, 0),
            (124, 1, 1, 0.0, 11809.24, 371.96, 4, 0),
            (134, 1, 1, 0.0, 20135.49, 371.96, 4, 0),
            (516, 1, 2, 0.0, 38879.54, 105.00, 5, 0),
            (550, 1, 2, 0.0, 28469.97, 105.00, 5, 0)
        ]
        content = create_cghd_file(5, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            # Only nodes 123, 134, and 550 are in submodel
            nodes = [123, 134, 550]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            # Only 3 boundary conditions should be kept
            assert new_ngb == 3

            # Verify output file
            with open(new_file) as f:
                new_content = f.read()

            # Check that kept nodes are in the file
            assert '123' in new_content
            assert '134' in new_content
            assert '550' in new_content

            # Check that removed nodes are not in the data section
            # (they might be in comments, so we check the data lines)
            new_lines = new_content.splitlines()
            data_section = False
            for line in new_lines:
                if line.strip().startswith('C') or line.strip().startswith('c'):
                    continue
                if '/ TUNITC' in line:
                    data_section = True
                    continue
                if data_section and line.strip():
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        node = int(parts[0])
                        assert node in [123, 134, 550]

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_remove_all_nodes(self):
        """Test when no nodes are in the submodel"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        bc_lines = [
            (123, 1, 1, 0.0, 5675.61, 371.96, 4, 0),
            (124, 1, 1, 0.0, 11809.24, 371.96, 4, 0)
        ]
        content = create_cghd_file(2, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            # No nodes are in submodel
            nodes = [999, 1000, 2000]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            # No boundary conditions should be kept
            assert new_ngb == 0

            # Verify output file has NGB = 0
            with open(new_file) as f:
                new_lines = f.read().splitlines()

            for line in new_lines:
                if '/ NGB' in line:
                    assert '0' in line.split()[0]
                    break

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_single_boundary_condition(self):
        """Test with single boundary condition"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        bc_lines = [
            (100, 1, 0, 50.0, 1000.0, 45.0, 0, 100.0)
        ]
        content = create_cghd_file(1, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            # Node 100 is in submodel
            nodes = [100]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            assert new_ngb == 1

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_preserves_parameters(self):
        """Test that conversion parameters are preserved in output"""
        params = {'facth': 2.5, 'factvl': 43560.0, 'tunitvl': '1month', 'factc': 43560.0, 'tunitc': '1month'}
        bc_lines = [
            (100, 1, 1, 0.0, 5000.0, 300.0, 2, 0)
        ]
        content = create_cghd_file(1, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            nodes = [100]
            sub_gw_bc_cghd_file(old_file, new_file, nodes)

            # Verify parameters are preserved
            with open(new_file) as f:
                new_content = f.read()

            assert '2.5' in new_content  # FACTH
            assert '43560.0' in new_content  # FACTVL and FACTC
            assert '1month' in new_content  # TUNITVL and TUNITC

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_multiple_layers(self):
        """Test boundary conditions across multiple layers"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        bc_lines = [
            (100, 1, 1, 0.0, 1000.0, 50.0, 0, 0),  # Layer 1
            (100, 2, 1, 0.0, 800.0, 45.0, 0, 0),   # Layer 2
            (200, 1, 2, 0.0, 1200.0, 55.0, 0, 0),  # Layer 1
            (200, 2, 2, 0.0, 900.0, 48.0, 0, 0)    # Layer 2
        ]
        content = create_cghd_file(4, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            # Only node 100 is in submodel (both layers)
            nodes = [100]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            # Both layers of node 100 should be kept
            assert new_ngb == 2

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        bc_lines = [
            (100, 1, 1, 0.0, 1000.0, 50.0, 0, 0)
        ]
        content = create_cghd_file(1, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            nodes = [100]
            # Should not raise an error with verbose=True
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes, verbose=True)

            assert new_ngb == 1

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        # Create file with various comment formats
        content = "C Comment with C\n"
        content += "c Comment with lowercase c\n"
        content += "* Comment with asterisk\n"
        content += "# Comment with hash\n"
        content += "     3                          / NGB\n"
        content += "C More comments\n"
        content += "     1                          / FACTH\n"
        content += "     1                          / FACTVL\n"
        content += "     1day                       / TUNITVL\n"
        content += "     1                          / FACTC\n"
        content += "     1day                       / TUNITC\n"
        content += "C Header comment\n"
        content += "      100     1       1       0.0    1000.0   50.0    0        0\n"
        content += "      200     1       1       0.0    1000.0   50.0    0        0\n"
        content += "      300     1       1       0.0    1000.0   50.0    0        0\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            nodes = [100, 300]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            # Only nodes 100 and 300 should be kept
            assert new_ngb == 2

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_real_file_format(self):
        """Test with format matching real C2VSimCG file"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        # Based on actual C2VSimCG_ConstrainedHeadBC.dat
        bc_lines = [
            (123, 1, 1, 0.0, 5675.61, 371.96, 4, 0),   # Black Butte Lake
            (124, 1, 1, 0.0, 11809.24, 371.96, 4, 0),  # Black Butte Lake
            (134, 1, 1, 0.0, 20135.49, 371.96, 4, 0),  # Black Butte Lake
            (516, 1, 2, 0.0, 38879.54, 105.00, 5, 0),  # Camanche
            (550, 1, 2, 0.0, 28469.97, 105.00, 5, 0),  # Camanche
            (160, 1, 3, 0.0, 9771.71, 110.63, 6, 0),   # Thermalito
            (176, 1, 3, 0.0, 24047.46, 110.63, 6, 0)   # Thermalito
        ]
        content = create_cghd_file(7, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            # Submodel includes Black Butte Lake and Thermalito nodes
            nodes = [123, 124, 134, 160, 176]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            # 5 boundary conditions should be kept (excluding Camanche nodes 516, 550)
            assert new_ngb == 5

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

        with pytest.raises(FileNotFoundError):
            sub_gw_bc_cghd_file('nonexistent_file.dat', 'output.dat', [1, 2, 3])

    def test_return_value_type(self):
        """Test that function returns an integer"""
        params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
        bc_lines = [
            (100, 1, 1, 0.0, 1000.0, 50.0, 0, 0),
            (200, 1, 1, 0.0, 1000.0, 50.0, 0, 0)
        ]
        content = create_cghd_file(2, params, bc_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            old_file = f.name

        new_file = old_file.replace('.dat', '_new.dat')

        try:
            from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file

            nodes = [100]
            new_ngb = sub_gw_bc_cghd_file(old_file, new_file, nodes)

            assert isinstance(new_ngb, int)

        finally:
            os.unlink(old_file)
            if os.path.exists(new_file):
                os.unlink(new_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
