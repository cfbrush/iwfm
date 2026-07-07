# iwfm_read_rz_file_names.py
# Read rootzone file names from the main rootzone file
# Copyright (C) 2020-2026 University of California
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


def iwfm_read_rz_file_names(rz_file_name, verbose=False):
    """iwfm_read_rz_file_names() - Read rootzone file names from the main rootzone file.

    Parameters
    ----------
    rz_file_name : str
        Path to the main IWFM Rootzone file

    verbose : bool, default = False
        If True, print status messages

    Returns
    -------
    rz_npc_file_name : str
        Non-ponded crop file name (AGNPFL)

    rz_pc_file_name : str
        Ponded crop file name (PFL)

    rz_ur_file_name : str
        Urban file name (URBFL)

    rz_nv_file_name : str
        Native and riparian vegetation file name (NVRVFL)

    """
    from pathlib import Path

    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"  Reading rootzone file names from {rz_file_name}")

    iwfm.file_test(rz_file_name)
    with open(rz_file_name, encoding='utf-8') as f:
        rz_lines = f.read().splitlines()

    # Skip to the file names section (after RZCONV, RZITERMX, FACTCN, GWUPTK)
    # Read the four file names: AGNPFL, PFL, URBFL, NVRVFL
    rz_npc_file_name, line_index = read_next_line_value(rz_lines, -1, skip_lines=4)
    rz_pc_file_name, line_index = read_next_line_value(rz_lines, line_index)
    rz_ur_file_name, line_index = read_next_line_value(rz_lines, line_index)
    rz_nv_file_name, line_index = read_next_line_value(rz_lines, line_index)

    rz_dir = Path(rz_file_name).parent

    def _resolve(name):
        # IWFM input files often hold Windows-style paths with `\\` separators
        # even when running on POSIX, so normalize to `/` before constructing
        # the Path. Then strip a leading "RootZone/" prefix (case-insensitive)
        # since the listed files are usually siblings of the main RZ file, and
        # finally resolve relative to the RZ file's directory.
        normalized = name.replace('\\', '/')
        if normalized.lower().startswith('rootzone/'):
            normalized = normalized[len('rootzone/'):]
        candidate = Path(normalized)
        if rz_dir != Path('') and not candidate.is_absolute():
            candidate = rz_dir / candidate
        # os.path.normpath -> Path resolution: collapse '..' / '.' segments
        return str(Path(*candidate.parts))

    rz_npc_file_name = _resolve(rz_npc_file_name)
    rz_pc_file_name = _resolve(rz_pc_file_name)
    rz_ur_file_name = _resolve(rz_ur_file_name)
    rz_nv_file_name = _resolve(rz_nv_file_name)

    if verbose:
        print(f"    Non-ponded crop file: {rz_npc_file_name}")
        print(f"    Ponded crop file: {rz_pc_file_name}")
        print(f"    Urban file: {rz_ur_file_name}")
        print(f"    Native & Riparian file: {rz_nv_file_name}")

    return rz_npc_file_name, rz_pc_file_name, rz_ur_file_name, rz_nv_file_name
