# test_dbf_open.py
# Unit tests for the dbf_open function in the iwfm package
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
import os
import tempfile
import struct
import datetime

import iwfm


def create_test_dbf_file(filepath, records):
    """Create a minimal DBF file for testing.

    Parameters
    ----------
    filepath : str
        Path to write the DBF file
    records : list of dict
        Records to write, each dict has 'ID' (int) and 'NAME' (str, max 20 chars)
    """
    # DBF file format (dBASE III)
    # Header: 32 bytes
    # Field descriptors: 32 bytes each + 1 byte terminator
    # Records: 1 byte delete flag + field data

    num_records = len(records)
    num_fields = 2  # ID (N, 10) and NAME (C, 20)

    # Field sizes
    id_size = 10
    name_size = 20
    record_size = 1 + id_size + name_size  # delete flag + fields

    header_size = 32 + (num_fields * 32) + 1  # header + field descriptors + terminator

    # Current date
    now = datetime.datetime.now()

    with open(filepath, 'wb') as f:
        # Header (32 bytes)
        f.write(struct.pack('<B', 0x03))  # Version (dBASE III)
        f.write(struct.pack('<B', now.year - 1900))  # Year
        f.write(struct.pack('<B', now.month))  # Month
        f.write(struct.pack('<B', now.day))  # Day
        f.write(struct.pack('<I', num_records))  # Number of records
        f.write(struct.pack('<H', header_size))  # Header size
        f.write(struct.pack('<H', record_size))  # Record size
        f.write(b'\x00' * 20)  # Reserved

        # Field descriptor for ID (32 bytes)
        f.write(b'ID' + b'\x00' * 9)  # Field name (11 bytes, null-padded)
        f.write(b'N')  # Field type (Numeric)
        f.write(b'\x00' * 4)  # Reserved
        f.write(struct.pack('<B', id_size))  # Field length
        f.write(struct.pack('<B', 0))  # Decimal count
        f.write(b'\x00' * 14)  # Reserved

        # Field descriptor for NAME (32 bytes)
        f.write(b'NAME' + b'\x00' * 7)  # Field name (11 bytes, null-padded)
        f.write(b'C')  # Field type (Character)
        f.write(b'\x00' * 4)  # Reserved
        f.write(struct.pack('<B', name_size))  # Field length
        f.write(struct.pack('<B', 0))  # Decimal count
        f.write(b'\x00' * 14)  # Reserved

        # Header terminator
        f.write(b'\x0D')

        # Records
        for rec in records:
            f.write(b' ')  # Delete flag (space = not deleted)
            # ID field (right-justified, space-padded)
            id_str = str(rec.get('ID', 0)).rjust(id_size)
            f.write(id_str.encode('ascii'))
            # NAME field (left-justified, space-padded)
            name_str = str(rec.get('NAME', '')).ljust(name_size)[:name_size]
            f.write(name_str.encode('ascii'))

        # End of file marker
        f.write(b'\x1A')


