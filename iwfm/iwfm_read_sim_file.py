# iwfm_read_sim_file.py
# Read IWFM simulation main file and return dictionary of file names
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


'''Read IWFM simulation main file and return dictionary of file names.'''

def iwfm_read_sim_file(sim_file, verbose=False):
    '''Read an IWFM Simulation main input file and return a list of the files called and some settings.

    Parameters
    ----------
    sim_file : str
        name of existing model main input file

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    sim_files : SimulationFiles
        SimulationFiles dataclass of existing model file names

    have_lake : bool
        True if existing model has a lake file
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from iwfm.iwfm_dataclasses import SimulationFiles

    if verbose: print(f"Entered iwfm_read_sim_file() with {sim_file}")

    iwfm.file_test(sim_file)
    with open(sim_file, encoding='utf-8') as f:
        sim_lines = f.read().splitlines()              # open and read input file

    preout, line_index = read_next_line_value(sim_lines, -1, skip_lines=3)  # preproc output file

    gw_file, line_index = read_next_line_value(sim_lines, line_index)  # groundwater main file

    stream_file, line_index = read_next_line_value(sim_lines, line_index)  # streams main file

    lake_file, line_index = read_next_line_value(sim_lines, line_index)  # lake file
    have_lake = True
    if lake_file[0] == '/':
        lake_file = ''
        have_lake = False

    root_file, line_index = read_next_line_value(sim_lines, line_index)  # root zone main file

    swshed_file, line_index = read_next_line_value(sim_lines, line_index)  # small watersheds file

    unsat_file, line_index = read_next_line_value(sim_lines, line_index)  # unsaturated zone file

    precip_file, line_index = read_next_line_value(sim_lines, line_index, skip_lines=2)  # precipitation file

    et_file, line_index = read_next_line_value(sim_lines, line_index)  # evapotranspiration file

    if verbose: print("Leaving iwfm_read_sim_file()")

    sim_files = SimulationFiles(
        preout=preout,
        gw_file=gw_file,
        stream_file=stream_file,
        lake_file=lake_file,
        root_file=root_file,
        swshed_file=swshed_file,
        unsat_file=unsat_file,
        precip=precip_file,
        et=et_file,
    )

    return sim_files, have_lake
