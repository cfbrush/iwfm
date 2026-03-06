# sim_info.py
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


def sim_info(in_file, verbose=False):
    ''' sim_info() - reads simulation input file and returns the starting date, ending
        date and time step of the simulation

    Parameters
    ----------
    in_file : str
        IWFM Simulation main input file

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    start_date : str
        simulation start date in DSS format

    end_date : str
        simulation end date in DSS format

    time_step : str
        time step in DSS format

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered sim_info() with {in_file}")

    iwfm.file_test(in_file)
    with open(in_file) as f:
        sim_lines = f.read().splitlines()

    # skip 15 non-comment lines to get to start_date
    start_date, in_index = read_next_line_value(sim_lines, 0, skip_lines=15)

    # Validate start_date format
    try:
        iwfm.validate_date_format(start_date, f'{in_file} line {in_index+1} start_date')
    except ValueError as e:
        raise ValueError(f"Error reading start date from {in_file} line {in_index+1}: {str(e)}") from e

    # skip 1 non-comment line (RESTART) to get to time_step
    time_step, in_index = read_next_line_value(sim_lines, in_index, skip_lines=1)

    # next line is end_date
    end_date, in_index = read_next_line_value(sim_lines, in_index)

    # Validate end_date format
    try:
        iwfm.validate_date_format(end_date, f'{in_file} line {in_index+1} end_date')
    except ValueError as e:
        raise ValueError(f"Error reading end date from {in_file} line {in_index+1}: {str(e)}") from e

    if verbose: print(f"Leaving sim_info()")

    return start_date, end_date, time_step
