# write_overwrite_file.py
# Write IWFM Groundwater Overwrite file
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


def write_overwrite_file(overwrite_file, in_lines, parnodes, nlay, parvals, fp, ctime, verbose=False):
    '''Receive a list of parameters and write them to an IWFM-2015 overwrite file.

         From REAL2IGSM.F90 by Matt Tonkin, with modifications by others

    Parameters
    ----------
    overwrite_file : str
        Overwrite file name

    in_lines : list
        each item is one line from the existing (template) overwrite file

    parnodes : list
        Node numbers corresponding to parvals items

    nlay : int
        Number of model layers

    parvals : list
        New parameter values

    fp : list
        Multiplier factors

    ctime : str
        Time step in DSS format

    verbose : bool, default=False
        Print to screen?
    '''

    line_index = 0
    with open(overwrite_file, 'w', encoding='utf-8') as f:

        while in_lines[line_index][0] == 'C':           # write comment lines
            f.write(f'{in_lines[line_index]}\n')
            line_index += 1 

        # write number of parameter lines
        f.write(f'    {len(parnodes[0][0] * nlay)}                       / NWRITE\n')
        line_index += 1

        while in_lines[line_index][0] == 'C':           # write comment lines
            f.write(f'{in_lines[line_index]}\n')
            line_index += 1 

        # write factors
        f.write(f'\t{fp[0]}\t{fp[1]}\t{fp[2]}\t{fp[3]}\t{fp[4]}\t{fp[5]}\t{fp[6]}\n')
        line_index += 1

        while in_lines[line_index][0] == 'C':           # write comment lines
            f.write(f'{in_lines[line_index]}\n')
            line_index += 1 

        # write time units
        f.write(f'    {ctime}               / TUNITKH\n')
        line_index += 1
        for i in range(0,2):                            # write remaining DSS time units
            f.write(f'{in_lines[line_index]}\n')
            line_index += 1 

        while in_lines[line_index][0] == 'C':           # write comment lines
            f.write(f'{in_lines[line_index]}\n')
            line_index += 1 

        for n in range(0, len(parnodes[0][1])):         # cycle through nodes
            for l in range(0, nlay):                    # cycle through layers
                pkh = parvals[0][l][n] if parvals[0][l][n] > 0 else -1
                ps  = parvals[1][l][n] if parvals[1][l][n] > 0 else -1
                pn  = parvals[2][l][n] if parvals[2][l][n] > 0 else -1
                pv  = parvals[3][l][n] if parvals[3][l][n] > 0 else -1
                pl  = parvals[4][l][n] if parvals[4][l][n] > 0 else -1
                sce = parvals[5][l][n] if parvals[5][l][n] > 0 else -1
                sci = parvals[6][l][n] if parvals[6][l][n] > 0 else -1

                f.write(f'\t{parnodes[0][l][n]}\t{l+1}\t{pkh:.4f}\t{ps:.3E}\t{pn:.3f}\t{pv:.3E}\t{pl:.4f}\t{sce:.3E}\t{sci:.3E}\n')

    return
