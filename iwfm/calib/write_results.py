# write_results.py
# write simulated and observed values to a text file
# Copyright (C) 2020-2021 University of California
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


def write_results(name, date, meas, sim, start_date):
    '''Write simulated and observed values for one observation well to a text file.

    Parameters
    ----------
    name : str
        Basename of output file

    date : list
        Dates for measurements

    meas : list
        Measured values

    sim : list
        Simulated equivalent values

    start_date : obj
        Simulation starting date

    Returns
    -------
    i : int
        Number of lines written
    '''
    with open(name + '_obs.out', 'w', encoding='utf-8') as o:
        o.write(f'# Observations for well {name}\n')
        o.write('# Date\tObserved\tModeled\n')
        for i in range(0, len(date)):
            o.write(f'{date[i]}\t{meas[i]}\t{sim[i]}\n')
    return i
