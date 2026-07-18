# file_validate_path.py
# Validate file path and that file is writable
# Copyright (C) 2020-2024 University of California
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


'''Validate file path and that file is writable.'''

def file_validate_path(output_file):
    """Validate output file path and create parent directories if needed.

    Parameters
    ----------
    output_file : str
        Path to the output file

    Raises
    ------
    ValueError
        If the path exists but is not a file.
    OSError
        If the parent directories cannot be created.
    """
    from pathlib import Path

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist
    if output_path.exists():
        if not output_path.is_file():
            raise ValueError(f"Output path {output_file} exists but is not a file")
