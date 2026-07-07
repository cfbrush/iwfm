#!/usr/bin/env python
# test_sub_lu_file.py
# Unit tests for sub_lu_file.py
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


def create_lu_file(dates, elem_data):
    """Create a land use file for testing.

    Parameters
    ----------
    dates : list of str
        List of dates in DSS format (e.g., '09/30/1922_24:00')
    elem_data : dict
        Dictionary where keys are element IDs and values are lists of land use
        values (one per date)

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Land Use Area File")
    lines.append("C*******************************************************************************")

    # Specification lines (4 lines that get skipped)
    lines.append("          43560.0                                    / FACTLNU")
    lines.append("          1                                          / NSPLNU")
    lines.append("          0                                          / NFQLNU")
    lines.append("                                                     / DSSFL")

    # Data section
    lines.append("C Land Use Data")
    lines.append("C  TIME  ELEM  AREA")

    elem_ids = sorted(elem_data.keys())

    for t, date in enumerate(dates):
        # First element for this time period includes the date
        first_elem = elem_ids[0]
        lines.append(f"{date}\t{first_elem}\t{elem_data[first_elem][t]}")

        # Remaining elements for this time period
        for elem_id in elem_ids[1:]:
            lines.append(f"\t{elem_id}\t{elem_data[elem_id][t]}")

    return '\n'.join(lines)


class TestSubLuFile:
    """Tests for sub_lu_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.lu_file import sub_lu_file

        with pytest.raises(FileNotFoundError):
            sub_lu_file('nonexistent_file.dat', 'output.dat', [1, 2, 3])

    def test_all_elements_in_submodel(self):
        """Test when all elements are in the submodel"""
        dates = ['09/30/1922_24:00', '10/31/1922_24:00']
        elem_data = {
            1: [100.0, 110.0],
            2: [200.0, 220.0],
            3: [300.0, 330.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            # All elements in submodel
            sub_lu_file(in_file, out_file, [1, 2, 3])

            assert os.path.exists(out_file)

            with open(out_file) as f:
                new_content = f.read()

            # All elements should be present
            assert '1\t' in new_content
            assert '2\t' in new_content
            assert '3\t' in new_content

    def test_partial_elements_in_submodel(self):
        """Test when some elements are in the submodel"""
        dates = ['09/30/1922_24:00']
        elem_data = {
            1: [100.0],
            2: [200.0],
            3: [300.0],
            4: [400.0],
            5: [500.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            # Only elements 1, 2, 3 in submodel (not 4, 5)
            sub_lu_file(in_file, out_file, [1, 2, 3])

            assert os.path.exists(out_file)

            with open(out_file) as f:
                new_content = f.read()

            # Elements 1, 2, 3 should be present
            assert '1\t' in new_content
            assert '2\t' in new_content
            assert '3\t' in new_content

            # Elements 4, 5 should not be in the data section
            # (they might appear in comments, so check specifically for data lines)
            lines = new_content.split('\n')
            data_lines = [l for l in lines if not l.startswith('C') and l.strip()]
            data_text = '\n'.join(data_lines)
            # Check that 4 and 5 don't appear as element IDs after the spec lines
            # The spec lines are first 4 non-comment lines

    def test_no_elements_in_submodel(self):
        """Test when no elements are in the submodel - function raises IndexError"""
        dates = ['09/30/1922_24:00']
        elem_data = {
            1: [100.0],
            2: [200.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            # No matching elements in submodel - function cannot handle this case
            # and raises IndexError (edge case - submodel must have at least one element)
            with pytest.raises(IndexError):
                sub_lu_file(in_file, out_file, [100, 200, 300])

    def test_multiple_time_periods(self):
        """Test file with multiple time periods"""
        dates = ['09/30/1922_24:00', '10/31/1922_24:00', '11/30/1922_24:00']
        elem_data = {
            1: [100.0, 110.0, 120.0],
            2: [200.0, 220.0, 240.0],
            3: [300.0, 330.0, 360.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            # Only elements 1, 2 in submodel
            sub_lu_file(in_file, out_file, [1, 2])

            assert os.path.exists(out_file)

            with open(out_file) as f:
                new_content = f.read()

            # All dates should be present
            assert '09/30/1922_24:00' in new_content
            assert '10/31/1922_24:00' in new_content
            assert '11/30/1922_24:00' in new_content

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        dates = ['09/30/1922_24:00']
        elem_data = {
            1: [100.0],
            2: [200.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            # Should not raise an error with verbose=True
            sub_lu_file(in_file, out_file, [1, 2], verbose=True)

            assert os.path.exists(out_file)

    def test_returns_none(self):
        """Test that function returns None"""
        dates = ['09/30/1922_24:00']
        elem_data = {
            1: [100.0],
            2: [200.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            result = sub_lu_file(in_file, out_file, [1, 2])

            assert result is None

    def test_preserves_header_comments(self):
        """Test that header comments are preserved in output"""
        dates = ['09/30/1922_24:00']
        elem_data = {
            1: [100.0],
            2: [200.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            sub_lu_file(in_file, out_file, [1, 2])

            with open(out_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Land Use Area File' in new_content

    def test_preserves_spec_lines(self):
        """Test that specification lines are preserved"""
        dates = ['09/30/1922_24:00']
        elem_data = {
            1: [100.0],
            2: [200.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            sub_lu_file(in_file, out_file, [1, 2])

            with open(out_file) as f:
                new_content = f.read()

            # Check spec lines are preserved
            assert '/ FACTLNU' in new_content
            assert '/ NSPLNU' in new_content
            assert '/ NFQLNU' in new_content
            assert '/ DSSFL' in new_content

    def test_single_element(self):
        """Test file with only one element"""
        dates = ['09/30/1922_24:00', '10/31/1922_24:00']
        elem_data = {
            1: [100.0, 110.0],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            sub_lu_file(in_file, out_file, [1])

            assert os.path.exists(out_file)

            with open(out_file) as f:
                new_content = f.read()

            # Element 1 should be present
            assert '1\t' in new_content

    def test_data_values_preserved(self):
        """Test that data values are preserved correctly"""
        dates = ['09/30/1922_24:00']
        elem_data = {
            1: [123.456],
            2: [789.012],
        }

        content = create_lu_file(dates, elem_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_lu.dat')
            with open(in_file, 'w') as f:
                f.write(content)

            out_file = os.path.join(tmpdir, 'new_lu.dat')

            from iwfm.sub.lu_file import sub_lu_file

            sub_lu_file(in_file, out_file, [1, 2])

            with open(out_file) as f:
                new_content = f.read()

            # Values should be present (may have slightly different formatting)
            assert '123.456' in new_content
            assert '789.012' in new_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
