# to_smp_ins.py
# Write smp and ins file lines for one observation
# Copyright (C) 2020-2026 University of California
# Based on a PEST utility written by John Doherty
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


def to_smp_ins(obs_site,obs_dt,obs_val,ts):   # put into smp and ins strings
    ''' to_smp_ins() - Write smp and ins file lines for one observation

    Parameters
    ----------
    obs_site : str
        site name

    obs_dt : datetime object
        date

    obs_val : float
        simulated value

    ts : ind
        time step

    Returns
    -------
    smp : string
        the observation in smp-file format: 
             'obs_site             mm/dd/yyyy  0:00:00                obs_val'

    ins : string
        the observation in ins-file format: 
             'L1  [obs_site_0ts]42:70'

    '''


    smp = str(f'{obs_site.ljust(20)} {obs_dt.strftime("%m/%d/%Y")}  0:00:00 {str(round(obs_val,6)).rjust(22)}')  # left-justify to 20 chars, right-justify to 22 chars
    ins = str(f'L1  [{obs_site}_{str(ts).rjust(3, "0")}]42:70')  # right-justify to 3 chars

    return smp, ins