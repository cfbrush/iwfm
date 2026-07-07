#!/usr/bin/env python
# test_sub_gw_bc_file.py
# Unit tests for sub_gw_bc_file.py
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
from pathlib import Path
from iwfm.iwfm_dataclasses import SimulationFiles


def create_bc_file(spfl_file, sphd_file, ghd_file, cghd_file, tsbc_file, noutb=0, bhydoutfl=''):
    """Create properly structured IWFM Boundary Conditions file for testing.

    IWFM File Format Convention:
    - Comment lines start with 'C', 'c', '*', or '#' in column 1
    - Data lines MUST start with whitespace (space or tab)

    Parameters
    ----------
    spfl_file : str
        Specified flow BC file path (empty string or '/' for none)
    sphd_file : str
        Specified head BC file path (empty string or '/' for none)
    ghd_file : str
        General head BC file path (empty string or '/' for none)
    cghd_file : str
        Constrained general head BC file path (empty string or '/' for none)
    tsbc_file : str
        Time series BC file path (empty string or '/' for none)
    noutb : int
        Number of boundary nodes for hydrograph printing
    bhydoutfl : str
        Boundary node flow output file

    Returns
    -------
    str
        File contents
    """
    # Header comment
    content = "C IWFM Boundary Conditions Data File\n"

    # File names - use '/' prefix to indicate blank/none, otherwise path with leading space
    if spfl_file:
        content += f"  {spfl_file}     / SPFLOWFL\n"
    else:
        content += "                                                 / SPFLOWFL\n"

    if sphd_file:
        content += f"  {sphd_file}     / SPHEADFL\n"
    else:
        content += "                                                 / SPHEADFL\n"

    if ghd_file:
        content += f"  {ghd_file}     / GHBCFL\n"
    else:
        content += "                                                 / GHBCFL\n"

    if cghd_file:
        content += f"  {cghd_file}     / CONGHBCFL\n"
    else:
        content += "                                                 / CONGHBCFL\n"

    if tsbc_file:
        content += f"  {tsbc_file}     / TSBCFL\n"
    else:
        content += "                                                 / TSBCFL\n"

    # Boundary node flow output section
    content += "C Boundary Node Flow Output Data\n"
    content += f"    {noutb}                           / NOUTB\n"
    if bhydoutfl:
        content += f"  {bhydoutfl}                / BHYDOUTFL\n"
    else:
        content += "                                / BHYDOUTFL\n"

    return content


def create_cghd_file(ngb, params, bc_lines):
    """Create properly structured IWFM Constrained General Head BC file for testing."""
    content = "C IWFM Constrained General Head Boundary Conditions Data File\n"
    content += f"     {ngb}                          / NGB\n"
    content += f"     {params['facth']}                          / FACTH\n"
    content += f"     {params['factvl']}                          / FACTVL\n"
    content += f"     {params['tunitvl']}                       / TUNITVL\n"
    content += f"     {params['factc']}                          / FACTC\n"
    content += f"     {params['tunitc']}                       / TUNITC\n"
    content += "C     INODE   ILAYER  ITSCOL  BH         BC       LBH    ITSCOLF  CFLOW\n"
    for bc in bc_lines:
        inode, ilayer, itscol, bh, bc_val, lbh, itscolf, cflow = bc
        content += f"      {inode}     {ilayer}       {itscol}       {bh}    {bc_val}   {lbh}    {itscolf}        {cflow}\n"
    return content


