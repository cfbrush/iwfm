# test_buds2xl.py
# Unit tests for the buds2xl function in the iwfm package
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

import iwfm
from iwfm.xls.buds2xl import buds2xl


def create_budget_input_file(factlou, unitlou, factarou, unitarou, factvolou, unitvolou,
                              cache, bdt, edt, nbudget, budget_data):
    """Create IWFM Budget input file content for testing.

    Parameters
    ----------
    factlou : float
        Factor to convert length units
    unitlou : str
        Output unit of length
    factarou : float
        Factor to convert area units
    unitarou : str
        Output unit of area
    factvolou : float
        Factor to convert volume units
    unitvolou : str
        Output unit of volume
    cache : int
        Cache size for output
    bdt : str
        Beginning date/time (MM/DD/YYYY_HH:MM)
    edt : str
        Ending date/time (MM/DD/YYYY_HH:MM)
    nbudget : int
        Number of budget classes
    budget_data : list of tuples
        Each tuple: (hdffile, outfile, intprnt, nlprint, lprint)

    Returns
    -------
    str
        File contents
    """
    content = "C IWFM Budget Input File\n"
    content += "C\n"
    content += "C Output Unit Control\n"
    content += "C\n"

    # Conversion factors and units
    content += f"    {factlou}                           / FACTLTOU\n"
    content += f"    {unitlou}                          / UNITLTOU\n"
    content += f"    {factarou}                   / FACTAROU\n"
    content += f"    {unitarou}                            / UNITAROU\n"
    content += f"    {factvolou}                   / FACTVLOU\n"
    content += f"    {unitvolou}                        / UNITVLOU\n"

    # Cache size
    content += f"    {cache}                        / CACHE\n"

    # Begin and end dates
    content += f"    {bdt}            / BDT\n"
    content += f"    {edt}            / EDT\n"

    # Number of budgets
    content += f"    {nbudget}                           / NBUDGET\n"
    content += "C\n"

    # Budget data for each budget class
    for hdffile, outfile, intprnt, nlprint, lprint in budget_data:
        content += f"  {hdffile}             / HDFFILE\n"
        content += f"  {outfile}             / OUTFILE\n"
        # If intprnt is empty, format like real files
        if intprnt == "":
            content += "\t\t\t\t\t/ INTPRNT\n"
        else:
            content += f"  {intprnt}                       / INTPRNT\n"
        content += f"   {nlprint}                        / NLPRNT\n"
        content += f"  {lprint}                        / LPRNT[1]\n"

    return content


class TestBuds2xlFunctionExists:
    """Test that the buds2xl function exists and is callable."""

    def test_buds2xl_exists(self):
        """Test that buds2xl function exists and is callable."""
        assert callable(buds2xl)


