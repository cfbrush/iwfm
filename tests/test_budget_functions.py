# test_budget_functions.py
# unit tests for budget processing utility functions in the iwfm package
# Copyright (C) 2025 University of California
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


class TestBudgetInfo:
    """Test the budget_info function."""
    
    def test_budget_info_basic_structure(self):
        """Test basic budget info parsing."""
        # Create mock budget file content
        budget_lines = [
            "C Header line 1",
            "C Header line 2", 
            "C Header line 3",
            "1/1/2020_24:00       100.0     200.0     300.0",
            "2/1/2020_24:00       150.0     250.0     350.0",
            "3/1/2020_24:00       175.0     275.0     375.0",
            "",
            "Footer line 1",
            "Footer line 2"
        ]
        
        try:
            tables, header, footer = iwfm.budget_info(budget_lines)
            
            # Check that function returns reasonable values
            assert isinstance(tables, int)
            assert isinstance(header, int) 
            assert isinstance(footer, int)
            
            # Header should be 3 (3 comment lines)
            assert header == 3
            
            # Validate that returned values are sensible
            assert tables >= 1
            assert header >= 0
            assert footer >= 0
            
        except Exception as e:
            # If there are still issues, fail the test with details
            pytest.fail(f"budget_info function failed: {e}")
    
    def test_budget_info_empty_lines_handling(self):
        """Test that budget_info handles empty lines correctly."""
        budget_lines = [
            "C Header",
            "",  # Empty line in header
            "C Another header",
            "1/1/2020_24:00       100.0",
            "",  # Empty line in data section
            "Footer line"
        ]
        
        try:
            tables, header, footer = iwfm.budget_info(budget_lines)
            
            # Should not crash and return reasonable values
            assert isinstance(tables, int)
            assert isinstance(header, int)
            assert isinstance(footer, int)
            assert tables >= 1
            
        except Exception as e:
            pytest.fail(f"budget_info failed with empty lines: {e}")
    
    def test_budget_info_minimal_input(self):
        """Test budget_info with minimal valid input."""
        budget_lines = [
            "C Header",
            "1/1/2020_24:00       100.0"
        ]
        
        try:
            tables, header, footer = iwfm.budget_info(budget_lines)
            
            # Should handle minimal input
            assert isinstance(tables, int)
            assert isinstance(header, int)
            assert isinstance(footer, int)
            assert header == 1  # One header line
            
        except Exception as e:
            pytest.fail(f"budget_info failed with minimal input: {e}")


class TestBud2Csv:
    """Test the bud2csv function (limited testing due to complexity)."""
    
    def test_bud2csv_function_exists(self):
        """Test that bud2csv function exists and can be called."""
        # This is a minimal test just to verify the function exists
        assert hasattr(iwfm, 'bud2csv')
        assert callable(getattr(iwfm, 'bud2csv'))


class TestBuds2Xl:
    """Test the buds2xl function (limited testing due to complexity)."""

    def test_buds2xl_function_exists(self):
        """Test that buds2xl function exists and can be called."""
        from iwfm.xls.buds2xl import buds2xl
        assert callable(buds2xl)
    
    def test_buds2xl_with_mock_file(self):
        """Test buds2xl with a mock budget file."""
        # Create a temporary mock budget file in the correct format
        # Based on iwfm_read_bud.py expectations
        budget_content = """C IWFM Budget.in file
C This is a test budget file
C Factor for length units conversion
1.0
C Length units
FEET
C Factor for area units conversion  
1.0
C Area units
ACRES
C Factor for volume units conversion
1.0
C Volume units
AF
C Cache factor
1.0
C Begin date
10/01/2010
C End date  
09/30/2015
C Number of budgets to process
1
C HDF5 file name
test_budget.hdf5
C Output file name
test_output.bud
C Print interval
1
C Number of locations to print
0
C Location print list
0
"""
        
        fd, temp_file = tempfile.mkstemp(suffix='.in', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(budget_content)
            
            # Test that the function can at least parse the budget file properly
            # First test the underlying iwfm_read_bud function which should work
            try:
                budget_list, factors = iwfm.iwfm_read_bud(temp_file, verbose=False)
                
                # Validate that iwfm_read_bud parsed the file correctly
                assert isinstance(budget_list, list)
                assert isinstance(factors, list)
                assert len(factors) == 9  # Should have 9 factors
                assert len(budget_list) == 1  # Should have 1 budget entry
                
                # Check specific values from our mock file
                nbudget, factlou, unutlou, factarou, unitarou, factvolou, unitvolou, bdt, edt = factors
                assert nbudget == 1
                assert factlou == 1.0
                assert unutlou == "FEET"
                assert factarou == 1.0
                assert unitarou == "ACRES"
                assert factvolou == 1.0
                assert unitvolou == "AF"
                assert bdt == "10/01/2010"
                assert edt == "09/30/2015"
                
                # Check budget list entry
                hdffile, outfile, intprnt, nlprint, lprint = budget_list[0]
                assert hdffile == "test_budget.hdf5"
                assert outfile == "test_output.bud"
                assert intprnt == "1"
                assert nlprint == "0"
                assert lprint == "0"
                
            except Exception as e:
                pytest.fail(f"iwfm_read_bud failed to parse mock budget file: {e}")
            
            # Now test the full buds2xl function, which may fail due to
            # dependencies (the HDF5 file referenced in the budget file
            # doesn't exist).
            try:
                from iwfm.xls.buds2xl import buds2xl
                result = buds2xl(temp_file, verbose=False)
                # If it somehow succeeds, that's acceptable
                assert result is None

            except FileNotFoundError:
                # Expected when the HDF5 file referenced in the budget file
                # doesn't exist. This means the budget .in file was parsed
                # successfully by iwfm_read_bud.
                pass

            except (ImportError, ModuleNotFoundError) as e:
                # Expected if Excel/HDF5 dependencies are missing
                if any(dep in str(e) for dep in ["win32com", "h5py", "xlwings", "openpyxl"]):
                    # This is acceptable - the function parsed the file but can't continue
                    # due to missing dependencies. The important part is that it didn't
                    # fail on the file format parsing.
                    pass
                else:
                    pytest.fail(f"Unexpected ImportError: {e}")

            except FileNotFoundError as e:
                # Expected - the HDF5 file doesn't exist, but this means the
                # budget file was parsed successfully
                if "test_budget.hdf5" in str(e):
                    pass
                else:
                    pytest.fail(f"Unexpected FileNotFoundError: {e}")

            except Exception as e:
                # Any other exception indicates a problem with the function
                pytest.fail(f"buds2xl function failed unexpectedly: {e}")
                
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)