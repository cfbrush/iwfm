# test_hdf5_read_hdf5.py
# Tests for hdf5/read_hdf5.py - Read HDF5 files
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


class TestReadHdf5Imports:
    """Tests for read_hdf5 imports."""

    def test_import_from_hdf5(self):
        """Test import from iwfm.hdf5."""
        from iwfm.hdf5 import read_hdf5
        assert callable(read_hdf5)

    def test_import_directly(self):
        """Test direct module import."""
        from iwfm.hdf5.read_hdf5 import read_hdf5
        assert callable(read_hdf5)

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.hdf5.read_hdf5 import read_hdf5

        assert read_hdf5.__doc__ is not None
        assert 'hdf5' in read_hdf5.__doc__.lower()


class TestReadHdf5Signature:
    """Tests for read_hdf5 function signature."""

    def test_function_signature(self):
        """Test that read_hdf5 has correct function signature."""
        from iwfm.hdf5.read_hdf5 import read_hdf5
        import inspect

        sig = inspect.signature(read_hdf5)
        params = list(sig.parameters.keys())

        assert 'filename' in params
        assert 'verbose' in params

    def test_default_verbose(self):
        """Test that verbose defaults to False."""
        from iwfm.hdf5.read_hdf5 import read_hdf5
        import inspect

        sig = inspect.signature(read_hdf5)
        assert sig.parameters['verbose'].default == False


@pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
class TestReadHdf5Functionality:
    """Tests for read_hdf5 functionality."""

    def test_opens_hdf5_file(self, tmp_path):
        """Test that function opens HDF5 file."""
        from iwfm.hdf5.read_hdf5 import read_hdf5

        # Create a test HDF5 file
        test_file = tmp_path / "test.hdf5"
        with h5py.File(test_file, 'w') as f:
            f.create_dataset('test_data', data=[1, 2, 3])

        # Read the file
        result = read_hdf5(str(test_file))

        assert result is not None
        assert 'test_data' in result
        result.close()

    def test_verbose_output(self, tmp_path, capsys):
        """Test that verbose mode prints message."""
        from iwfm.hdf5.read_hdf5 import read_hdf5

        # Create a test HDF5 file
        test_file = tmp_path / "test.hdf5"
        with h5py.File(test_file, 'w') as f:
            f.create_dataset('data', data=[1])

        result = read_hdf5(str(test_file), verbose=True)
        result.close()

        captured = capsys.readouterr()
        assert 'test.hdf5' in captured.out or 'Opened' in captured.out

    def test_file_not_found(self):
        """Test that function exits for missing file."""
        from iwfm.hdf5.read_hdf5 import read_hdf5

        with pytest.raises(FileNotFoundError):
            read_hdf5('nonexistent_file.hdf5')

    def test_returns_h5py_file_object(self, tmp_path):
        """Test that function returns h5py File object."""
        from iwfm.hdf5.read_hdf5 import read_hdf5

        test_file = tmp_path / "test.hdf5"
        with h5py.File(test_file, 'w') as f:
            f.create_dataset('data', data=[1])

        result = read_hdf5(str(test_file))

        assert isinstance(result, h5py.File)
        result.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
