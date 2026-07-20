# cdec2monthly.py
# Read CDEC observations, convert sub-monthly observations to the monthly average
# and write to a csv file
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


'''Read a CDEC observations file, convert sub-monthly observations to the monthly average, and write to a csv file.'''

def cdec2monthly(input_file, output_file, verbose=False):
    '''Read a CDEC observations file, convert sub-monthly observations to the monthly average, and write to a csv file.

    Parameters
    ----------
    input_file: str
        Name of file containing CDEC-formatted observations

    output_file : str
        Name of output csv file with monthly values

    verbose : bool, default=False
       Turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import polars as pl

    # read csv and replace error codes with null
    flow_data = (
        pl.read_csv(input_file)
        .with_columns(
            pl.col('FLOW (CFS)')
            .str.replace_all(r'--|ARTN|BRTN|ART|BRT', '')
            .replace('', None)
            .cast(pl.Float64)
        )
        .with_columns(
            # combine DATE and TIME columns and parse as datetime
            (pl.col('DATE') + ' ' + pl.col('TIME (PST)'))
            .str.to_datetime('%m/%d/%Y %H:%M', strict=False)
            .alias('DATE'),
            (pl.col('FLOW (CFS)') * 1.983).alias('FLOW (AF)')
        )
        .drop_nulls(subset=['DATE'])  # remove rows with unparseable dates
    )

    # get daily mean values
    flow_daily = (
        flow_data
        .group_by_dynamic('DATE', every='1d')
        .agg(
            pl.col('FLOW (CFS)').mean(),
            pl.col('FLOW (AF)').mean()
        )
    )

    # aggregate to monthly sums
    flow_monthly = (
        flow_daily
        .group_by_dynamic('DATE', every='1mo')
        .agg(
            pl.col('FLOW (AF)').sum()
        )
    )

    # write to output file
    flow_monthly.select(['DATE', 'FLOW (AF)']).write_csv(output_file)

    if verbose:
        print(f'  Aggregated {input_file} to monthly flows and wrote to {output_file}')
    return


if __name__ == '__main__':
    ''' Run cdec2monthly() from command line '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:  # ask for file names from terminal
        input_file = input('CDEC daily data file name: ')
        output_file = input('Output monthly data file name: ')

    iwfm.file_test(input_file)

    idb.exe_time()  # initialize timer
    cdec2monthly(input_file, output_file)

    print('  Read {} and wrote {}'.format(input_file, output_file))  # update cli
    idb.exe_time()  # print elapsed time
