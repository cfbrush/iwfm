# sim_obs_list.py
# Read (1) IWFM Groundwater file, (2) a PEST .smp file with observed values, 
# and (3) an IWFM hydrograph output file with simulated values,
# Print a table of well IDs, dates, observed and simulated values and differences
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


def sim_obs_list(obs, well_dict, gwhyd_sim, dates):
    ''' sim_obs_list() calculaters simulated equivalents for observations and difference
      between them

    Parameters
    ----------
    obs : list
        list of observed values

    well_dict : dict
        dictionary of well information

    gwhyd_sim : list
        list of simulated values

    dates : list
        list of dates

    Returns
    -------
    sim_obs_list : list
        list of simulated and observed values
    '''

    sim_obs_list = []              # initialize list of simulated and observed values

    # cycle through the list of wells in obs to create output values
    for i in range(0,len(obs)):              # move through the file
        obs_name, obs_date , obs_meas = obs[i][0], obs[i][1], obs[i][3]
        if obs_name in well_dict and obs_date >= dates[0] and obs_date <= dates[-1]:
            col = well_dict.get(obs_name).column-1    # adjust col for zero index

            # index of date in dates before obs_date
            date_index = 0
            while dates[date_index] < obs_date:
                date_index += 1
            date_index -= 1

            # interpolate simulated values from dates before and after obs_date to get simulated equivalent on obs_date
            before_date = dates[date_index]
            after_date  = dates[date_index+1]

            before_head = gwhyd_sim[date_index][col]
            after_head  = gwhyd_sim[date_index+1][col]

            delta = float((obs_date - before_date)/(after_date - before_date))
  
            sim_equiv = before_head + (after_head - before_head) * delta

            sim_obs_list.append([obs_name, obs_date.strftime("%m/%d/%Y"), obs_meas, sim_equiv, obs_meas-sim_equiv])


    return sim_obs_list


if __name__ == '__main__':
    ' Run sim_obs_list() from command line '
    import sys
    import iwfm
    import iwfm.calib as ical
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    verbose = False

    if len(sys.argv) > 1:                    # arguments are listed on the command line
        gwhyd_info_file = sys.argv[1]          # IWFM Groundwater.data file
        obs_file        = sys.argv[2]          # pest smp file with observed values
        gwhyd_file      = sys.argv[3]          # Simulation file with simulated values
        output_file     = sys.argv[4]          # output file name

    else:                                    # get everything form the command line
        gwhyd_info_file = input("IWFM Groundwater.dat file name: ")
        obs_file        = input("Observed values file name (smp format): ")
        gwhyd_file      = input("Simulated values file name: ")
        output_file     = input("Output file name: ")

    # test that the input files exist
    from pathlib import Path
    if not Path(obs_file).is_file():
        iwfm.file_missing(obs_file)
    if not Path(gwhyd_info_file).is_file():
        iwfm.file_missing(gwhyd_info_file)
    if not Path(gwhyd_file).is_file():
        iwfm.file_missing(gwhyd_file)

    well_dict = ical.read_obs_wells(gwhyd_info_file)          # build groundwater hydrograph dictionary
    if verbose: print(f'  Read information for {len(well_dict):,} observation wells.')

    obs = ical.smp_read(obs_file)                             # read observed values
    if verbose: print(f'  Read {len(obs):,} observations.')

    sim_array = iwfm.read_sim_hyd(gwhyd_file)                  # read simulated hydrograph
    dates = list(sim_array[:, 0])                              # extract dates from column 0
    gwhyd_sim = sim_array[:, 1:].astype(float).tolist()        # extract values as list of lists

    sim_obs = sim_obs_list(obs, well_dict, gwhyd_sim, dates)  # compare simulated and observed values

    # save the results to a text file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Well ID, Date, Observed, Simulated, Difference\n") # header
        for item in sim_obs:
            f.write(f"{item[0]}, {item[1]}, {item[2]:.2f}, {item[3]:.2f}, {item[4]:.2f}\n")

    print(f'  Wrote {len(sim_obs):,} observations and simulated equivalents to {output_file}.')
    