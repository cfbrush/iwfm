# rz_dest_file.py
# Copy the surface flow destination file and reduce to the elements in a submodel
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

'''Copy the surface flow destination file (DESTFL, rootzone v4.12+) and reduce to the elements in a submodel.'''

import re


def sub_rz_dest_file(old_filename, new_filename, elems, sub_snodes, verbose=False):
    '''Read the original surface flow destination file, keep the destination pairs of the submodel elements, and write out a new file.

    Rootzone component versions 4.12+ move surface-flow destinations out of
    the main file's element rows into this time-series file: after NDSTN /
    NSPDSTN / NFQDSTN header lines, each data row is
    ``date (TYPDEST,DEST) (TYPDEST,DEST) ...`` with one pair per element in
    element order. Pairs pointing at a stream node (TYPDEST = 1) outside
    the submodel are changed to outside-of-model (0,0).

    Parameters
    ----------
    old_filename : str
        name of existing model surface flow destination file

    new_filename : str
        name of new submodel surface flow destination file

    elems : list of ints
        list of existing model elements in submodel

    sub_snodes : list of ints
        submodel stream nodes

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered sub_rz_dest_file() with {old_filename}")

    elems = set(int(e) for e in elems)
    snodes = set(int(s) for s in sub_snodes)

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        dest_lines = f.read().splitlines()

    # NDSTN: number of elements with destination pairs
    ndstn_str, line_index = read_next_line_value(dest_lines, -1, column=0)
    ndstn = int(ndstn_str)
    dest_lines[line_index] = ('      ' + str(len(elems))).ljust(45) + '/ NDSTN'

    # skip NSPDSTN and NFQDSTN
    _, line_index = read_next_line_value(dest_lines, line_index, column=0, skip_lines=1)

    # data rows: date followed by one (TYPDEST,DEST) pair per element
    pair_re = re.compile(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)')
    line_index += 1
    while line_index < len(dest_lines):
        line = dest_lines[line_index]
        if not line.strip() or line[0] in 'Cc*#':
            line_index += 1
            continue
        parts = line.split()
        date = parts[0]
        pairs = pair_re.findall(line)
        if len(pairs) != ndstn:
            raise ValueError(
                f'{old_filename}: expected {ndstn} destination pairs, '
                f'found {len(pairs)}'
            )
        kept = []
        for element_id, (typdest, dest) in enumerate(pairs, start=1):
            if element_id not in elems:
                continue
            typdest, dest = int(typdest), int(dest)
            if typdest == 1 and dest not in snodes:
                typdest, dest = 0, 0        # stream node left the submodel
            kept.append(f'({typdest},{dest})')
        dest_lines[line_index] = f' {date}    ' + '    '.join(kept)
        line_index += 1

    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(dest_lines) + '\n')

    if verbose:
        print(f'      Wrote surface flow destination file {new_filename}')

    return
