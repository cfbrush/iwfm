# well_pairs_2_obs_list.py
# Read a file of paired observation well locations for groundwater head differences
# and a file of head observations. For each well pair, find matching observations 
# +/- a specified number of days. For each set of well names, write the matching
# observations, mean date and head difference.
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

def well_pairs_2_obs_list(well_pair_file, obs_file, days=15, verbose=False):
    '''Read a file of paired observation well locations for groundwater head differences and a file of head observations.

    For each well pair, find matching observations +/- a specified number of days. For each set of well names, write the matching

    Parameters
    ----------
    well_pair_file : str
        name of csv file containing paired well names.
        File contents ``PairNo, WellName1, WellName2``::

            PairNo    : int, index number for well pair
            WellName1 : str, name of first well
            WellName2 : str, name of second well

    obs_file : str
        name of csv file containing head observations.
        File contents ``WELL_NAME, MSMT_DATE, WSE``::

            WELL_NAME : str, name of well
            MSMT_DATE : str, date of measurement (mm/dd/yyyy)
            WSE       : float, water surface elevation

    days : int (default: 15)
        window for matching dates between two wells

    Verbose : bool (default: False)
        print additional information to terminal

    Returns
    -------
    well_pair_count : int
        number of well pairs pocessed

    obs_count : list
        number of vertical head difference values 




    '''
    import datetime

    with open(well_pair_file, encoding='utf-8') as f:
        well_lines = f.read().splitlines()         # open and read input file
    well_lines.pop(0)                                             # remove first line of well_lines (header)

    import iwfm

    with open(obs_file, encoding='utf-8') as f:
        obs_lines =  f.read().splitlines()               # open and read input file
    obs_lines.pop(0)                                              # remove first line of obs_lines (header)

    # Convert second column of obs_lines to datetime objects
    obs_lines = [line.split(',') for line in obs_lines]           # split into list of lists

    # Validate and parse dates
    parsed_obs_lines = []
    for i, line in enumerate(obs_lines):
        try:
            date_dt = iwfm.safe_parse_date(line[1], f'{obs_file} line {i+2}')  # +2 because header was removed
        except ValueError as e:
            raise ValueError(f"Error reading {obs_file} line {i+2}: {str(e)}") from e
        parsed_obs_lines.append([line[0], date_dt, line[2]])
    obs_lines = parsed_obs_lines

    obs_match, well_count, obs_count = [], 0, 0

    for well_pair in well_lines:
        well_count += 1
        well_pair_id, well_1, well_2 = well_pair.split(',')

        obs_1 = [line for line in obs_lines if line[0] == well_1]        # Get observations for well_1 from obs_lines
        obs_2 = [line for line in obs_lines if line[0] == well_2]        # Get observations for well_2 from obs_lines

        # Find matching observations +/- days
        for obs_1_line in obs_1:
            obs_1_date, obs_1_head = obs_1_line[1], obs_1_line[2]
            for obs_2_line in obs_2:
                obs_2_date, obs_2_head = obs_2_line[1], obs_2_line[2]

                if obs_2_date >= obs_1_date - datetime.timedelta(days=days) and obs_2_date <= obs_1_date + datetime.timedelta(days=days):
                    mid_date = obs_1_date + (obs_2_date - obs_1_date)/2
                    head_diff = float(obs_1_head) - float(obs_2_head)
                    date_1, date_2, date_3 = obs_1_date.strftime("%m/%d/%Y"), obs_2_date.strftime("%m/%d/%Y"), mid_date.strftime("%m/%d/%Y")
                    obs_match.append([well_pair_id, well_1, date_1, obs_1_head, well_2, date_2, obs_2_head, date_3, round(head_diff, 2)])
                    obs_count += 1
                    break

    # Create output file name from input file name
    output_file = well_pair_file.replace('.csv', '_headfiff.csv')
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('WELL_PAIR_ID,WELL_1_NAME,WELL_1_DATE,WELL_1_HEAD,WELL_2_NAME,WELL_2_DATE,WELL_2_HEAD,MID_DATE,HEAD_DIFF\n')
        for line in obs_match:
            f.write(f'{line[0]},{line[1]},{line[2]},{line[3]},{line[4]},{line[5]},{line[6]},{line[7]}\n')

    return well_count, obs_count, output_file


if __name__ == '__main__':
    ' Run well_pairs_2_obs_list() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        well_pair_file  = sys.argv[1]
        obs_file        = sys.argv[2]
    else:  # ask for file names from terminal
        well_pair_file  = input('Well pair file name (csv): ')
        obs_file        = input('Head observations file name (csv): ')

    iwfm.file_test(well_pair_file)
    iwfm.file_test(obs_file)

    idb.exe_time()  # initialize timer

    well_count, obs_count, output_file = well_pairs_2_obs_list(well_pair_file, obs_file)

    print(f'\n  Wrote {obs_count:,} vertical head differences at {well_count:,} wells to {output_file}')
    idb.exe_time()  # print elapsed time
