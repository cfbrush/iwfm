# write_lu2file.py
# Write IWFM land use to file
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


def write_lu2file(out_table,out_file,in_years,date_head_tail=['09/30/', '_24:00'],
    verbose=False,lu_type = ''):
    '''Write IWFM land use to file.

    Parameters
    ----------
    out_table : list
        IWFM land use information

    out_file : str
        Name of output file

    in_years : list
        Calendar years 

    date_head_tail : list, default=['09/30/', '_24:00']
        Strings to convert in_year to DSS format

    verbose : bool, default=False
        Turn command-line output on or off

    lu_type : str, default=''
        Land use type for verbose output

    Returns
    -------
    nothing
    '''
    with open(out_file, 'w', encoding='utf-8') as f:
        for i in range(0,len(in_years)):
            date = date_head_tail[0] + str(in_years[i]) + date_head_tail[1]  # date in DSS format
            for j in range(0, len(out_table[i])):
                if j == 0:  # start line with date in DSS format
                    f.write(date)
                f.write('\t' + str(j + 1) + '\t')  # elem number
                for word in out_table[i][j]:
                    f.write(str(round(word, 2)) + '\t')
                f.write('\n')

    if verbose:
        if len(in_years)==1:
            print(f'  Wrote {lu_type} land use for {in_years[0]} to {out_file}')
        else:
            print(f'  Wrote {lu_type} land use for {len(in_years)} years to {out_file}')

    return 
