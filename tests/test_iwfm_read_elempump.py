#!/usr/bin/env python
# test_iwfm_read_elempump.py
# Unit tests for iwfm_read_elempump.py
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


def create_elempump_file(nsink, pump_data, nlayers=3, comment_suffix=True):
    """Create IWFM Element Pumping file for testing.

    Parameters
    ----------
    nsink : int
        Number of pumping elements
    pump_data : list of tuples
        Each tuple: (elem_id, icolsk, fracsk, ioptsk, fracskl_list,
                     typdstsk, dstsk, icfirigsk, icacjsk, icskmax, fskmax)
        fracskl_list should have nlayers elements
    nlayers : int, default=3
        Number of aquifer layers
    comment_suffix : bool, default=True
        Whether to add comment suffix to data lines (like "/AgWell")

    Returns
    -------
    str
        File contents
    """
    content = "C IWFM Element Pumping File\n"
    content += "C\n"
    content += f"     {nsink}                       / NSINK\n"
    content += "C\n"
    content += "C  ID  ICOLSK   FRACSK   IOPTSK   "

    # Add layer headers
    for i in range(1, nlayers + 1):
        content += f"FRACSKL({i})  "
    content += "TYPDSTSK   DSTSK   ICFIRIGSK   ICADJSK  ICSKMAX  FSKMAX\n"
    content += "C" + "-" * 100 + "\n"

    # Add pump data
    for elem_id, icolsk, fracsk, ioptsk, fracskl_list, typdstsk, dstsk, icfirigsk, icacjsk, icskmax, fskmax in pump_data:
        # Format: ID, ICOLSK, FRACSK, IOPTSK, FRACSKL[layers], TYPDSTSK, DSTSK, ICFIRIGSK, ICACJSK, ICSKMAX, FSKMAX
        content += f"{elem_id}\t{icolsk}\t{fracsk:.3f}\t{ioptsk}\t"

        # Add layer fractions
        for frac in fracskl_list:
            content += f"{frac:.5f}\t"

        content += f"{typdstsk}\t{dstsk}\t{icfirigsk}\t{icacjsk}\t{icskmax}\t{fskmax}"

        if comment_suffix:
            content += "\t/AgWell" if icfirigsk == 1 else "\t/Urban"
        content += "\n"

    return content


