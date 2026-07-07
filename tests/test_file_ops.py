# test_file_ops.py
# unit test for file operations in the iwfm package
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
from pathlib import Path

import pytest

import iwfm


def test_file_test_existing(tmp_path):
    p = tmp_path / "exists.txt"
    p.write_text("hello")
    # Should not raise
    iwfm.file_test(str(p))


def test_file_test_missing_raises_file_not_found(tmp_path):
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        iwfm.file_test(str(missing))


def test_file_missing_raises_with_message(tmp_path):
    target = tmp_path / "nope.txt"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        iwfm.file_missing(str(target))


def test_file_delete_removes_file(tmp_path):
    p = tmp_path / "todelete.txt"
    p.write_text("x")
    assert p.exists()
    iwfm.file_delete(str(p))
    assert not p.exists()


def test_file_delete_missing_is_noop(tmp_path):
    p = tmp_path / "already_gone.txt"
    assert not p.exists()
    # Should not raise
    iwfm.file_delete(str(p))


def test_file_rename_basic(tmp_path):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("data")
    iwfm.file_rename(str(src), str(dst))
    assert not src.exists()
    assert dst.read_text() == "data"


def test_file_rename_dest_exists_without_force_exits(tmp_path, capsys):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("s")
    dst.write_text("d")
    with pytest.raises(FileExistsError, match="destination already exists"):
        iwfm.file_rename(str(src), str(dst), force=0)
    # Ensure nothing changed
    assert src.read_text() == "s"
    assert dst.read_text() == "d"


def test_file_rename_dest_exists_with_force_overwrites(tmp_path):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("s")
    dst.write_text("d")
    iwfm.file_rename(str(src), str(dst), force=1)
    assert not src.exists()
    assert dst.read_text() == "s"


def test_file_2_bak_creates_backup(tmp_path):
    src = tmp_path / "file.txt"
    src.write_text("payload")
    iwfm.file_2_bak(str(src))
    bak = tmp_path / "file.bak"
    assert bak.exists()
    assert not src.exists()
    assert bak.read_text() == "payload"


def test_file_type_error_raises_with_message():
    with pytest.raises(ValueError, match="must be a ABC file"):
        iwfm.file_type_error("file.xyz", "ABC")


def test_file_validate_path_creates_parent_dirs(tmp_path):
    out = tmp_path / "nested" / "path" / "out.txt"
    iwfm.file_validate_path(str(out))
    assert (tmp_path / "nested" / "path").exists()
    # Path may or may not exist yet as a file; ensure no exit occurred and directory exists


def test_file_validate_path_exits_when_target_is_directory(tmp_path, monkeypatch):
    # Create a directory where a file is expected
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    # The function should raise when output path exists but is not a file
    with pytest.raises(ValueError):
        iwfm.file_validate_path(str(target_dir))


