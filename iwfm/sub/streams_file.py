# sub_streams_file.py
# Copies the old Simulation streams main file and replaces the contents with 
# those of the new submodel, and writes out the new file, then calls methods 
# to modify the other Simulation stream component files
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


def sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes, base_path=None, verbose=False):
    '''sub_streams_file() - Read the original Simulation streams main file, 
        determine which elements are in the submodel, and writes out a new file, 
        then modifies the other Simulation stream component files

    Parameters
    ----------
    sim_files : SimulationFiles
        existing model file names

    sim_files_new : SimulationFiles
        new submodel file names

    elem_list : list of ints
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

    comments = ['C','c','*','#']

    # Check if streams file is in the model
    stream_file = sim_files.stream_file
    if not stream_file:
        iwfm.file_missing('streams file', 'Not specified in simulation input file')

    # Use iwfm utility for file validation
    iwfm.file_test(stream_file)

    with open(stream_file, encoding='utf-8') as f:
        stream_lines = f.read().splitlines()
    stream_lines.append('')

    _, line_index = read_next_line_value(stream_lines, 0, column=0, skip_lines=0)  # skip initial comments (starting from line 1)

    st_dict = {}

    # inflow file name
    inflow_file = stream_lines[line_index].split()[0]                   # stream inflow file
    have_inflow = True
    if inflow_file[0] == '/':
        inflow_file = ''
        have_inflow = False
        stream_lines[line_index] = '                                         / INFLOWFL'
    else:
        inflow_file = inflow_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            inflow_file = str(base_path / inflow_file)
        stream_lines[line_index] = '   ' + sim_files_new.stin_file + '		        / INFLOWFL'
    st_dict['stin_file'] = inflow_file

    # diversion specification file name
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=0)
    divspec_file = stream_lines[line_index].split()[0]                   # tile drain main file
    have_divspec = True
    if divspec_file[0] == '/':
        divspec_file = ''
        have_divspec = False
        stream_lines[line_index] = '                                         / DIVSPECFL'
    else:
        divspec_file = divspec_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            divspec_file = str(base_path / divspec_file)
        stream_lines[line_index] = '   ' + sim_files_new.divspec_file + '		        / DIVSPECFL'
    st_dict['divspec_file'] = divspec_file

    # bypass specification file name
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=0)
    bp_file = stream_lines[line_index].split()[0]                 # bypass specification file
    bp_line = line_index
    have_bp = True
    if bp_file[0] == '/':
        bp_file = ''
        have_bp = False
        stream_lines[line_index] = '                                         / BYPSPECFL'
    else:
        bp_file = bp_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            bp_file = str(base_path / bp_file)
        stream_lines[line_index] = '   ' + sim_files_new.bp_file + '		        / BYPSPECFL'
    st_dict['bp_file'] = bp_file

    # diversion time series file
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=0)
    div_file = stream_lines[line_index].split()[0]           # subsidence main file
    have_div = True
    if div_file[0] == '/':
        div_file = ''
        have_div = False
        stream_lines[line_index] = '                                         / DIVFL'
    else:
        parts = div_file.replace('\\', ' ').split()
        if len(parts) < 2:
            raise ValueError(f"{stream_file} line {line_index}: Expected path with backslash for diversion file, got '{div_file}'")
        div_file = parts[1]
        stream_lines[line_index] = '   ' + sim_files_new.div_file + '		        / DIVFL'
    st_dict['div_file'] = div_file

    # skip comments to hydrograph section
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=2)

    nhyds = int(stream_lines[line_index].split()[0])                # number of hydrographs
    hyds_line = line_index
 
    # --  hydrograph section --
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=6)
 
    # check each hydrographs and remove the hydrographs outside the submodel boundary
    new_hyds = 0 
    for i in range(0, nhyds):
        sn = int(stream_lines[line_index].split()[0])

        if sn not in sub_snodes:
            del stream_lines[line_index]
        else:
            new_hyds += 1
            line_index += 1

    # update the number of hydrographs
    stream_lines[hyds_line] = '     ' + str(new_hyds) + '        / NOUTR'
    
    # --- stream node budgets section --
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=0)

    nbud = int(stream_lines[line_index].split()[0])                # number of stream node budgets
    buds_line = line_index
 
    # check each hydrographs and remove the hydrographs outside the submodel boundary
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=1)
    new_buds = 0 
    for i in range(0, nbud):
        sn = int(stream_lines[line_index].split()[0])

        if sn not in sub_snodes:
            del stream_lines[line_index]
        else:
            new_buds += 1
            line_index += 1

    # update the number of hydrographs
    stream_lines[buds_line] = '     ' + str(new_buds) + '        / NBUDR'
    
    # -- streambed parameters
    _, line_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=3)

    count = 0 
    while len(stream_lines) > line_index and len(stream_lines[line_index]) > 0 and stream_lines[line_index][0] not in comments:
        sn = int(stream_lines[line_index].split()[0])

        if sn not in sub_snodes:
            del stream_lines[line_index]
        else:
            count += 1
            line_index += 1

    # -- inflow file --
    if have_inflow:
        iwfm.sub_st_inflow_file(inflow_file, sim_files_new.stin_file, sub_snodes, verbose=verbose)

    # -- diversion specification file file --
    # ** too abstract - needs to be done manually

    # -- bypass specification file --
    if bp_file:
        have_bp = iwfm.sub_st_bp_file(bp_file, sim_files_new.bp_file, elem_list, sub_snodes, verbose=verbose)
        if have_bp == 0:
          stream_lines[bp_line] = '                                         / BYPSPECFL'

    # -- don't modify diversion time series file file --
    new_stream_file = sim_files_new.stream_file
    with open(new_stream_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(stream_lines))
    if verbose:
        print(f'  Wrote stream main file {new_stream_file}')

    return
