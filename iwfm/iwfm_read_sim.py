# iwfm_read_sim.py
# Read IWFM Simulation main file
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


def iwfm_read_sim(sim_file, verbose=False):
    ''' iwfm_read_sim() - Read an IWFM Simulation main input file, and
        return a SimulationFiles dataclass with the files called and some settings

    Parameters
    ----------
    sim_file : str
        Name of IWFM Simulation file

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    sim_files : SimulationFiles
        SimulationFiles dataclass with file names and settings.
        Field names: preout, gw_file, stream_file, lake_file, root_file,
        swshed_file, unsat_file, irrfrac, supplyadj, precip, et,
        start, step, end.

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from iwfm.iwfm_dataclasses import SimulationFiles

    if verbose: print(f"Entered iwfm_read_sim() with {sim_file}")

    iwfm.file_test(sim_file)
    with open(sim_file, encoding='utf-8') as f:
        sim_lines = f.read().splitlines()

    preout, line_index = read_next_line_value(sim_lines, -1, skip_lines=3)

    gw_file, line_index = read_next_line_value(sim_lines, line_index)

    stream_file, line_index = read_next_line_value(sim_lines, line_index)

    temp, line_index = read_next_line_value(sim_lines, line_index)
    if temp[0] == '/':   # check for presence of lake file
        lake_file = ''
    else:
        lake_file = temp

    root_file, line_index = read_next_line_value(sim_lines, line_index)

    swshed_file, line_index = read_next_line_value(sim_lines, line_index)

    unsat_file, line_index = read_next_line_value(sim_lines, line_index)

    irrfrac, line_index = read_next_line_value(sim_lines, line_index)

    supplyadj, line_index = read_next_line_value(sim_lines, line_index)

    precip, line_index = read_next_line_value(sim_lines, line_index)

    et, line_index = read_next_line_value(sim_lines, line_index)

    start, line_index = read_next_line_value(sim_lines, line_index)

    step, line_index = read_next_line_value(sim_lines, line_index, skip_lines=1)

    end, line_index = read_next_line_value(sim_lines, line_index)

    if verbose: print("Leaving iwfm_read_sim()")

    return SimulationFiles(
        preout=preout,
        gw_file=gw_file,
        stream_file=stream_file,
        lake_file=lake_file,
        root_file=root_file,
        swshed_file=swshed_file,
        unsat_file=unsat_file,
        irrfrac=irrfrac,
        supplyadj=supplyadj,
        precip=precip,
        et=et,
        start=start,
        step=step,
        end=end,
    )
