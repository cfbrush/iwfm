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


def file_validate_path(output_file):
    """Validate output file path and create parent directories if needed.

    Parameters
    ----------
    output_file : str
        Path to the output file

    Raises
    ------
    SystemExit
        On any error (the inner ``ValueError`` and any OS-level exception
        from ``Path.mkdir`` are caught and reported to stdout, then
        ``sys.exit()`` is called). To get a recoverable signal instead,
        validate the path yourself.
    ValueError
        Documented for symmetry — the function raises ``ValueError`` on
        the "path exists but is not a file" case, but the broad
        ``except Exception`` catches it and converts to ``SystemExit``.
    """
    import sys
    from pathlib import Path

    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist
        if output_path.exists():
            if not output_path.is_file():
                raise ValueError(f"Output path {output_file} exists but is not a file")
    except Exception as e:
        print('  *****************************************************************')
        print('  * ')
        print(f'  *   Error validating output path: {e}.')
        print('  *   Quitting.')
        print('  * ')
        print('  *****************************************************************')
        sys.exit()
