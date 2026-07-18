# sub_sim_file.py
# Copies the old simulation input file, replaces the file names with
# those of the new submodel, and writes out the new file
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


def sub_sim_file(in_sim_file, sim_files_new, has_lake=False):
    '''Copy the old simulation input file, replacing the file names with those of the new model, and write out the new file.

    Parameters
    ----------
    in_sim_file : str
        name of existing simprocessor main input file

    sim_files_new : SimulationFiles
        SimulationFiles dataclass of submodel simulation file names

    has_lake : bool, default=False
        does the submodel have a lake file?

    Returns:
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    # -- read the simprocessor file into array sim_lines
    iwfm.file_test(in_sim_file)
    with open(in_sim_file, encoding='utf-8') as f:
        sim_lines = f.read().splitlines()  # open and read input file

    _, line_index = read_next_line_value(sim_lines, -1, column=0, skip_lines=3)  # skip comments and three header lines

    # -- preprocessor output file
    sim_lines[line_index] = (' ' * 4 + sim_files_new.preout).ljust(53) + ' '.join(
        sim_lines[line_index].split()[1:]
    )  # indent 4 chars, pad to 53

    # -- groundwater file
    _, line_index = read_next_line_value(sim_lines, line_index, column=0, skip_lines=0)
    sim_lines[line_index] = (' ' * 4 + sim_files_new.gw_file).ljust(53) + ' '.join(sim_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- stream file
    _, line_index = read_next_line_value(sim_lines, line_index, column=0, skip_lines=0)
    sim_lines[line_index] = (' ' * 4 + sim_files_new.stream_file).ljust(53) + ' '.join(sim_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- lake file
    _, line_index = read_next_line_value(sim_lines, line_index, column=0, skip_lines=0)
    if has_lake:
        sim_lines[line_index] = (' ' * 4 + sim_files_new.lake_file).ljust(53) + ' '.join(sim_lines[line_index].split()[1:])  # indent 4 chars, pad to 53
    else:
        # blank the lake file name (the original model may have a lake file
        # even when the submodel contains no lakes); keep the '/ ...' tail
        parts = sim_lines[line_index].split()
        tail = next((n for n, p in enumerate(parts) if p.startswith('/')), None)
        if tail is not None and tail > 0:  # a lake file name precedes the '/'
            sim_lines[line_index] = (' ' * 53) + ' '.join(parts[tail:])

    # -- rootzone file
    _, line_index = read_next_line_value(sim_lines, line_index, column=0, skip_lines=0)
    sim_lines[line_index] = (' ' * 4 + sim_files_new.root_file).ljust(53) + ' '.join(sim_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- small watersheds file
    _, line_index = read_next_line_value(sim_lines, line_index, column=0, skip_lines=0)
    sim_lines[line_index] = (' ' * 4 + sim_files_new.swshed_file).ljust(53) + ' '.join(sim_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- unsaturated file
    _, line_index = read_next_line_value(sim_lines, line_index, column=0, skip_lines=0)
    sim_lines[line_index] = (' ' * 4 + sim_files_new.unsat_file).ljust(53) + ' '.join(sim_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    sim_lines.append('')

    # -- write new simulation input file
    with open(sim_files_new.sim_name, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(sim_lines))

    return
