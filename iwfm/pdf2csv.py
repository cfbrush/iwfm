# pdf2csv.py
# Read a PDF file and write tables to a csv file
# info and gwhyd_sim columns, and returns the dictionary
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


'''Read a PDF file and write tables to a csv file.'''

def pdf2csv(input_file, output_file, verbose=False, log_file='pdf2csv.log'):
    '''Read a PDF file and write tables to a csv file.

    Parameters
    ----------
    input_file : str
        name of input PDF file

    output_file : str
        name of output csv file

    verbose : bool, default=False
        turn command-line output on or off

    log_file : str, default='pdf2csv.log'
        name of log file for warnings and errors

    Returns
    -------
    nothing
    '''
    from tabula.io import convert_into
    import warnings
    import logging

    # Set up logging
    logging.basicConfig(
        filename=log_file,
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        try:
            convert_into(input_file, output_file, output_format='csv', pages='all')

            # Log any warnings
            for warning in w:
                logging.warning(f'{warning.category.__name__}: {warning.message}')

        except ImportError as e:
            if 'jpype' in str(e):
                logging.warning(f'JPype import failed: {e}. Falling back to subprocess mode.')
            else:
                raise
        except Exception as e:
            logging.error(f'Error converting {input_file}: {e}')
            raise

    if verbose:
        print(f'  Wrote table(s) in {input_file} to {output_file}')
    return


if __name__ == '__main__':
    ' Run pdf2csv() from command line '
    import sys
    import os
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        input_file = sys.argv[1]
    else:  # ask for file names from terminal
        input_file = input('PDF file name: ')

    iwfm.file_test(input_file)

    output_file = os.path.splitext(input_file)[0] + '.csv'  # filename without extension

    idb.exe_time()  # initialize timer
    pdf2csv(input_file, output_file, verbose=verbose)  
    idb.exe_time()  # print elapsed time
