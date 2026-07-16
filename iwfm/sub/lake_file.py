# lake_file.py
# Copy the simulation lake main file and reduce to the lakes in a submodel
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


def sub_lake_file(sim_files, sim_files_new, lake_info, verbose=False):
    '''sub_lake_file() - Read the original Simulation lake main file, keep
        only the lakes that are in the submodel, and write out a new file

    Handles lake component versions 4.0 and 5.0:
      - v4.0 file names: MXLKELVFL, LKBUDFL, FNLKELVFL; parameter rows are
        `IL CLAKE DLAKE ICHLMAX ICETLK ICPCPLK NAMELK`
      - v5.0 file names: LKBUDFL, FNLKELVFL; parameter rows are
        `IL CLAKE DLAKE ICETLK ICPCPLK NAMELK`, followed by an outflow
        rating-table section (`IL NPOINTS LKL LKQ` + NPOINTS-1 continuation
        rows per lake)
    Both versions end with an initial-elevation section (`ILAKE HLAKE`).

    Kept rows are written verbatim; lakes keep their original ID numbers
    (matching the preprocessor-side sub_pp_lake_file). The v4.0 MXLKELVFL
    time-series file reference and its ICHLMAX column pointers are left
    unchanged, as are the LKBUDFL/FNLKELVFL output file names.

    Parameters
    ----------
    sim_files : SimulationFiles
        existing model file names

    sim_files_new : SimulationFiles
        new submodel file names

    lake_info : list
        submodel lake info from sub_pp_lakes() (first item of each entry
        is the lake ID)

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    comments = 'Cc*#'

    lake_file = sim_files.lake_file
    iwfm.file_test(lake_file)
    with open(lake_file, encoding='utf-8') as f:
        lake_lines = f.read().splitlines()

    sub_ids = {int(info[0]) for info in lake_info}

    # lake component version from the first line, e.g. '#4.0'
    version = lake_lines[0][1:].strip() if len(lake_lines[0]) > 1 else ''
    v5 = version.startswith('5')

    def is_data(index):
        line = lake_lines[index].strip()
        return bool(line) and lake_lines[index][0] not in comments

    # -- skip the file-name lines (v4.0: MXLKELVFL, LKBUDFL, FNLKELVFL;
    #    v5.0: LKBUDFL, FNLKELVFL) and the FACTK/TUNITK/FACTL lines
    n_skip = (2 if v5 else 3) + 3
    line_index = -1
    for _ in range(n_skip):
        _, line_index = read_next_line_value(lake_lines, line_index, column=0)

    # -- lake parameter rows: contiguous data lines, one per lake
    _, line_index = read_next_line_value(lake_lines, line_index, column=0)
    delete = []
    lake_order = []  # lake IDs in file order, for the rating tables
    while line_index < len(lake_lines) and is_data(line_index):
        lake_id = int(lake_lines[line_index].split()[0])
        lake_order.append(lake_id)
        if lake_id not in sub_ids:
            delete.append(line_index)
        line_index += 1

    # -- v5.0 only: outflow rating tables
    if v5:
        # skip FACTLKL, FACTLKQ, TUNITLKQ
        line_index -= 1
        for _ in range(3):
            _, line_index = read_next_line_value(lake_lines, line_index, column=0)
        # one block per lake: `IL NPOINTS LKL LKQ` + NPOINTS-1 rows
        for _ in range(len(lake_order)):
            _, line_index = read_next_line_value(lake_lines, line_index, column=0)
            parts = lake_lines[line_index].split()
            lake_id, npoints = int(parts[0]), int(parts[1])
            block = [line_index]
            for _ in range(npoints - 1):
                _, line_index = read_next_line_value(lake_lines, line_index, column=0)
                block.append(line_index)
            if lake_id not in sub_ids:
                delete.extend(block)

    # -- initial lake elevations: FACT line, then one `ILAKE HLAKE` row per lake
    _, line_index = read_next_line_value(lake_lines, line_index, column=0)  # FACT
    for _ in range(len(lake_order)):
        _, line_index = read_next_line_value(lake_lines, line_index, column=0)
        if int(lake_lines[line_index].split()[0]) not in sub_ids:
            delete.append(line_index)

    # -- write out everything except the deleted rows
    delete = set(delete)
    new_lake_file = sim_files_new.lake_file
    with open(new_lake_file, 'w', encoding='utf-8') as f:
        for index, line in enumerate(lake_lines):
            if index not in delete:
                f.write(line + '\n')

    if verbose:
        print(f'  Wrote submodel lake file {new_lake_file}')

    return