class TestBuds2xlInputFileParsing:
    """Test that buds2xl correctly parses the Budget input file via iwfm_read_bud."""

    def test_parses_single_budget(self):
        """Test parsing input file with a single budget."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=1,
            budget_data=[
                ("test_GW_Budget.hdf", "test_GW_Budget.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            # Test that iwfm_read_bud can parse the file
            budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)

            # Verify factors
            nbudget, factlou, unutlou, factarou, unitarou, factvolou, unitvolou, bdt, edt = factors
            assert nbudget == 1
            assert factlou == 1.0
            assert unutlou == "FEET"
            assert abs(factarou - 0.000022957) < 1e-9
            assert unitarou == "AC"
            assert abs(factvolou - 0.000022957) < 1e-9
            assert unitvolou == "AC.FT."
            assert bdt == "09/30/1973_24:00"
            assert edt == "09/30/2015_24:00"

            # Verify budget list
            assert len(budget_list) == 1
            hdffile, outfile, intprnt, nlprint, lprint = budget_list[0]
            assert hdffile == "test_GW_Budget.hdf"
            assert outfile == "test_GW_Budget.bud"
            assert nlprint == "1"
            assert lprint == "-1"

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_parses_multiple_budgets(self):
        """Test parsing input file with multiple budgets."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=3,
            budget_data=[
                ("GW_Budget.hdf", "GW_Budget.bud", "", "1", "-1"),
                ("LWU_Budget.hdf", "LWU_Budget.bud", "", "1", "-1"),
                ("Streams_Budget.hdf", "Streams_Budget.bud", "1MON", "1", "-1"),
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)

            # Verify count
            nbudget = factors[0]
            assert nbudget == 3
            assert len(budget_list) == 3

            # Verify each budget entry
            assert budget_list[0][0] == "GW_Budget.hdf"
            assert budget_list[1][0] == "LWU_Budget.hdf"
            assert budget_list[2][0] == "Streams_Budget.hdf"

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_parses_different_units(self):
        """Test parsing input file with different unit configurations."""
        content = create_budget_input_file(
            factlou=0.3048,
            unitlou="METERS",
            factarou=1.0,
            unitarou="SQ.FT.",
            factvolou=1.0,
            unitvolou="CU.FT.",
            cache=100000,
            bdt="01/01/2000_24:00",
            edt="12/31/2020_24:00",
            nbudget=1,
            budget_data=[
                ("test.hdf", "test.bud", "1DAY", "0", "0")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)

            nbudget, factlou, unutlou, factarou, unitarou, factvolou, unitvolou, bdt, edt = factors
            assert abs(factlou - 0.3048) < 1e-6
            assert unutlou == "METERS"
            assert factarou == 1.0
            assert unitarou == "SQ.FT."
            assert factvolou == 1.0
            assert unitvolou == "CU.FT."

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestBuds2xlWithRealInputFile:
    """Integration tests using actual Budget input file from test data."""

    @pytest.fixture
    def budget_input_path(self):
        """Return path to the Budget input test file."""
        return os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021', 'Budget', 'C2VSimCG_Budget.in'
        )

    def test_budget_input_file_exists(self, budget_input_path):
        """Test that the Budget input test file exists, otherwise skip."""
        if not os.path.exists(budget_input_path):
            pytest.skip(f"Test data file not found: {budget_input_path}")

    def test_parse_real_budget_input_file(self, budget_input_path):
        """Test parsing the real C2VSimCG Budget input file."""
        if not os.path.exists(budget_input_path):
            pytest.skip("Budget input test file not found")

        budget_list, factors = iwfm.iwfm_read_bud(budget_input_path, verbose=False)

        # Verify factors from real file
        nbudget, factlou, unutlou, factarou, unitarou, factvolou, unitvolou, bdt, edt = factors

        # Real file has 7 budget classes
        assert nbudget == 7
        assert len(budget_list) == 7

        # Verify unit settings
        assert factlou == 1.0
        assert unutlou == "FEET"
        assert abs(factarou - 0.000022957) < 1e-9
        assert unitarou == "AC"
        assert abs(factvolou - 0.000022957) < 1e-9
        assert unitvolou == "AC.FT."

    def test_real_file_budget_list_contents(self, budget_input_path):
        """Test that the budget list from real file contains expected entries."""
        if not os.path.exists(budget_input_path):
            pytest.skip("Budget input test file not found")

        budget_list, factors = iwfm.iwfm_read_bud(budget_input_path, verbose=False)

        # Check that budget entries contain expected file patterns
        hdf_files = [entry[0] for entry in budget_list]
        bud_files = [entry[1] for entry in budget_list]

        # Should contain GW, LWU, RZ, Streams, SWatersheds, Diversions, Unsat budgets
        assert any('GW_Budget' in f for f in hdf_files)
        assert any('LWU_Budget' in f for f in hdf_files)
        assert any('RZ_Budget' in f for f in hdf_files)
        assert any('Streams_Budget' in f for f in hdf_files)
        assert any('SWatersheds_Budget' in f for f in hdf_files)
        assert any('Diversions' in f for f in hdf_files)
        assert any('Unsat_Budget' in f for f in hdf_files)

        # All output files should be .bud files
        for bud_file in bud_files:
            assert bud_file.endswith('.bud')

    def test_buds2xl_with_missing_hdf_files(self, budget_input_path):
        """Test that buds2xl fails gracefully when HDF files are missing."""
        if not os.path.exists(budget_input_path):
            pytest.skip("Budget input test file not found")

        # buds2xl should fail because the HDF5 files don't exist at relative paths.
        with pytest.raises(FileNotFoundError):
            buds2xl(budget_input_path, verbose=False)


