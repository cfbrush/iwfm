# wdl_ts_4_wells.py
# Write well data as time series
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


def wdl_ts_4_wells(station_file, waterlevel_file, verbose=False):
    ''' wdl_ts_4_wells() - Write well data as time series

    Parameters
    ----------
    station_file : str
        well information file name
    
    waterlevel_file : str
        water levels file name
    
    verbose : bool, default=True
        True = command-line output on 

    Returns
    -------
    nothing
    
    '''
    import csv
    from iwfm.debug.logger_setup import logger

    station_file_base = station_file[0 : station_file.find('.')]  # basename
    station_file_ext = station_file[
        station_file.find('.') + 1 : len(station_file) + 1
    ]  # extention
    output_file = station_file_base + '_TS.out'

    # -- read stations into a dictionary
    try:
        with open(station_file, encoding='utf-8') as f:
            file_lines = f.read().splitlines()
    except FileNotFoundError:
        logger.error(f'File not found: {station_file}')
        raise
    except PermissionError:
        logger.error(f'Permission denied reading file: {station_file}')
        raise
    except OSError as e:
        logger.error(f'OS error reading file {station_file}: {e}')
        raise
    logger.debug(f'Read {len(file_lines)} lines from {station_file}')
    if verbose:
        print(f'Read {len(file_lines):,} stations from {station_file}')

    mydict = {
        entry['STN_ID']: [entry['SITE_CODE'], entry['SWN']]
        for entry in csv.DictReader(file_lines, delimiter='\t')
    }

    lines_in, lines_out = 0, 0
    try:
        with open(waterlevel_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(
                'STN_ID,SITE_CODE,WLM_ID,MSMT_DATE,WLM_RPE,WLM_GSE,RDNG_WS,RDNG_RP,WSE,RPE_GSE,GSE_WSE,WLM_QA_DESC,WLM_DESC,WLM_ACC_DESC,WLM_ORG_ID,WLM_ORG_NAME,MSMT_CMT,COOP_AGENCY_ORG_ID,COOP_ORG_NAME\n'
            )
            for line in infile:
                lines_in = lines_in + 1
                items = line.split()
                if len(line) > 10:
                    value = mydict.get(items[0][0 : line.find(',')])
                    if value is not None:
                        outfile.write(line)
                        lines_out = lines_out + 1
    except FileNotFoundError:
        logger.error(f'File not found: {waterlevel_file}')
        raise
    except PermissionError:
        logger.error(f'Permission denied on file: {waterlevel_file} or {output_file}')
        raise
    except OSError as e:
        logger.error(f'OS error processing files {waterlevel_file} / {output_file}: {e}')
        raise
    logger.debug(f'Processed {lines_in} lines from {waterlevel_file}, wrote {lines_out} lines to {output_file}')
    if verbose:
        print(f'Processed {lines_in:,} lines from {waterlevel_file}')
        print(f'Wrote {lines_out:,} lines to {output_file}')
    return

if __name__ == '__main__':
    ' Run wdl_ts_4_wells() from command line'
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        station_file = sys.argv[1]
        waterlevel_file = sys.argv[2]
    else:  # ask for file names from terminal
        station_file = input('Well station file name: ')
        waterlevel_file   = input('Water level file name: ')

    iwfm.file_test(station_file)  
    iwfm.file_test(waterlevel_file)

    idb.exe_time()  # initialize timer
    iwfm.wdl_ts_4_wells(station_file, waterlevel_file, verbose=verbose)

    idb.exe_time()  # print elapsed time
