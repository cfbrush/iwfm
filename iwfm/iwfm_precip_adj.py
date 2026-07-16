# iwfm_precip_adj.py
# Read IWFM precipitation file, list of VIC cells and VIC adjustment factors
# and write adjusted precipitation file
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


def iwfm_precip_adj(precip_filename,elem_VIC_filemane,factors_filename,
    years_filename,out_filename,verbose=False,per_line=6):
    ''' iwfm_precip_adj() - Read an IWFM precipitation file, a list of VIC grid 
        cells for each precipitation column, and a table of monthly adjustment 
        factors for each VIC grid cell, and writes out an IWFM precipitation 
        file with precipitation rates adjusted by the VIC factors

    Parameters
    ----------
    precip_filename : str
      Name of existing IWFM precipitation file

    elem_VIC_filemane : str
      Name of file linking model elements to VIC elements

    factors_filename : str
      Name of file with VIC factors

    years_filename : str
      Name of file with replacement years

    out_filename : str
      Name of output IWFM precipitation file
    
    verbose : bool, default=False
     Turn command-line output on or off
    
    per_line : int, default=6
      If verbose==True, number of items to write to CLI per line

    Returns
    -------
    nothing

    '''
    import re
    import sys
    import numpy as np
    import iwfm

    skip = 5  # skip 5 non-comment lines before reaching data lines

    # -- read precip column-VIC grid linkage ------------------------
    # data: precip col -> region, VIC ID
    iwfm.file_test(elem_VIC_filemane)
    with open(elem_VIC_filemane, encoding='utf-8') as f:
        elem_vic = f.read().splitlines()
    elem_vic.pop(0)  # remove header lines
    vic_rows = len(elem_vic)

    vic_cols = {}
    for item in elem_vic:
        item = re.split(';|,|\t', item)
        vic_cols[int(item[0])]=[int(item[1]),item[2],item[3]]
    if verbose:
        print(f'  Read VIC grid data for {vic_rows:,} precipitation columns')

    # -- get the climate factors ------------------------------------
    iwfm.file_test(factors_filename)
    with open(factors_filename, encoding='utf-8') as f:
        factors = f.read().splitlines()  # open and read input file
    factors.pop(0)  # remove header row
    
    d_factors, vic_years, i = {}, [], 0
    while i < len(factors) and len(factors[i]) > 1:  # put factors into a dictionary
        factor = re.split(';|,|\t', factors[i])
        mm, dd, yy = re.split('/', factor[0])
        month = str(yy) + '-' + str(mm)
        if yy not in vic_years:
            vic_years.append(yy)  # list of calendar years with factors
        factor = [float(x) for x in factor[1:]]
        d_factors[month] = factor
        i += 1

   # -- replacement years for years without VIC factors ------------
    iwfm.file_test(years_filename)
    with open(years_filename, encoding='utf-8') as f:
        rep_years = f.read().splitlines()  # open and read input file

    d_repyr_col = {}  # region name -> column of replacement years file
    rep_list = rep_years[0].split(',') # header
    for i in range(1, len(rep_list)):
        d_repyr_col[rep_list[i]] = i - 1

    # create a dictionary of all years and replacement years for missing VIC years
    rep_years.pop(0)  # remove header line
    d_VICyear = {}
    for year in rep_years:
        item = re.split(';|,|\t', year)
        item = [int(x) for x in item]
        d_VICyear[item[0]] = item[1:]

    # -- read IWFM precipitation file ------------------------------------
    iwfm.file_test(precip_filename)
    with open(precip_filename, encoding='utf-8') as f:
        precip = f.read().splitlines()  # open and read input file

    with open(out_filename, 'w', encoding='utf-8') as of: # open output file for copy of header info

        # find line with first data set, get month and year
        pline, status = 0, 1  # pline = line being processed, continue until status < 1
        while status > 0:
            if precip[pline][0] == 'C':  # skip lines that begin with 'C', 'c' or '*'
                of.write(precip[pline] + '\n')
                pline += 1
            elif precip[pline][0] != 'C':
                if skip > 0:  # also handle the other header lines
                    of.write(precip[pline] + '\n')
                    skip -= 1
                    pline += 1
                else:
                    items = precip[pline].split()
                    cols = len(items)
                    status = 0

        # -- do the work -------------------------------------------------
        if verbose:
            print(f'  Processing {len(precip) - pline :,} precipitation dates...')

        if verbose:  # create outport to write unbuffered output to console
            outport = iwfm.Unbuffered(sys.stdout)

        print_count = 0
        # write out the factors to a separate file just in case...
        with open('factors.dat', 'w', encoding='utf-8') as factfile:  
            factfile.write('Date            \t' + '\t'.join(map(str, [i for i in range(1,cols+1)])) + '\n')

            # process each row of the precipitation file, replacing adjusted values
            while pline < len(precip) and len(precip[pline]) > 10:
                items = precip[pline].split()
                pline += 1

                p = [float(x) for x in items[1:]] # precip

                date = items[0].replace('_24:00', '')
                if verbose:  # write progress to console
                    if print_count > per_line - 2:
                        outport.write(' ' + date)
                        print_count = 0
                    else:
                        if print_count == 0:
                            outport.write('\n  ' + date)
                        else:
                            outport.write(' ' + date)
                        print_count += 1

                f, ex = [], []
                for e in range(1, len(items)):  # cycle through precip columns
                    try:
                        vic_id = vic_cols[e][0]  # precip column -> VIC_ID
                    except (KeyError, IndexError):
                        # No VIC ID for this column - use factor of 1.0 (no change)
                        f.append(1.0)  # factor of precip column
                        ex.append(e)
                    else:
                        mm, dd, yy = re.split('/', date)
                        month = str(yy) + '-' + str(int(mm))

                        if yy not in vic_years:  # use replacement years
                            # replacement year can vary by precip column
                            repyr = d_VICyear[int(yy)]     # replacement year as string
                            yy = repyr[d_repyr_col[vic_cols[e][1]]]
                            month = str(yy) + '-' + str(int(mm))

                        f.append(d_factors[month][vic_id-1])  # factor of precip column

                new_p = np.round(np.array(p) * np.array(f), 2)
                of.write(items[0] + '\t' + '\t'.join(map(str, new_p)) + '\n')
                factfile.write(items[0] + '\t' + '\t'.join(map(str, [round(F,2) for F in f])) + '\n')


    if verbose:  # write progress to console
        outport.write('\n')
        if len(ex) > 0:
            print('\n  These precipitation columns had no VIC ID and were not changed:')
            print('   '+','.join([str(i) for i in ex]))

        print(f'\n  Wrote adjusted precipitation rates to {out_filename}\n')
    return


if __name__ == '__main__':
    ' Run iwfm_precip_adj() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        precip_filename = sys.argv[1]
        elem_VIC_filemane = sys.argv[2]
        factors_filename = sys.argv[3]
        years_filename = sys.argv[4]
        out_filename = sys.argv[5]

    else:  # ask for file names from terminal
        precip_filename   = input('IWFM Precipitation file name: ')
        elem_VIC_filemane = input('Element-VIC file name: ')
        factors_filename  = input('Factors file name: ')
        years_filename    = input('Years file name: ')
        out_filename      = input('Output file name: ')

    iwfm.file_test(precip_filename)
    iwfm.file_test(elem_VIC_filemane)
    iwfm.file_test(factors_filename)
    iwfm.file_test(years_filename)

    idb.exe_time()  # initialize timer
    iwfm_precip_adj(precip_filename,elem_VIC_filemane,factors_filename,
        years_filename,out_filename,verbose=True)

    idb.exe_time()  # print elapsed time
