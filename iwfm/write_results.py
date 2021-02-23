# write_results.py
# Writes simulated and observed values for one observation well to a text file
# Copyright (C) 2020-2021 Hydrolytics LLC
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
    """ write_results() - Write simulated and observed values for one 
        observation well to a text file

    Parameters:
      name            (str):  Name of output file
      date            (list): Dates corresponding to measured values
      meas            (list): Measured values
      sim             (list): Simulated equivalents to measured values
      start_date      (str):  Date in MM/DD/YYYY format

    Returns:
      nothing
    
    """
    import iwfm as iwfm
    output_filename = name + '_obs.out'
    with open(output_filename, 'w') as output_file:
        output_file.write('# Observations for well {}\n'.format(name))
        output_file.write('# Date\tObserved\tModeled\n')
        for i in range(0, len(date)):
            output_file.write(
                '{}\t{}\t{}\n'.format(
                    iwfm.date_index(int(date[i]), start_date), meas[i], sim[i]
                )
            )
    return