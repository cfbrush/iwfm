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

    Raises
    ------
    SystemExit
        If ``in_file`` does not exist (via :func:`iwfm.file_test`).
    ValueError
        If the parsed start_date or end_date does not match the expected
        ``MM/DD/YYYY`` (or ``MM/DD/YYYY_HH:MM``) format.

    '''
    import re
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered sim_info() with {in_file}")

    iwfm.file_test(in_file)
    with open(in_file) as f:
        sim_lines = f.read().splitlines()

    # Scan for start_date (BDT) by matching MM/DD/YYYY_HH:MM date format
    # on a non-comment data line, instead of counting lines
    date_pattern = re.compile(r'^\d{1,2}/\d{1,2}/\d{4}(_\d{2}:\d{2})?$')
    in_index = None
    for i, line in enumerate(sim_lines):
        stripped = line.strip()
        if not stripped or stripped[0] in 'Cc*#':
            continue
        first_token = stripped.split()[0]
        if date_pattern.match(first_token):
            in_index = i
            break

    if in_index is None:
        raise ValueError(f"Could not find start date (BDT) in {in_file}. "
                         f"Expected a line with MM/DD/YYYY or MM/DD/YYYY_HH:MM format.")

    start_date = sim_lines[in_index].split()[0]

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
