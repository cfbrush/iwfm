# sub_pp_file.py
# Copies the old preprocessor input file, replaces the file names with
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


def sub_pp_file(in_pp_file, pre_files, pre_files_new, has_lake=False):
    '''Copy the old preprocessor input file, replacing the file names with those of the new model, and write out the new file.

    Parameters
    ----------
    in_pp_file : str
        name of existing preprocessor main input file

    pre_files : PreprocessorFiles
        PreprocessorFiles dataclass of existing model preprocessor file names

    pre_files_new : PreprocessorFiles
        PreprocessorFiles dataclass of submodel preprocessor file names

    has_lake : bool, default=False
        does the submodel have a lake file?

    Returns:
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    # -- read the preprocessor file into array pre_lines
    iwfm.file_test(in_pp_file)
    with open(in_pp_file, encoding='utf-8') as f:
        pre_lines = f.read().splitlines()  # open and read input file

    # -- preproc output file (skip comments + 3 title lines)
    _, line_index = read_next_line_value(pre_lines, -1, column=0, skip_lines=3)
    pre_lines[line_index] = (' ' * 4 + pre_files_new.preout).ljust(53) + ' '.join(
        pre_lines[line_index].split()[1:]
    )  # indent 4 chars, pad to 53

    # -- element file
    _, line_index = read_next_line_value(pre_lines, line_index, column=0, skip_lines=0)
    pre_lines[line_index] = (' ' * 4 + pre_files_new.elem_file).ljust(53) + ' '.join(pre_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- node file
    _, line_index = read_next_line_value(pre_lines, line_index, column=0, skip_lines=0)
    pre_lines[line_index] = (' ' * 4 + pre_files_new.node_file).ljust(53) + ' '.join(pre_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- stratigraphy file
    _, line_index = read_next_line_value(pre_lines, line_index, column=0, skip_lines=0)
    pre_lines[line_index] = (' ' * 4 + pre_files_new.strat_file).ljust(53) + ' '.join(pre_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- stream file
    _, line_index = read_next_line_value(pre_lines, line_index, column=0, skip_lines=0)
    pre_lines[line_index] = (' ' * 4 + pre_files_new.stream_file).ljust(53) + ' '.join(pre_lines[line_index].split()[1:])  # indent 4 chars, pad to 53

    # -- lake file
    _, line_index = read_next_line_value(pre_lines, line_index, column=0, skip_lines=0)
    if len(pre_files.lake_file) > 1 and has_lake:
        pre_lines[line_index] = (' ' * 4 + pre_files_new.lake_file).ljust(53) + ' '.join(pre_lines[line_index].split()[1:])  # indent 4 chars, pad to 53
    else:
        pre_lines[line_index] = (
            (' ' * 4 + ' ').ljust(53)  # indent 4 chars, pad to 53
            + '/ '
            + ' '.join(pre_lines[line_index].split()[1:])
        )

    pre_lines.append('')
    # -- write new preprocessor input file
    with open(pre_files_new.prename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(pre_lines))

    return
