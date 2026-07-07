# write_missing.py
# Write observation IDs with no simulated equivalent to a text file
# Copyright (C) 2020-2023 University of California
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

def write_missing(missing,obs_file,fname='missing.tmp',verbose=False):
    ''' write_missing() - takes a list of observation IDs and filename obs_file, 
        and writes them to an output files (default output file name missing.tmp). 
        This is used to write out the observation IDs of observations in the observation
        data set that are not used in the simulation file 
        
    Parameters
    ----------
    missing : list of strings
        observation names

    obs_file : str
        observation file name

    fname : str, default = 'missing.tmp'
        output file name

    Returns
    -------
    nothing

    '''

    if len(missing) > 0:
        missing.sort()
        with open(fname, 'a', encoding='utf-8') as fmiss:
            fmiss.write(f'Simulation sites not in {obs_file}:\n')
            for item in missing:
                fmiss.write(f'{item}\n')
            fmiss.write('\n')
    return
