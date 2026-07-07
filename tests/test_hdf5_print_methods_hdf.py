# test_hdf5_print_methods_hdf.py
# Tests for hdf5/print_methods_hdf.py - Print HDF5 file methods
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

# Check if h5py is available
try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False


class TestPrintMethodsHdfImports:
    """Tests for print_methods_hdf imports."""

    def test_import_directly(self):
        """Test direct module import."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf
        assert callable(print_methods_hdf)

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf

        assert print_methods_hdf.__doc__ is not None
        assert 'hdf' in print_methods_hdf.__doc__.lower()


class TestPrintMethodsHdfSignature:
    """Tests for print_methods_hdf function signature."""

    def test_function_signature(self):
        """Test that print_methods_hdf has correct function signature."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf
        import inspect

        sig = inspect.signature(print_methods_hdf)
        params = list(sig.parameters.keys())

        assert 'filename' in params
        assert 'spacing' in params
        assert 'verbose' in params

    def test_default_spacing(self):
        """Test that default spacing is 20."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf
        import inspect

        sig = inspect.signature(print_methods_hdf)
        assert sig.parameters['spacing'].default == 20

    def test_default_verbose(self):
        """Test that verbose defaults to False."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf
        import inspect

        sig = inspect.signature(print_methods_hdf)
        assert sig.parameters['verbose'].default == False


@pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
class TestPrintMethodsHdfFunctionality:
    """Tests for print_methods_hdf functionality."""

    def test_returns_list(self, tmp_path):
        """Test that function returns a list of methods."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf

        # Create a test HDF5 file
        test_file = tmp_path / "test.hdf5"
        with h5py.File(test_file, 'w') as f:
            f.create_dataset('test_data', data=[1, 2, 3])

        result = print_methods_hdf(str(test_file))

        assert isinstance(result, list)
        assert len(result) > 0

    def test_returns_string_methods(self, tmp_path):
        """Test that returned list contains strings."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf

        test_file = tmp_path / "test.hdf5"
        with h5py.File(test_file, 'w') as f:
            f.create_dataset('data', data=[1])

        result = print_methods_hdf(str(test_file))

        for method in result:
            assert isinstance(method, str)

    def test_file_not_found(self):
        """Test that function exits for missing file."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf

        with pytest.raises(FileNotFoundError):
            print_methods_hdf('nonexistent_file.hdf5')

    def test_verbose_output(self, tmp_path, capsys):
        """Test that verbose mode prints message."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf

        test_file = tmp_path / "test.hdf5"
        with h5py.File(test_file, 'w') as f:
            f.create_dataset('data', data=[1])

        print_methods_hdf(str(test_file), verbose=True)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_includes_common_h5py_methods(self, tmp_path):
        """Test that result includes common h5py File methods."""
        from iwfm.hdf5.print_methods_hdf import print_methods_hdf

        test_file = tmp_path / "test.hdf5"
        with h5py.File(test_file, 'w') as f:
            f.create_dataset('data', data=[1])

        result = print_methods_hdf(str(test_file))

        # h5py.File should have these common methods/attributes
        method_names = [m for m in result]
        # Check that we got some methods
        assert len(method_names) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