# the gate variable keeps its original name so the skipif marks
# below stay unchanged
DBFREAD_AVAILABLE = True


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfOpenFunctionExists:
    """Test that the dbf_open function exists and is callable."""

    def test_dbf_open_exists(self):
        """Test that dbf_open function exists in the iwfm module."""
        assert hasattr(iwfm, 'dbf_open')
        assert callable(getattr(iwfm, 'dbf_open'))


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfOpenBasicFunctionality:
    """Test basic functionality of dbf_open."""

    def test_open_simple_dbf(self):
        """Test opening a simple DBF file."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 1, 'NAME': 'Test1'},
                {'ID': 2, 'NAME': 'Test2'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            assert db is not None
            assert len(db) == 2
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_open_with_load_false(self):
        """Test opening DBF with load=False (default)."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Record1'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, load=False, verbose=False)

            assert db is not None
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_open_with_load_true(self):
        """Test opening DBF with load=True."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 1, 'NAME': 'Loaded1'},
                {'ID': 2, 'NAME': 'Loaded2'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, load=True, verbose=False)

            assert db is not None
            # When loaded, records are in memory
            record_list = list(db)
            assert len(record_list) == 2
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_open_empty_dbf(self):
        """Test opening a DBF file with no records."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = []
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            assert db is not None
            assert len(db) == 0
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfOpenReturnType:
    """Test the return type of dbf_open."""

    def test_returns_dbf_object(self):
        """Test that dbf_open returns a DBF object."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Test'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            # Should be a DBF object from dbfread
            assert hasattr(db, 'fields')
            assert hasattr(db, 'records')
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_db_is_iterable(self):
        """Test that returned DB object is iterable."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 1, 'NAME': 'Iter1'},
                {'ID': 2, 'NAME': 'Iter2'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            # Should be iterable
            record_list = list(db)
            assert len(record_list) == 2
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfOpenRecordAccess:
    """Test accessing records from opened DBF."""

    def test_access_record_fields(self):
        """Test accessing fields in records."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 42, 'NAME': 'Answer'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, load=True, verbose=False)
            record_list = list(db)

            assert record_list[0]['ID'] == 42
            assert record_list[0]['NAME'].strip() == 'Answer'
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_multiple_records(self):
        """Test accessing multiple records."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 1, 'NAME': 'First'},
                {'ID': 2, 'NAME': 'Second'},
                {'ID': 3, 'NAME': 'Third'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, load=True, verbose=False)
            record_list = list(db)

            assert len(record_list) == 3
            assert record_list[0]['ID'] == 1
            assert record_list[1]['ID'] == 2
            assert record_list[2]['ID'] == 3
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfOpenVerboseMode:
    """Test verbose mode of dbf_open."""

    def test_verbose_false(self):
        """Test that verbose=False produces no output."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Silent'}]
            create_test_dbf_file(temp_file, records)

            # Should not raise any errors
            db = iwfm.dbf_open(temp_file, verbose=False)

            assert db is not None
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_verbose_true(self, capsys):
        """Test that verbose=True produces output."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Verbose'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=True)

            captured = capsys.readouterr()
            assert 'Opened file' in captured.out
            assert '1' in captured.out  # Number of records
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfOpenErrorHandling:
    """Test error handling in dbf_open."""

    def test_nonexistent_file(self):
        """Test opening a file that doesn't exist."""
        with pytest.raises(Exception):
            iwfm.dbf_open('nonexistent_file.dbf', verbose=False)

    def test_invalid_dbf_file(self):
        """Test opening an invalid DBF file."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        try:
            # Write garbage data
            with os.fdopen(fd, 'wb') as f:
                f.write(b'This is not a valid DBF file')

            with pytest.raises(Exception):
                iwfm.dbf_open(temp_file, verbose=False)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfOpenFieldInfo:
    """Test field information from opened DBF."""

    def test_field_names(self):
        """Test that field names are accessible."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'FieldTest'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            field_names = [f.name for f in db.fields]
            assert 'ID' in field_names
            assert 'NAME' in field_names
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_record_count(self):
        """Test that record count is correct."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': i, 'NAME': f'Record{i}'}
                for i in range(10)
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            assert len(db) == 10
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestDbfOpenWithoutLibrary:
    """Tests that run even when dbfread is not installed."""

    def test_function_exists_in_module(self):
        """Test that dbf_open is defined in iwfm module."""
        assert hasattr(iwfm, 'dbf_open')

    @pytest.mark.skipif(DBFREAD_AVAILABLE, reason="Test only runs when dbfread is NOT installed")
    def test_import_error_without_dbfread(self):
        """Test that calling dbf_open without dbfread raises ImportError."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            # Create a minimal valid-looking file
            with open(temp_file, 'wb') as f:
                f.write(b'\x03')  # Version byte

            with pytest.raises(ImportError):
                iwfm.dbf_open(temp_file, verbose=False)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