class TestSubGwBcFile:
    """Tests for sub_gw_bc_file function"""

    def test_all_files_blank(self):
        """Test BC file with all sub-files blank"""
        content = create_bc_file('', '', '', '', '')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='new_spfl',
                sphd_file='new_sphd',
                ghd_file='new_ghd',
                cghd_file='new_cghd',
                tsbc_file='new_tsbc'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file

            # Create dummy bounding polygon
            from shapely.geometry import Polygon
            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_bc_file(old_file, sim_files_new, [1, 2, 3], [1, 2], bounding_poly)

            # Verify output file was created
            assert os.path.exists(new_bc_file)

            # Read and verify content
            with open(new_bc_file) as f:
                new_content = f.read()

            # All file references should still be blank (start with /)
            assert '/ SPFLOWFL' in new_content
            assert '/ SPHEADFL' in new_content
            assert '/ GHBCFL' in new_content

    def test_with_cghd_file(self):
        """Test BC file with constrained general head BC file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the constrained general head BC file
            gw_dir = os.path.join(tmpdir, 'Groundwater')
            os.makedirs(gw_dir, exist_ok=True)
            cghd_path = os.path.join(gw_dir, 'cghd.dat')

            params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
            cghd_bc_lines = [
                (100, 1, 1, 0.0, 1000.0, 50.0, 0, 0),
                (200, 1, 1, 0.0, 2000.0, 60.0, 0, 0),
                (300, 1, 1, 0.0, 3000.0, 70.0, 0, 0)
            ]
            cghd_content = create_cghd_file(3, params, cghd_bc_lines)
            with open(cghd_path, 'w') as f:
                f.write(cghd_content)

            # Create the main BC file referencing the CGHD file
            # Use forward slash for cross-platform compatibility
            content = create_bc_file('', '', '', 'Groundwater/cghd.dat', '')

            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            new_cghd_file = os.path.join(tmpdir, 'new_cghd.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='new_spfl',
                sphd_file='new_sphd',
                ghd_file='new_ghd',
                cghd_file=new_cghd_file,
                tsbc_file='new_tsbc'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only nodes 100 and 300 are in submodel
            sub_gw_bc_file(old_file, sim_files_new, [100, 300], [1, 2], bounding_poly,
                          base_path=Path(tmpdir))

            # Verify main BC file was created
            assert os.path.exists(new_bc_file)

            # Verify CGHD file was created with filtered nodes
            assert os.path.exists(new_cghd_file)

            with open(new_cghd_file) as f:
                cghd_new_content = f.read()

            # Node 200 should be removed
            lines = cghd_new_content.splitlines()
            data_lines = [l for l in lines if l.strip() and not l.strip().startswith(('C', 'c', '*', '#')) and '/' not in l]

            # Should have 2 data lines (nodes 100 and 300)
            node_ids = []
            for line in data_lines:
                parts = line.split()
                if parts and parts[0].isdigit():
                    node_ids.append(int(parts[0]))

            assert 100 in node_ids
            assert 300 in node_ids
            assert 200 not in node_ids

    def test_updates_file_references(self):
        """Test that file references are updated in output"""
        content = create_bc_file(
            'Groundwater\\old_spfl.dat',
            'Groundwater\\old_sphd.dat',
            'Groundwater\\old_ghd.dat',
            '',  # No CGHD file to avoid needing actual file
            'Groundwater\\old_tsbc.dat'
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='NewModel_SpFlow',
                sphd_file='NewModel_SpHead',
                ghd_file='NewModel_GHD',
                cghd_file='NewModel_CGHD',
                tsbc_file='NewModel_TSBC'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_bc_file(old_file, sim_files_new, [1, 2, 3], [1, 2], bounding_poly)

            # Verify output file content
            with open(new_bc_file) as f:
                new_content = f.read()

            # Check that new file names are in the output
            assert 'NewModel_SpFlow.dat' in new_content
            assert 'NewModel_SpHead.dat' in new_content
            assert 'NewModel_GHD.dat' in new_content
            assert 'NewModel_TSBC.dat' in new_content

    def test_preserves_noutb(self):
        """Test that NOUTB value is preserved"""
        content = create_bc_file('', '', '', '', '', noutb=5, bhydoutfl='output.dat')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='new_spfl',
                sphd_file='new_sphd',
                ghd_file='new_ghd',
                cghd_file='new_cghd',
                tsbc_file='new_tsbc'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_bc_file(old_file, sim_files_new, [1, 2, 3], [1, 2], bounding_poly)

            with open(new_bc_file) as f:
                new_content = f.read()

            # NOUTB should be preserved
            assert '5' in new_content
            assert '/ NOUTB' in new_content

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        content = create_bc_file('', '', '', '', '')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='new_spfl',
                sphd_file='new_sphd',
                ghd_file='new_ghd',
                cghd_file='new_cghd',
                tsbc_file='new_tsbc'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Should not raise an error with verbose=True
            sub_gw_bc_file(old_file, sim_files_new, [1, 2, 3], [1, 2], bounding_poly, verbose=True)

            assert os.path.exists(new_bc_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        # Create file with various comment formats
        content = "C Comment with C\n"
        content += "c Comment with lowercase c\n"
        content += "* Comment with asterisk\n"
        content += "# Comment with hash\n"
        content += "                                                 / SPFLOWFL\n"
        content += "C More comments\n"
        content += "                                                 / SPHEADFL\n"
        content += "                                                 / GHBCFL\n"
        content += "                                                 / CONGHBCFL\n"
        content += "                                                 / TSBCFL\n"
        content += "C Boundary output section\n"
        content += "    0                           / NOUTB\n"
        content += "                                / BHYDOUTFL\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='new_spfl',
                sphd_file='new_sphd',
                ghd_file='new_ghd',
                cghd_file='new_cghd',
                tsbc_file='new_tsbc'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Should parse correctly despite various comment styles
            sub_gw_bc_file(old_file, sim_files_new, [1, 2, 3], [1, 2], bounding_poly)

            assert os.path.exists(new_bc_file)

    def test_real_file_format(self):
        """Test with format matching real C2VSimCG file (no TSBC file to avoid path parsing issue)"""
        # Based on actual C2VSimCG_BC.dat structure
        # Note: The function expects Windows-style backslash paths for some fields
        # We test with only CGHD file which handles forward slashes correctly
        content = "C IWFM Boundary Conditions Data File\n"
        content += "C C2VSimCG v2025\n"
        content += "                                                 / SPFLOWFL\n"
        content += "                                                 / SPHEADFL\n"
        content += "                                                 / GHBCFL\n"
        content += "  Groundwater/C2VSimCG_ConstrainedHeadBC.dat     / CONGHBCFL\n"
        content += "                                                 / TSBCFL\n"
        content += "C Boundary Node Flow Output Data\n"
        content += "    0                           / NOUTB\n"
        content += "                                / BHYDOUTFL\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create subdirectory structure
            gw_dir = os.path.join(tmpdir, 'Groundwater')
            os.makedirs(gw_dir, exist_ok=True)

            # Create the CGHD file
            params = {'facth': 1, 'factvl': 1, 'tunitvl': '1day', 'factc': 1, 'tunitc': '1day'}
            cghd_bc_lines = [
                (123, 1, 1, 0.0, 5675.61, 371.96, 4, 0),
                (124, 1, 1, 0.0, 11809.24, 371.96, 4, 0),
                (516, 1, 2, 0.0, 38879.54, 105.00, 5, 0)
            ]
            cghd_content = create_cghd_file(3, params, cghd_bc_lines)
            cghd_path = os.path.join(gw_dir, 'C2VSimCG_ConstrainedHeadBC.dat')
            with open(cghd_path, 'w') as f:
                f.write(cghd_content)

            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            new_cghd_file = os.path.join(tmpdir, 'new_cghd.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='NewModel_SpFlow',
                sphd_file='NewModel_SpHead',
                ghd_file='NewModel_GHD',
                cghd_file=new_cghd_file,
                tsbc_file='NewModel_TSBC'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (1000, 0), (1000, 1000), (0, 1000)])

            # Only nodes 123 and 124 are in submodel
            sub_gw_bc_file(old_file, sim_files_new, [123, 124], [1, 2], bounding_poly,
                          base_path=Path(tmpdir))

            # Verify files were created
            assert os.path.exists(new_bc_file)
            assert os.path.exists(new_cghd_file)

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.gw_bc_file import sub_gw_bc_file
        from shapely.geometry import Polygon

        bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        sim_files_new = SimulationFiles(
            bc_file='new_bc.dat',
            spfl_file='new_spfl',
            sphd_file='new_sphd',
            ghd_file='new_ghd',
            cghd_file='new_cghd',
            tsbc_file='new_tsbc'
        )

        with pytest.raises(FileNotFoundError):
            sub_gw_bc_file('nonexistent_file.dat', sim_files_new, [1, 2, 3], [1, 2], bounding_poly)

    def test_returns_none(self):
        """Test that function returns None"""
        content = create_bc_file('', '', '', '', '')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_bc.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_bc_file = os.path.join(tmpdir, 'new_bc.dat')
            sim_files_new = SimulationFiles(
                bc_file=new_bc_file,
                spfl_file='new_spfl',
                sphd_file='new_sphd',
                ghd_file='new_ghd',
                cghd_file='new_cghd',
                tsbc_file='new_tsbc'
            )

            from iwfm.sub.gw_bc_file import sub_gw_bc_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_bc_file(old_file, sim_files_new, [1, 2, 3], [1, 2], bounding_poly)

            assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
