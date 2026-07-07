# test_dbf_print_record.py
# Unit tests for the dbf_print_record function in the iwfm package
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
class TestDbfPrintRecordFunctionExists:
    """Test that the dbf_print_record function exists and is callable."""

    def test_dbf_print_record_exists(self):
        """Test that dbf_print_record function exists in the iwfm module."""
        assert hasattr(iwfm, 'dbf_print_record')
        assert callable(getattr(iwfm, 'dbf_print_record'))


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfPrintRecordBasicFunctionality:
    """Test basic functionality of dbf_print_record."""

    def test_print_first_record(self, capsys):
        """Test printing the first record (index 0)."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 1, 'NAME': 'FirstRecord'},
                {'ID': 2, 'NAME': 'SecondRecord'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            assert 'Record 0' in captured.out
            assert '1' in captured.out  # ID value
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_print_second_record(self, capsys):
        """Test printing the second record (index 1)."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 100, 'NAME': 'First'},
                {'ID': 200, 'NAME': 'Second'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 1)

            captured = capsys.readouterr()
            assert 'Record 1' in captured.out
            assert '200' in captured.out  # ID value of second record
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_print_last_record(self, capsys):
        """Test printing the last record."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 1, 'NAME': 'First'},
                {'ID': 2, 'NAME': 'Middle'},
                {'ID': 3, 'NAME': 'Last'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 2)

            captured = capsys.readouterr()
            assert 'Record 2' in captured.out
            assert '3' in captured.out  # ID value of last record
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfPrintRecordOutputFormat:
    """Test the output format of dbf_print_record."""

    def test_output_contains_record_number(self, capsys):
        """Test that output contains the record number."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 42, 'NAME': 'TestName'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            assert 'Record 0' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_output_contains_field_values(self, capsys):
        """Test that output contains field values."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 999, 'NAME': 'SpecialName'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            assert '999' in captured.out
            assert 'SpecialName' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_output_has_newline(self, capsys):
        """Test that output has proper formatting with newlines."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Test'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            # The format is 'Record {rec}: \n{records[rec]}'
            assert '\n' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfPrintRecordMultipleRecords:
    """Test dbf_print_record with multiple records."""

    def test_print_different_records(self, capsys):
        """Test printing different records from the same database."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 10, 'NAME': 'Alpha'},
                {'ID': 20, 'NAME': 'Beta'},
                {'ID': 30, 'NAME': 'Gamma'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            # Print first record
            iwfm.dbf_print_record(db, 0)
            captured1 = capsys.readouterr()
            assert '10' in captured1.out
            assert 'Alpha' in captured1.out

            # Print third record
            iwfm.dbf_print_record(db, 2)
            captured2 = capsys.readouterr()
            assert '30' in captured2.out
            assert 'Gamma' in captured2.out

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_print_all_records_sequentially(self, capsys):
        """Test printing all records one by one."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': i, 'NAME': f'Record{i}'}
                for i in range(5)
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            for i in range(5):
                iwfm.dbf_print_record(db, i)
                captured = capsys.readouterr()
                assert f'Record {i}' in captured.out
                assert str(i) in captured.out

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfPrintRecordEdgeCases:
    """Test edge cases for dbf_print_record."""

    def test_single_record_database(self, capsys):
        """Test with database containing only one record."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'OnlyOne'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            assert 'Record 0' in captured.out
            assert 'OnlyOne' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_record_with_spaces_in_name(self, capsys):
        """Test printing record with spaces in field values."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Has Spaces Here'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            assert 'Has Spaces Here' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_record_with_special_characters(self, capsys):
        """Test printing record with special characters."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Test-Name_123'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            assert 'Test-Name_123' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_invalid_record_index(self):
        """Test printing with invalid record index."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Test'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            # Trying to access index 5 when only 1 record exists
            with pytest.raises(IndexError):
                iwfm.dbf_print_record(db, 5)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_negative_record_index(self, capsys):
        """Test printing with negative record index (Python allows this)."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 1, 'NAME': 'First'},
                {'ID': 2, 'NAME': 'Last'}
            ]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)

            # -1 should access last record in Python
            iwfm.dbf_print_record(db, -1)

            captured = capsys.readouterr()
            # The record number in output will be -1
            assert 'Record -1' in captured.out
            # But it should print the last record's data
            assert '2' in captured.out or 'Last' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfPrintRecordWithLoadedDb:
    """Test dbf_print_record with pre-loaded database."""

    def test_print_from_loaded_db(self, capsys):
        """Test printing from a database loaded into memory."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [
                {'ID': 100, 'NAME': 'Loaded1'},
                {'ID': 200, 'NAME': 'Loaded2'}
            ]
            create_test_dbf_file(temp_file, records)

            # Open with load=True to load into memory
            db = iwfm.dbf_open(temp_file, load=True, verbose=False)
            iwfm.dbf_print_record(db, 0)

            captured = capsys.readouterr()
            assert 'Record 0' in captured.out
            assert '100' in captured.out
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.skipif(not DBFREAD_AVAILABLE, reason="dbfread library not installed")
class TestDbfPrintRecordReturnValue:
    """Test return value of dbf_print_record."""

    def test_returns_none(self):
        """Test that dbf_print_record returns None."""
        fd, temp_file = tempfile.mkstemp(suffix='.dbf')
        os.close(fd)

        try:
            records = [{'ID': 1, 'NAME': 'Test'}]
            create_test_dbf_file(temp_file, records)

            db = iwfm.dbf_open(temp_file, verbose=False)
            result = iwfm.dbf_print_record(db, 0)

            assert result is None
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestDbfPrintRecordWithoutLibrary:
    """Tests that run even when dbfread is not installed."""

    def test_function_exists_in_module(self):
        """Test that dbf_print_record is defined in iwfm module."""
        assert hasattr(iwfm, 'dbf_print_record')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
