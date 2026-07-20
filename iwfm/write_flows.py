# write_flows.py
# Write flow data frm table to csv file
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


'''Write flow data from a table to a csv file.'''

def write_flows(data_file_base, file_type, table, site_info, verbose=False):
    '''Write flow data from a table to a csv file.

    Parameters
    ----------
    data_file_base : str
        Output file base name

    file_type : str
        Flow data description for file name

    table : list
        Data

    site_info : list
        Column headers

    verbose : bool
        Turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import os
    import csv
    import numpy as np

    outFileName = os.path.splitext(data_file_base)[0] + file_type + '.csv'

    with open(outFileName, 'w', newline='', encoding='utf-8') as outFile:
        outWriter = csv.writer(outFile)

        # write header info
        out_sites = np.array(site_info).T  # transpose
        for i in range(0, len(out_sites)):
            outWriter.writerow(out_sites[i])

        # write out_table
        out_table = np.array(table).T  # transpose
        for i in range(0, len(out_table)):
            outWriter.writerow(out_table[i])

    if verbose:
        print(f'  Wrote {len(table)} cols x {len(table[0])} rows to {outFileName}')

    return
