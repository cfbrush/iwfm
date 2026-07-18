# sub_st_bp_file.py
# Copy the stream bypass specification file and replace the contents with
# those of the new submodel, and write out the new file
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




def sub_st_bp_file(old_filename, new_filename, elem_list, snode_list, verbose=False):
    '''Copy the stream bypass specification file and replace the contents with those of the new submodel, and write out the new file.

    Parameters
    ----------
    old_filename : str
        name of existing model element ppumping file

    new_filename : str
        name of new subnmodel element pumpgin file

    elem_list : list of ints
        list of existing model elements in submodel

    snode_list : list of ints
        list of existing model stream nodes in submodel

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    elems = []
    for e in elem_list:
        elems.append(int(e[0]))

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        bp_lines = f.read().splitlines()
    bp_lines.append('\n\n\n\n\n')

    _, line_index = read_next_line_value(bp_lines, -1, column=0, skip_lines=0)  # skip initial comments

    # -- bypass specifications
    nbp = int(bp_lines[line_index].split()[0])                  # number of diversions
    new_nbp, nbp_line = 0, line_index

    _, line_index = read_next_line_value(bp_lines, line_index - 1, column=0, skip_lines=5)  # skip factors
    bp_keep, bp_nlines = [], []
    for j in range(0, nbp):
        _, line_index = read_next_line_value(bp_lines, line_index - 1, column=0, skip_lines=0)  # skip comments
        t = bp_lines[line_index].split()

        if int(t[4]) > 0:                     # one line: column of diversion file
            nlines = 1
        else:
            nlines = 1 + abs(int(t[4]))           # abs(IDIVC) columns
        bp_nlines.append(nlines)

        if int(t[1]) in snode_list:
            bp_keep.append(int(t[0]))
            new_nbp += 1
            for i in range(0, nlines):
                line_index += 1
        else:                      
            bp_keep.append(-1)
            for i in range(0, nlines):
                del bp_lines[line_index]

    bp_lines[nbp_line] = '      ' + str(new_nbp) + '                        / NDIVS'

    _, line_index = read_next_line_value(bp_lines, line_index - 1, column=0, skip_lines=0)  # skip comments to seepage section

    for i in range(0,nbp):
        _, line_index = read_next_line_value(bp_lines, line_index - 1, column=0, skip_lines=0)  # skip comments
        t = bp_lines[line_index].split()
        nlines = int(t[1])

        if bp_keep[i] < 0:
            if nlines == 0:
                del bp_lines[line_index]
            else: 
                for j in range(0, nlines):
                    del bp_lines[line_index]
        else:
            line_index += nlines
        
    bp_lines.append('')

    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(bp_lines))
    if verbose:
        print(f'      Wrote stream bypass specification file {new_filename}')

    return new_nbp