class TestIwfmReadElempump:
    """Tests for iwfm_read_elempump function"""

    def test_single_ag_pump(self):
        """Test reading single agricultural pump"""
        pump_data = [
            (1, 1, 1.000, 3, [0.1, 0.3, 0.6], -1, 0, 1, 3, 0, 1)
        ]

        content = create_elempump_file(1, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify header
            assert 'active' in header
            assert 'icolsk' in header
            assert 'fracskl_1' in header
            assert 'fracskl_3' in header

            # Verify ag pump was read
            assert len(elempump_ag) == 1
            assert elempump_ag[0][0] == 1  # active
            assert elempump_ag[0][1] == 1  # icolsk
            assert elempump_ag[0][2] == 1.0  # fracsk
            assert elempump_ag[0][3] == 3  # ioptsk
            assert elempump_ag[0][10] == 0.1  # fracskl_1
            assert elempump_ag[0][11] == 0.3  # fracskl_2
            assert elempump_ag[0][12] == 0.6  # fracskl_3

            # Verify urban pump is empty (initialized)
            assert elempump_ur[0][0] == 0

        finally:
            os.unlink(temp_file)

    def test_single_urban_pump(self):
        """Test reading single urban pump (icfirigsk=2)"""
        pump_data = [
            (1, 5, 0.500, 2, [0.2, 0.5, 0.3], 0, 0, 2, 0, 0, 1)
        ]

        content = create_elempump_file(1, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify urban pump was read
            assert elempump_ur[0][0] == 1  # active
            assert elempump_ur[0][1] == 5  # icolsk
            assert elempump_ur[0][2] == 0.5  # fracsk
            assert elempump_ur[0][6] == 2  # icfirigsk (urban)

            # Verify ag pump is empty
            assert elempump_ag[0][0] == 0

        finally:
            os.unlink(temp_file)

    def test_multiple_elements_mixed_ag_urban(self):
        """Test reading multiple elements with both ag and urban pumps"""
        pump_data = [
            (1, 1, 1.000, 3, [0.1, 0.3, 0.6], -1, 0, 1, 3, 0, 1),  # Ag
            (2, 2, 1.000, 3, [0.2, 0.4, 0.4], -1, 0, 2, 0, 0, 1),  # Urban
            (3, 3, 0.750, 2, [0.3, 0.3, 0.4], 2, 5, 1, 5, 10, 0.5)  # Ag
        ]

        content = create_elempump_file(3, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1, 2, 3]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify element 1 (ag)
            assert elempump_ag[0][0] == 1  # active
            assert elempump_ag[0][6] == 1  # icfirigsk = ag

            # Verify element 2 (urban)
            assert elempump_ur[1][0] == 1  # active
            assert elempump_ur[1][6] == 2  # icfirigsk = urban

            # Verify element 3 (ag)
            assert elempump_ag[2][0] == 1  # active
            assert elempump_ag[2][2] == 0.75  # fracsk
            assert elempump_ag[2][4] == 2  # typdstsk
            assert elempump_ag[2][5] == 5  # dstsk

        finally:
            os.unlink(temp_file)

    def test_zero_fracsk_sets_inactive(self):
        """Test that fracsk=0 sets active flag to 0"""
        pump_data = [
            (1, 1, 0.000, 3, [0.1, 0.3, 0.6], -1, 0, 1, 3, 0, 1)
        ]

        content = create_elempump_file(1, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify inactive when fracsk=0
            assert elempump_ag[0][0] == 0  # active should be 0
            assert elempump_ag[0][2] == 0.0  # fracsk

        finally:
            os.unlink(temp_file)

    def test_different_layer_counts(self):
        """Test reading file with different number of layers"""
        pump_data = [
            (1, 1, 1.000, 3, [0.3, 0.3, 0.2, 0.2], -1, 0, 1, 3, 0, 1)
        ]

        content = create_elempump_file(1, pump_data, nlayers=4)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify header has 4 layer columns
            assert 'fracskl_1' in header
            assert 'fracskl_4' in header

            # Verify all 4 layer fractions
            assert elempump_ag[0][10] == 0.3  # fracskl_1
            assert elempump_ag[0][11] == 0.3  # fracskl_2
            assert elempump_ag[0][12] == 0.2  # fracskl_3
            assert elempump_ag[0][13] == 0.2  # fracskl_4

        finally:
            os.unlink(temp_file)

    def test_different_typdstsk_values(self):
        """Test different destination types"""
        pump_data = [
            (1, 1, 1.0, 3, [0.5, 0.3, 0.2], -1, 0, 1, 0, 0, 1),  # Same element
            (2, 2, 1.0, 3, [0.4, 0.4, 0.2], 0, 0, 1, 0, 0, 1),   # Outside model
            (3, 3, 1.0, 3, [0.3, 0.5, 0.2], 2, 10, 1, 0, 0, 1),  # To element 10
            (4, 4, 1.0, 3, [0.2, 0.3, 0.5], 4, 2, 1, 0, 0, 1),   # To subregion 2
        ]

        content = create_elempump_file(4, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1, 2, 3, 4]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify different typdstsk values
            assert elempump_ag[0][4] == -1  # typdstsk
            assert elempump_ag[1][4] == 0
            assert elempump_ag[2][4] == 2
            assert elempump_ag[2][5] == 10  # dstsk
            assert elempump_ag[3][4] == 4
            assert elempump_ag[3][5] == 2  # dstsk (subregion)

        finally:
            os.unlink(temp_file)

    def test_max_pumping_specification(self):
        """Test pumps with maximum pumping specifications"""
        pump_data = [
            (1, 1, 1.0, 3, [0.5, 0.3, 0.2], -1, 0, 1, 0, 5, 0.8),   # With max
            (2, 2, 1.0, 3, [0.4, 0.4, 0.2], -1, 0, 1, 0, 0, 1.0),   # No max
        ]

        content = create_elempump_file(2, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1, 2]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify max pumping values
            assert elempump_ag[0][8] == 5  # icskmax
            assert elempump_ag[0][9] == 0.8  # fskmax
            assert elempump_ag[1][8] == 0  # no max
            assert elempump_ag[1][9] == 1.0

        finally:
            os.unlink(temp_file)

    def test_supply_adjustment_column(self):
        """Test pumps with supply adjustment specifications"""
        pump_data = [
            (1, 1, 1.0, 3, [0.5, 0.3, 0.2], -1, 0, 1, 7, 0, 1),  # With adjustment
            (2, 2, 1.0, 3, [0.4, 0.4, 0.2], -1, 0, 1, 0, 0, 1),  # No adjustment
        ]

        content = create_elempump_file(2, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1, 2]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify supply adjustment values
            assert elempump_ag[0][7] == 7  # icacjsk
            assert elempump_ag[1][7] == 0  # no adjustment

        finally:
            os.unlink(temp_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        content = "C IWFM Element Pumping File\n"
        content += "c This is a comment\n"
        content += "* Another comment\n"
        content += "# Hash comment\n"
        content += "     2                       / NSINK\n"
        content += "C More comments\n"
        content += "C  ID  ICOLSK   FRACSK   IOPTSK   FRACSKL(1)  FRACSKL(2)  FRACSKL(3)  TYPDSTSK   DSTSK   ICFIRIGSK   ICADJSK  ICSKMAX  FSKMAX\n"
        content += "C" + "-" * 100 + "\n"
        content += "1\t1\t1.000\t3\t0.10000\t0.30000\t0.60000\t-1\t0\t1\t3\t0\t1\t/AgWell\n"
        content += "2\t2\t1.000\t3\t0.20000\t0.40000\t0.40000\t-1\t0\t2\t0\t0\t1\t/Urban\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1, 2]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Should read correctly despite comment lines
            assert elempump_ag[0][0] == 1  # Element 1 active (ag)
            assert elempump_ur[1][0] == 1  # Element 2 active (urban)

        finally:
            os.unlink(temp_file)

    def test_real_file_format(self):
        """Test with format matching real IWFM file"""
        pump_data = [
            (1, 1, 1.000, 3, [0.05343, 0.25546, 0.35421, 0.33693], -1, 0, 1, 3, 0, 1),
            (2, 1, 1.000, 3, [0.18193, 0.29787, 0.23113, 0.28913], -1, 0, 1, 3, 0, 1),
            (3, 1, 1.000, 3, [0.13675, 0.25838, 0.25431, 0.35044], -1, 0, 1, 3, 0, 1),
        ]

        content = create_elempump_file(3, pump_data, nlayers=4)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = [1, 2, 3]
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Verify first element
            assert elempump_ag[0][0] == 1
            assert elempump_ag[0][10] == pytest.approx(0.05343, abs=0.00001)
            assert elempump_ag[0][13] == pytest.approx(0.33693, abs=0.00001)

            # Verify all elements are ag
            assert elempump_ag[0][0] == 1
            assert elempump_ag[1][0] == 1
            assert elempump_ag[2][0] == 1

        finally:
            os.unlink(temp_file)

    def test_large_number_of_pumps(self):
        """Test reading many element pumps"""
        # Create 50 pumps - mix of ag and urban
        pump_data = []
        for i in range(1, 51):
            icfirigsk = 1 if i % 3 != 0 else 2  # Mostly ag, some urban
            pump_data.append((i, i, 1.0, 3, [0.3, 0.4, 0.3], -1, 0, icfirigsk, 0, 0, 1))

        content = create_elempump_file(50, pump_data, nlayers=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elempump import iwfm_read_elempump

            elem_ids = list(range(1, 51))
            elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(
                temp_file, elem_ids, ag=1, ur=2, comment=1, verbose=False
            )

            # Count ag and urban pumps
            ag_count = sum(1 for pump in elempump_ag if pump[0] == 1)
            ur_count = sum(1 for pump in elempump_ur if pump[0] == 1)

            # Should have about 33 ag and 17 urban (every 3rd is urban)
            assert ag_count == 34  # 50 - 16 urban pumps
            assert ur_count == 16  # Every 3rd element

        finally:
            os.unlink(temp_file)


# -----------------------------------------------------------------------------
# Error-path tests
# -----------------------------------------------------------------------------

def test_iwfm_read_elempump_missing_file_exits(tmp_path):
    """Calling with a nonexistent path bails out via iwfm.file_test() → sys.exit()."""
    import pytest
    from iwfm.iwfm_read_elempump import iwfm_read_elempump

    bogus = str(tmp_path / "does_not_exist.dat")
    with pytest.raises(SystemExit):
        iwfm_read_elempump(bogus, [1, 2, 3])


def test_iwfm_read_elempump_empty_file_raises(tmp_path):
    """An empty element-pump file should fail the parser."""
    import pytest
    from iwfm.iwfm_read_elempump import iwfm_read_elempump

    empty = tmp_path / "empty.dat"
    empty.write_text("")
    with pytest.raises((IndexError, ValueError)):
        iwfm_read_elempump(str(empty), [1, 2, 3])
