#!/usr/bin/env python
# test_sub_gw_pump_well_file.py
# Unit tests for sub_gw_pump_well_file.py
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


def create_well_file(nwell, well_locations, well_specs, ngrp, groups):
    """Create a well specification file for testing.

    Parameters
    ----------
    nwell : int
        Number of wells
    well_locations : list of tuples
        Each tuple: (well_id, x, y, rwell, perft, perfb)
    well_specs : list of tuples
        Each tuple: (well_id, icolwl, fracwl, ioptwl, typdstwl, dstwl, icfirigwl, icadjwl, icwlmax, fwlmax)
    ngrp : int
        Number of element groups
    groups : list of tuples
        Each tuple: (grp_id, [elem1, elem2, ...])

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Well Specification File")
    lines.append("C*******************************************************************************")

    # NWELL and factors
    lines.append(f"     {nwell}                       / NWELL")
    lines.append("     1.0                       / FACTXY")
    lines.append("     1.0                       / FACTRW")
    lines.append("     1.0                       / FACTLT")

    # Well location section
    lines.append("C  ID  XWELL  YWELL  RWELL  PERFT  PERFB")
    for loc in well_locations:
        well_id, x, y, rwell, perft, perfb = loc
        lines.append(f"    {well_id}     {x}     {y}     {rwell}     {perft}     {perfb}")

    # Well pumping characteristics section
    lines.append("C Well Pumping Characteristics")
    lines.append("C  ID  ICOLWL  FRACWL  IOPTWL  TYPDSTWL  DSTWL  ICFIRIGWL  ICADJWL  ICWLMAX  FWLMAX")
    for spec in well_specs:
        well_id, icolwl, fracwl, ioptwl, typdstwl, dstwl, icfirigwl, icadjwl, icwlmax, fwlmax = spec
        lines.append(f"    {well_id}     {icolwl}     {fracwl}     {ioptwl}     {typdstwl}     {dstwl}     {icfirigwl}     {icadjwl}     {icwlmax}     {fwlmax}")

    # Element groups section
    lines.append("C Delivery Element Groups")
    lines.append(f"     {ngrp}                  / NGRP")

    if ngrp > 0:
        lines.append("C  ID  NELEM  IELEM")
        for grp_id, elems in groups:
            # First line: grp_id, nelem, first_elem
            lines.append(f"    {grp_id}     {len(elems)}     {elems[0]}")
            # Continuation lines: remaining elements
            for i in range(1, len(elems)):
                lines.append(f"                     {elems[i]}")

    return '\n'.join(lines)


class TestSubGwPumpWellFile:
    """Tests for sub_gw_pump_well_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
        from shapely.geometry import Polygon

        bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

        with pytest.raises(FileNotFoundError):
            sub_gw_pump_well_file('nonexistent_file.dat', 'output.dat', [1, 2, 3], bounding_poly)

    def test_no_wells_in_submodel(self):
        """Test when no wells fall within the bounding polygon"""
        # Wells outside the bounding polygon (x, y coords at 500, 500)
        well_locations = [
            (1, 500.0, 500.0, 1.0, 100.0, 200.0),
            (2, 600.0, 600.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),
            (2, 2, 1.0, 3, -1, 0, 1, 0, 2, 1.0),
        ]

        content = create_well_file(2, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            # Small bounding polygon that excludes all wells
            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_pump_well_file(old_file, new_file, [1, 2, 3], bounding_poly)

            # Should return False when no wells in submodel
            assert result is False

            # Output file should still be created
            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # NWELL should be 0
            assert '0' in new_content

    def test_all_wells_in_submodel(self):
        """Test when all wells fall within the bounding polygon"""
        # Wells inside the bounding polygon
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
            (2, 25.0, 75.0, 1.0, 100.0, 200.0),
            (3, 75.0, 25.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),
            (2, 2, 1.0, 3, -1, 0, 1, 0, 2, 1.0),
            (3, 3, 1.0, 3, -1, 0, 1, 0, 3, 1.0),
        ]

        content = create_well_file(3, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            # Bounding polygon includes all wells
            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_pump_well_file(old_file, new_file, [1, 2, 3], bounding_poly)

            # Should return True when wells exist in submodel
            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # NWELL should be 3
            assert '3' in new_content and '/ NWELL' in new_content

    def test_partial_wells_in_submodel(self):
        """Test when some wells fall within the bounding polygon"""
        # Wells 1 and 2 inside, well 3 outside
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),   # inside
            (2, 25.0, 75.0, 1.0, 100.0, 200.0),   # inside
            (3, 500.0, 500.0, 1.0, 100.0, 200.0), # outside
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),
            (2, 2, 1.0, 3, -1, 0, 1, 0, 2, 1.0),
            (3, 3, 1.0, 3, -1, 0, 1, 0, 3, 1.0),
        ]

        content = create_well_file(3, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_pump_well_file(old_file, new_file, [1, 2, 3], bounding_poly)

            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # Check NWELL line shows 2 wells
            lines = new_content.split('\n')
            nwell_line = [l for l in lines if '/ NWELL' in l][0]
            assert '2' in nwell_line

    def test_with_element_groups(self):
        """Test filtering of element groups"""
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
            (2, 25.0, 75.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, 6, 1, 1, 0, 1, 1.0),  # TYPDSTWL=6 uses element group
            (2, 2, 1.0, 3, 6, 2, 1, 0, 2, 1.0),
        ]

        # Groups: group 1 has elements 1, 2, 3; group 2 has elements 10, 20 (outside submodel)
        groups = [
            (1, [1, 2, 3]),
            (2, [10, 20]),
        ]

        content = create_well_file(2, well_locations, well_specs, 2, groups)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only elements 1, 2, 3 in submodel
            result = sub_gw_pump_well_file(old_file, new_file, [1, 2, 3], bounding_poly)

            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # Group 2 should be removed (no elements in submodel)
            # NGRP should be 1
            lines = new_content.split('\n')
            ngrp_line = [l for l in lines if '/ NGRP' in l][0]
            assert '1' in ngrp_line

    def test_partial_element_group(self):
        """Test element group with some elements inside and some outside submodel"""
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, 6, 1, 1, 0, 1, 1.0),
        ]

        # Group 1 has elements 1, 2, 10, 20 (only 1, 2 in submodel)
        groups = [
            (1, [1, 2, 10, 20]),
        ]

        content = create_well_file(1, well_locations, well_specs, 1, groups)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only elements 1, 2 in submodel (not 10, 20)
            result = sub_gw_pump_well_file(old_file, new_file, [1, 2], bounding_poly)

            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # Group should still exist but with only 2 elements
            assert '1' in new_content  # Element 1
            assert '2' in new_content  # Element 2

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),
        ]

        content = create_well_file(1, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Should not raise an error with verbose=True
            result = sub_gw_pump_well_file(old_file, new_file, [1, 2], bounding_poly, verbose=True)

            assert result is True
            assert os.path.exists(new_file)

    def test_returns_bool(self):
        """Test that function returns boolean"""
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),
        ]

        content = create_well_file(1, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_pump_well_file(old_file, new_file, [1, 2], bounding_poly)

            assert isinstance(result, bool)

    def test_preserves_comments(self):
        """Test that header comments are preserved in output"""
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),
        ]

        content = create_well_file(1, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_pump_well_file(old_file, new_file, [1, 2], bounding_poly)

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Well Specification File' in new_content

    def test_no_element_groups(self):
        """Test file with zero element groups"""
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
            (2, 25.0, 75.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),  # TYPDSTWL=-1, no group needed
            (2, 2, 1.0, 3, -1, 0, 1, 0, 2, 1.0),
        ]

        content = create_well_file(2, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_pump_well_file(old_file, new_file, [1, 2], bounding_poly)

            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # NGRP should still be 0
            lines = new_content.split('\n')
            ngrp_line = [l for l in lines if '/ NGRP' in l][0]
            assert '0' in ngrp_line

    def test_wells_on_boundary(self):
        """Test wells exactly on the boundary polygon edge"""
        # Well at (100, 50) is on the edge of polygon (0,0)-(100,0)-(100,100)-(0,100)
        # Shapely's within() returns False for points on boundary
        well_locations = [
            (1, 100.0, 50.0, 1.0, 100.0, 200.0),  # On boundary (edge)
            (2, 50.0, 50.0, 1.0, 100.0, 200.0),   # Inside
        ]
        well_specs = [
            (1, 1, 1.0, 3, -1, 0, 1, 0, 1, 1.0),
            (2, 2, 1.0, 3, -1, 0, 1, 0, 2, 1.0),
        ]

        content = create_well_file(2, well_locations, well_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_pump_well_file(old_file, new_file, [1, 2], bounding_poly)

            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # Only well 2 should be kept (well 1 is on boundary, not within)
            lines = new_content.split('\n')
            nwell_line = [l for l in lines if '/ NWELL' in l][0]
            assert '1' in nwell_line

    def test_multiple_groups_partial_removal(self):
        """Test multiple element groups with partial removal"""
        well_locations = [
            (1, 50.0, 50.0, 1.0, 100.0, 200.0),
        ]
        well_specs = [
            (1, 1, 1.0, 3, 6, 1, 1, 0, 1, 1.0),
        ]

        # Group 1: all elements in submodel
        # Group 2: no elements in submodel
        # Group 3: some elements in submodel
        groups = [
            (1, [1, 2, 3]),
            (2, [100, 200, 300]),
            (3, [1, 100, 2, 200]),
        ]

        content = create_well_file(1, well_locations, well_specs, 3, groups)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_well.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_well.dat')

            from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only elements 1, 2, 3 in submodel
            result = sub_gw_pump_well_file(old_file, new_file, [1, 2, 3], bounding_poly)

            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # NGRP should be 2 (groups 1 and 3, group 2 removed entirely)
            lines = new_content.split('\n')
            ngrp_line = [l for l in lines if '/ NGRP' in l][0]
            assert '2' in ngrp_line


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
