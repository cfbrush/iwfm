# headdiff_hyds.py
# calculates vertical head differences
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

'''Calculate vertical head differences.'''

from math import ceil


def headdiff_hyds(hdiff_pairs, hdiff_data, rthresh, ts_func, start_date, verbose=False):
    '''Calculate vertical head differences and write them to a sample bore (smp) file.

    Parameters
    ----------
    hdiff_sites : list
        list of head difference sites

    hdiff_pairs : list
        list of head difference pairs

    rthresh : float
        threshold

    ts_func : ?
        ?

    start_date : dtaetime object
        simulation start time

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    smp_out : list of floats
        head difference for each pair in smp format

    ins_out : list of strings
        instructions for reading smp_out data
    '''
    import iwfm.calib as icalib

    smp_out, ins_out, temp, data, sites = [], [], [], [], []
    hdiff_data.sort( key = lambda l: (l[0], l[1]))                      # sort by site then by date

    old_site = hdiff_data[0][0]
    for item in hdiff_data:
        site = item[0]
        if site != old_site:  # finish this site, prep for next
            data.append(temp)
            temp = []
            sites.append(old_site)
            old_site = site
        temp.append([item[1],item[2]])
    # finish last site
    data.append(temp)
    sites.append(old_site)
    # now data is a 2d array, each col a different site (indexed with sites), each row date and time

    # now step through hdiff_pairs, and calculate head differences
    for pair in hdiff_pairs:
        if pair[0] in sites and pair[1] in sites:
            left, right = pair[0], pair[1]
            site = f'{left}_{right}'
            left_col, right_col = sites.index(left), sites.index(right)     # which columns of data

            for i in range(0,len(data[left_col])):
                d_left, d_right = data[left_col][i][0],data[right_col][i][0]
                if abs((d_left - d_right).days) <= rthresh:
                    obs_val = data[left_col][i][1] - data[right_col][i][1]
                    ts = ceil(float(ts_func((d_left - start_date).days)))  # date to time step w/interpolation function
                    smp, ins = icalib.to_smp_ins(site,d_left,obs_val,ts)        # put into smp and ins strings

                    smp_out.append(smp)                                           # add smp string to smp_out list
                    ins_out.append(ins)                                           # add ins string to ins_out list
    return smp_out, ins_out
