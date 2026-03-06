# get_obs_hyd.py
# Extract one column from a VIC file to another file
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

from iwfm.debug.logger_setup import logger


def get_obs_hyd(obs_file,start_date):
    ''' get_obs_hyd - reads an observation sample bore (smp) file, and returns a list
        of observation sites and a list of observation data as [site_id, days since
        start, date as datetime object]

    Parameters
    ----------
    obs_file : str
        name of observation file (in SMP format)

    start_date : datetime object
        simulation starting date


    Returns
    -------
    obs_sites : list of str
        observation site names

    obs_data : list
        [site name, days since start, date as datetime object]

    '''

    from datetime import datetime

    logger.debug(f'get_obs_hyd(): reading {obs_file}')
    with open(obs_file) as f:
        obs_lines = f.read().splitlines()                         # obs_lines has observations to match
    logger.debug(f'  Read {len(obs_lines):,} lines from {obs_file}')

    obs_data, obs_sites = [], []
    for count, line in enumerate(obs_lines):
        item = line.split()

        if len(item) < 2:                                                  # error
            logger.error(f'Error at line {count:,} of {obs_file}: "{line}"')
            print(f'\n * Error at line {count:,} of {obs_file}: ')         # error
            print(f' * "{line}"\n\n')                                      # error
            import sys                                                     # error
            sys.exit()                                                     # error

        if item[0] not in obs_sites:
            obs_sites.append(item[0])

        date_obj = datetime.strptime(item[1], '%m/%d/%Y')  # string to datetime
        days = (date_obj - start_date).days  # days since start date
        obs_data.append([item[0], days, date_obj])  # site, days since start, date as datetime object

    obs_data.sort( key = lambda l: (l[0], l[1]))
    obs_sites.sort( key = lambda l: (l[0]))

    logger.info(f'  Read {len(obs_sites):,} observation sites, {len(obs_data):,} observations from {obs_file}')
    return obs_sites, obs_data
