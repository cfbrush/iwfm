#!/usr/bin/env python
# test_sub_gw_pump_file.py
# Unit tests for sub_gw_pump_file.py
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


def create_pump_file(well_file, epump_file, prate_file, pumpout_file=''):
    """Create a pumping main file for testing.

    Parameters
    ----------
    well_file : str
        Well specification file path (empty string for none)
    epump_file : str
        Element pumping file path (empty string for none)
    prate_file : str
        Pumping rates file path (empty string for none)
    pumpout_file : str
        Pumping output file path (empty string for none)

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Pumping Main Data File")
    lines.append("C*******************************************************************************")

    # WELLFL - well specification file
    if well_file:
        lines.append(f"  {well_file}          / WELLFL")
    else:
        lines.append("                                          / WELLFL")

    # ELEMPUMPFL - element pumping file
    if epump_file:
        lines.append(f"  {epump_file}          / ELEMPUMPFL")
    else:
        lines.append("                                          / ELEMPUMPFL")

    # PUMPFL - pumping rates file
    if prate_file:
        lines.append(f"  {prate_file}          / PUMPFL")
    else:
        lines.append("                                          / PUMPFL")

    # PUMPOUTFL - output file
    if pumpout_file:
        lines.append(f"  {pumpout_file}          / PUMPOUTFL")
    else:
        lines.append("                                          / PUMPOUTFL")

    return '\n'.join(lines)


def create_well_file(nwell, well_specs):
    """Create a well specification file for testing.

    Parameters
    ----------
    nwell : int
        Number of wells
    well_specs : list of tuples
        Each tuple: (well_id, elem_id, x, y)

    Returns
    -------
    str
        File contents
    """
    lines = []
    lines.append("C IWFM Well Specification File")
    lines.append(f"     {nwell}                       / NWELL")
    # These 3 factor lines get skipped
    lines.append("     1.0                       / FACTXY")
    lines.append("     1.0                       / FACTRW")
    lines.append("     1.0                       / FACTLT")
    lines.append("C  ID  XWELL  YWELL  RWELL  PERFT  PERFB")

    # First section: well location lines (ID, X, Y, RWELL, PERFT, PERFB)
    # The code reads: id = t[0], x = t[1], y = t[2]
    for spec in well_specs:
        well_id, elem_id, x, y = spec[0], spec[1], spec[2], spec[3]
        lines.append(f"    {well_id}     {x}     {y}     1.0     100.0     200.0")

    lines.append("C  Second section: ID, ICOLWL, FRACWL, IOPTWL, TYPDSTWL, DSTWL, ICFIRIGWL, ICADJWL, ICWLMAX, FWLMAX")
    # Second section: well specification lines (same count as nwell)
    for spec in well_specs:
        well_id = spec[0]
        lines.append(f"    {well_id}     1     1.0     3     -1     0     1     0     1     1.0")

    # Add NGRP section
    lines.append("C Element Groups")
    lines.append("     0                  / NGRP")

    return '\n'.join(lines)


def create_epump_file(nsink, pump_specs):
    """Create an element pumping file for testing.

    Parameters
    ----------
    nsink : int
        Number of element pumping specifications
    pump_specs : list of tuples
        Each tuple: (elem_id, ...)

    Returns
    -------
    str
        File contents
    """
    lines = []
    lines.append("C IWFM Element Pumping Specification File")
    lines.append(f"     {nsink}                       / NSINK")
    lines.append("C  ID  ICOLSK   FRACSK   IOPTSK   ...")

    for spec in pump_specs:
        elem_id = spec[0]
        lines.append(f"    {elem_id}     1     1.0     3       0.25     0.25     0.25    0.25       -1         0       1           3")

    # Add NGRP section
    lines.append("C Element Groups")
    lines.append("     0                  / NGRP")

    return '\n'.join(lines)


class TestSubGwPumpFile:
    """Tests for sub_gw_pump_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.gw_pump_file import sub_gw_pump_file
        from shapely.geometry import Polygon

        bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

        with pytest.raises(FileNotFoundError):
            sub_gw_pump_file('nonexistent_file.dat', {}, [1, 2, 3], bounding_poly)

    def test_all_files_blank(self):
        """Test pump file with all sub-files blank"""
        content = create_pump_file('', '', '')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_pump_file(old_file, sim_files_new, [1, 2, 3], bounding_poly)

            # Verify output file was created
            assert os.path.exists(sim_files_new.pump_file)

            with open(sim_files_new.pump_file) as f:
                new_content = f.read()

            # All file references should still be blank
            assert '/ WELLFL' in new_content
            assert '/ ELEMPUMPFL' in new_content
            assert '/ PUMPFL' in new_content

    def test_with_well_file(self):
        """Test pump file with well specification file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create subdirectory structure
            gw_dir = os.path.join(tmpdir, 'Groundwater')
            os.makedirs(gw_dir, exist_ok=True)

            # Create well spec file
            well_specs = [
                (1, 1, 50.0, 50.0),  # Well 1 in element 1
                (2, 2, 25.0, 75.0),  # Well 2 in element 2
                (3, 10, 200.0, 200.0)  # Well 3 in element 10 (not in submodel)
            ]
            well_content = create_well_file(3, well_specs)
            well_path = os.path.join(gw_dir, 'wellspec.dat')
            with open(well_path, 'w') as f:
                f.write(well_content)

            # Create main pump file referencing the well file
            content = create_pump_file('Groundwater/wellspec.dat', '', '')

            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_well_file = os.path.join(tmpdir, 'new_well.dat')
            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=new_well_file,
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            # Bounding polygon includes wells at (50,50) and (25,75), but not (200,200)
            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only elements 1, 2 in submodel (not element 10)
            # Pass base_path to resolve relative file paths
            sub_gw_pump_file(old_file, sim_files_new, [1, 2], bounding_poly, base_path=Path(tmpdir))

            # Verify main pump file was created
            assert os.path.exists(sim_files_new.pump_file)

            with open(sim_files_new.pump_file) as f:
                new_content = f.read()

            # Well file reference should be updated
            assert 'new_well.dat' in new_content

    def test_with_epump_file(self):
        """Test pump file with element pumping file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create subdirectory structure
            gw_dir = os.path.join(tmpdir, 'Groundwater')
            os.makedirs(gw_dir, exist_ok=True)

            # Create element pumping file
            pump_specs = [
                (1,),  # Element 1
                (2,),  # Element 2
                (3,),  # Element 3
                (10,)  # Element 10 (not in submodel)
            ]
            epump_content = create_epump_file(4, pump_specs)
            epump_path = os.path.join(gw_dir, 'epump.dat')
            with open(epump_path, 'w') as f:
                f.write(epump_content)

            # Create main pump file referencing the epump file
            content = create_pump_file('', 'Groundwater/epump.dat', '')

            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_epump_file = os.path.join(tmpdir, 'new_epump.dat')
            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=new_epump_file,
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only elements 1, 2, 3 in submodel (not element 10)
            # Pass base_path to resolve relative file paths
            sub_gw_pump_file(old_file, sim_files_new, [1, 2, 3], bounding_poly, base_path=Path(tmpdir))

            # Verify main pump file was created
            assert os.path.exists(sim_files_new.pump_file)

            with open(sim_files_new.pump_file) as f:
                new_content = f.read()

            # Element pump file reference should be updated
            assert 'new_epump.dat' in new_content

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        content = create_pump_file('', '', '')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Should not raise an error with verbose=True
            sub_gw_pump_file(old_file, sim_files_new, [1, 2], bounding_poly, verbose=True)

            assert os.path.exists(sim_files_new.pump_file)

    def test_returns_none(self):
        """Test that function returns None"""
        content = create_pump_file('', '', '')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_pump_file(old_file, sim_files_new, [1, 2], bounding_poly)

            assert result is None

    def test_preserves_comments(self):
        """Test that header comments are preserved in output"""
        content = create_pump_file('', '', '')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_pump_file(old_file, sim_files_new, [1, 2], bounding_poly)

            with open(sim_files_new.pump_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Pumping Main Data File' in new_content

    def test_updates_prate_file_reference(self):
        """Test that pumping rates file reference is updated"""
        content = create_pump_file('', '', 'Groundwater/pumprates.dat')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_pump_file(old_file, sim_files_new, [1, 2], bounding_poly)

            with open(sim_files_new.pump_file) as f:
                new_content = f.read()

            # Pumping rates file reference should be updated
            assert 'new_prate.dat' in new_content

    def test_windows_path_handling(self):
        """Test that Windows-style backslash paths are handled"""
        # Use Windows-style path (backslash)
        content = create_pump_file('', '', 'Groundwater\\pumprates.dat')

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_pump_file(old_file, sim_files_new, [1, 2], bounding_poly)

            assert os.path.exists(sim_files_new.pump_file)

    def test_no_wells_sets_blank_reference(self):
        """Test that well file reference is set blank when no wells in submodel"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create subdirectory structure
            gw_dir = os.path.join(tmpdir, 'Groundwater')
            os.makedirs(gw_dir, exist_ok=True)

            # Create well spec file with wells outside submodel
            well_specs = [
                (1, 100, 500.0, 500.0),  # Well 1 in element 100 (outside)
                (2, 200, 600.0, 600.0),  # Well 2 in element 200 (outside)
            ]
            well_content = create_well_file(2, well_specs)
            well_path = os.path.join(gw_dir, 'wellspec.dat')
            with open(well_path, 'w') as f:
                f.write(well_content)

            # Create main pump file
            content = create_pump_file('Groundwater/wellspec.dat', '', '')

            old_file = os.path.join(tmpdir, 'old_pump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            sim_files_new = SimulationFiles(
                pump_file=os.path.join(tmpdir, 'new_pump.dat'),
                well_file=os.path.join(tmpdir, 'new_well.dat'),
                epump_file=os.path.join(tmpdir, 'new_epump.dat'),
                prate_file=os.path.join(tmpdir, 'new_prate.dat')
            )

            from iwfm.sub.gw_pump_file import sub_gw_pump_file
            from shapely.geometry import Polygon

            # Small bounding polygon that excludes all wells
            bounding_poly = Polygon([(0, 0), (50, 0), (50, 50), (0, 50)])

            # Elements 1, 2, 3 in submodel but wells are in elements 100, 200
            # Pass base_path to resolve relative file paths
            sub_gw_pump_file(old_file, sim_files_new, [1, 2, 3], bounding_poly, base_path=Path(tmpdir))

            with open(sim_files_new.pump_file) as f:
                new_content = f.read()

            # When no wells remain, file reference should be blank
            # The function sets blank when have_well becomes False
            lines = new_content.split('\n')
            well_line = [l for l in lines if '/ WELLFL' in l][0]
            # Should be blank (just whitespace before / WELLFL)
            assert well_line.strip().startswith('/')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
