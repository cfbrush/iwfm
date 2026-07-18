# sub_swhed_file.py
# Copies the old node file and replaces the contents with those of the new
# submodel, and writes out the new file
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


def sub_swhed_file(old_filename, new_filename, node_list, snode_list, verbose=False):
    '''Read original old small watershed file, determine which small watersheds are in the submodel, and write out a new file.

    Parameters
    ----------
    old_filename : str
        name of existing nmodel small watersheds file

    new_filename : str
        name of new subnmodel small watersheds file

    node_list : ints
        list of existing model nodes in submodel

    snode_list : ints
        list of existing model stream nodes in submodel

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        swshwd_lines = f.read().splitlines()

    _, line_index = read_next_line_value(swshwd_lines, -1, column=0, skip_lines=2)  # skip output file names and comments

    nsw_line, nsw = line_index, int(swshwd_lines[line_index].split()[0])

    _, line_index = read_next_line_value(swshwd_lines, line_index + 3, column=0, skip_lines=0)  # skip NSW + 3 factors (4 lines), then comments

    sw_list = []
    for sw in range(0, nsw):  # small watershed descriptions
        change, line, items = 0, line_index, swshwd_lines[line_index].split()

        if int(items[4]) in node_list:  # if IWB = GW node in submodel, keep small watershed
            sw_list.append(int(items[0]))  # ID
            
            # if IWBTS not in submodel, replace with '0'
            if (int(items[2]) not in snode_list):
                change, items[2] = 1, '0'

            # check that each arc node is in the submodel
            for l in range(1, int(items[3])):
                _, line_index = read_next_line_value(swshwd_lines, line_index - 1, column=0, skip_lines=1)
                
                # remove this arc node and decrement nwb
                if (int(swshwd_lines[line_index].split()[0]) not in snode_list):
                    del swshwd_lines[line_index]
                    change, items[3] = 1, str(int(items[3]) - 1)
                    line_index -= 1

            if change:
                swshwd_lines[line] = '\t'.join([i for i in items])

            _, line_index = read_next_line_value(swshwd_lines, line_index - 1, column=0, skip_lines=1)
        else:  # remove these lines
            for i in range(0, int(items[3])):
                del swshwd_lines[line_index]

    # replace NSW
    swshwd_lines[nsw_line] = (' ' * 6 + str(len(sw_list))).ljust(50) + ' '.join(
        swshwd_lines[nsw_line].split()[1:]
    )  # indent 6 chars, pad to 50

    _, line_index = read_next_line_value(swshwd_lines, line_index - 1, column=0, skip_lines=6)

    # remove root zone parameters for small watersheds outside submodel
    for sw in range(0, nsw):
        if int(swshwd_lines[line_index].split()[0]) not in node_list:  # remove the line
            del swshwd_lines[line_index]
        else:
            line_index += 1

    _, line_index = read_next_line_value(swshwd_lines, line_index - 1, column=0, skip_lines=3)

    # remove aquifer parameters for small watersheds outside submodel
    for sw in range(0, nsw):
        if int(swshwd_lines[line_index].split()[0]) not in node_list:  # remove the line
            del swshwd_lines[line_index]
        else:
            line_index += 1

    _, line_index = read_next_line_value(swshwd_lines, line_index - 1, column=0, skip_lines=1)

    # remove initial conditions for small watersheds outside submodel
    for sw in range(0, nsw):
        if int(swshwd_lines[line_index].split()[0]) not in node_list:  # remove the line
            del swshwd_lines[line_index]
        else:
            line_index += 1

    swshwd_lines.append('')
    # -- write submodel small watersheds file
    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(swshwd_lines))

    if verbose:
        print(f'  Wrote small watershed file {new_filename}')

    return