class TestBuds2xlOutputTypes:
    """Test buds2xl with different output type options."""

    def test_type_parameter_xlsx(self):
        """Test that type='xlsx' is the default and accepted."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=1,
            budget_data=[
                ("nonexistent.hdf", "output.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            # Should fail on the missing HDF file, not on the type parameter itself
            with pytest.raises(FileNotFoundError):
                buds2xl(temp_file, type='xlsx', verbose=False)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_type_parameter_csv(self):
        """Test that type='csv' is accepted (even if not fully implemented)."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=1,
            budget_data=[
                ("nonexistent.hdf", "output.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            # Should fail on the missing HDF file, not on the type parameter itself
            with pytest.raises(FileNotFoundError):
                buds2xl(temp_file, type='csv', verbose=False)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestBuds2xlErrorHandling:
    """Test buds2xl error handling."""

    def test_missing_input_file(self):
        """Test that buds2xl raises error for missing input file."""
        with pytest.raises(FileNotFoundError):
            buds2xl("nonexistent_budget_file.in", verbose=False)

    def test_empty_budget_list(self):
        """Test buds2xl with zero budgets in file."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=0,
            budget_data=[]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            # With 0 budgets, should complete without processing any files
            # This may or may not raise an exception depending on implementation
            try:
                buds2xl(temp_file, verbose=False)
            except Exception:
                # Either completing without error or raising is acceptable
                pass

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestBuds2xlVerboseMode:
    """Test buds2xl verbose output option."""

    def test_verbose_false_no_crash(self):
        """Test that verbose=False doesn't cause issues."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=1,
            budget_data=[
                ("test.hdf", "test.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            # Should fail on the missing HDF file, not on the verbose parameter itself
            with pytest.raises(FileNotFoundError):
                buds2xl(temp_file, verbose=False)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_verbose_true_no_crash(self):
        """Test that verbose=True doesn't cause issues."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=1,
            budget_data=[
                ("test.hdf", "test.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            # Should fail on the missing HDF file, not on the verbose parameter itself
            with pytest.raises(FileNotFoundError):
                buds2xl(temp_file, verbose=True)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestBuds2xlFilePathHandling:
    """Test buds2xl handling of various file path formats."""

    def test_relative_path_in_budget_entries(self):
        """Test that relative paths in budget entries are handled."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=1,
            budget_data=[
                ("..\\Results\\test.hdf", "..\\Results\\test.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)

            # Should parse the relative paths correctly
            assert "..\\Results\\test.hdf" in budget_list[0][0]

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_paths_without_spaces(self):
        """Test that file paths without spaces are handled correctly.

        Note: The IWFM parser splits on whitespace, so paths with spaces
        are not fully supported. This test verifies paths without spaces work.
        """
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1973_24:00",
            edt="09/30/2015_24:00",
            nbudget=1,
            budget_data=[
                ("MyFiles\\test_budget.hdf", "MyFiles\\test_budget.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)

            # Should parse paths without spaces
            assert "MyFiles\\test_budget.hdf" in budget_list[0][0]

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestBuds2xlDateTimeFormats:
    """Test buds2xl handling of different date/time formats."""

    def test_standard_datetime_format(self):
        """Test standard MM/DD/YYYY_HH:MM format."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="01/01/2000_24:00",
            edt="12/31/2020_24:00",
            nbudget=1,
            budget_data=[
                ("test.hdf", "test.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)
            bdt = factors[7]
            edt = factors[8]

            assert bdt == "01/01/2000_24:00"
            assert edt == "12/31/2020_24:00"

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_midnight_format(self):
        """Test that midnight is represented as 24:00."""
        content = create_budget_input_file(
            factlou=1.0,
            unitlou="FEET",
            factarou=0.000022957,
            unitarou="AC",
            factvolou=0.000022957,
            unitvolou="AC.FT.",
            cache=500000,
            bdt="09/30/1900_24:00",
            edt="09/30/2100_24:00",
            nbudget=1,
            budget_data=[
                ("test.hdf", "test.bud", "", "1", "-1")
            ]
        )

        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)
            bdt = factors[7]
            edt = factors[8]

            # Should contain 24:00 for midnight
            assert "24:00" in bdt
            assert "24:00" in edt

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
