# lu2tables.py
# Read IWFM land use file and write to a separate file for each land use type
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

from iwfm.debug.logger_setup import logger

def lu2tables(land_use_file, output_file_type, verbose=False, debug=1):
    '''lu2tables() - Read an IWFM land use file and write contents to a 
       separate file for each land use type

    *** INCOMPLETE - UNDER DEVELOPMENT ***

    Parameters
    ----------
    land_use_file : str
        name of existing model land use file

    output_file_type : str
        type of output file to create

    verbose : bool, default=False
        turn command-line output on or off

    debug : bool, default=0
        turn additional command-line output on or off

    Returns
    -------
    nothing

    SUGGESTED FUTURE CHANGES:
      - include option for output file type i.e. type='dat' with options
            like 'csv', 'excel', 'dbf', etc

    '''
    import datetime
    import iwfm

    # find the base name and extension
    land_use_file_base = land_use_file[0 : land_use_file.find('.')]

    # -- SUGGESTED FUTURE CHANGES TO IMPROVE THIS PROGRAM --
    # -- read a cl value for output file type
    # -- allow multiple items: pop each item from arvg[] and process it
    # -- may need to add varnames i.e. '-ext=xlsx' or '--excel'
    # out_file_ext = 'dat'                 # default output
    # if len(sys.argv) > 2:                # If there is a value...
    #    cl_value = sys.argv[2]            # Read the debug value from command line
    # if cl_value == 'xls'||'xlsx' then call write_2_excel() to write

    if verbose:
        print(f'  Creating land use area tables from {land_use_file}')  

    try:
        with open(land_use_file, encoding='utf-8') as f:
            file_lines = f.read().splitlines()  # open input file
    except FileNotFoundError as e:
        logger.error(f'lu2tables: file not found {land_use_file}: {e}')
        raise
    except (PermissionError, OSError) as e:
        logger.error(f'lu2tables: failed to read {land_use_file}: {e}')
        raise

    # determine how many data lines per time step
    # Check lines starting at the bottom, find first line with length > 5
    # If there's a change something else is at the bottom,
    # then change to either skip_back(n) or test for int
    i = len(file_lines) - 1                         # start at the bottom# last line of file
    while i > 0 and len(file_lines[i]) < 5:         # find last line with data (skip empty lines)
        i -= 1

    # Check if we found a valid data line
    if i <= 0:
        msg = f'Could not find data lines in land use file {land_use_file}: all lines appear to be empty or too short (< 5 characters)'
        logger.error(f'lu2tables: {msg}')
        raise ValueError(msg)

    # the first item on this line is the largest element number
    last_data_line_no = i

    # move up the file to a line with a date, counting lines
    no_elems = 0          # will count elements as we go backwards
    # Count backwards until we find a line with a date (contains '/' and '_')
    while i > 0:
        first_field = file_lines[i].split()[0] if len(file_lines[i].split()) > 0 else ''
        if '/' in first_field and '_' in first_field:
            # Found a line with a date field (start of this time step)
            no_elems += 1  # Count this line too
            break
        no_elems += 1
        i -= 1

    # Check if we found a valid date line
    if i <= 0:
        msg = f'Could not find a date line in land use file {land_use_file}, searched from line {last_data_line_no} to line {i}'
        logger.error(f'lu2tables: {msg}')
        raise ValueError(msg)

    # determine number of time steps and crops
    # Find the first data line by searching for a line that starts with a date (MM/DD/YYYY_HH:MM)
    line_index = 0
    while line_index < len(file_lines):
        stripped = file_lines[line_index].strip()
        # Check if line starts with a date pattern (at least 2 slashes and underscore for time)
        if (len(stripped) > 0 and stripped[0].isdigit() and
            stripped.count('/') >= 2 and '_' in stripped):
            # Verify it looks like a date by checking first field
            first_field = stripped.split()[0] if len(stripped.split()) > 0 else ''
            if '/' in first_field and '_' in first_field:
                # Found a line that starts with a date in DSS format
                break
        line_index += 1

    if line_index >= len(file_lines):
        msg = f'Could not find the start of data in land use file {land_use_file}: expected a line starting with a date (MM/DD/YYYY_HH:MM)'
        logger.error(f'lu2tables: {msg}')
        raise ValueError(msg)

    no_time_steps = int((last_data_line_no - line_index)/no_elems + 1)
    no_crops = (len(file_lines[line_index].split()) - 2)  # number of crops/land use types (subtract date and element number)

    dates = ['' for x in range(no_time_steps)]  # empty list

    # get list of element numbers
    elem_list, ts_line_index, l_index = [], 0, line_index
    first_data_line = line_index  # Save the position of the first data line
    while ts_line_index < no_elems:  # iterate through each element
        this_line = file_lines[l_index].split()  # line to list
        if (ts_line_index == 0):  # first line has an extra item, the date in DSS format
            date = this_line.pop(0)  # remove the date
        elem = int(this_line.pop(0))  # get the element number
        elem_list.append(elem)
        ts_line_index += 1
        l_index += 1

    # create empty 3D list for data
    data = [[['0' for z in range(no_time_steps)] for y in range(no_elems)] for x in range(no_crops) ]  # empty array

    # Reset line_index to the start of the data for the main loop
    line_index = first_data_line
    ts_index = 0
    # fill the data and years arrays
    while ts_index < no_time_steps:  # iterate through each time step
        ts_line_index = 0
        while ts_line_index < no_elems:  # iterate through each element
            this_line = file_lines[line_index].split()  # line to list
            if (ts_line_index == 0):  # first line has an extra item, the date in DSS format
                import iwfm
                date = this_line.pop(0)  # Get the date
                try:
                    month, day, year, hr, minute = iwfm.validate_dss_date_format(date, f'line {line_index+1} date')
                except ValueError as e:
                    raise ValueError(f"Error parsing DSS date at line {line_index+1}: {str(e)}") from e

                # DSS midnight = '24', datetime midnight = 0
                if hr == 24:
                    hr = 0

                dates[ts_index] = datetime.datetime(year, month, day, hr, minute)
            elem = int(this_line.pop(0))  # pop the element number
            for crop in range(0, no_crops):
                data[crop][ts_line_index][ts_index] = this_line[crop]  # assign values to data array
            ts_line_index += 1
            line_index += 1
            # ----- end of (while ts_line_index) loop -----
        ts_index += 1
        # ----- end of (while ts_index) loop -----

    # write to text files
    crops = [x+1 for x in range(no_crops)]  # integer crop numbers

    if output_file_type == 'csv':
        iwfm.write_2_csv(land_use_file_base, data, crops, elem_list, no_time_steps, dates)
        if verbose:
            print(f'  Wrote land use area tables to {land_use_file_base}_*.csv')
    else:   # default to 'dat'
        iwfm.write_2_dat(land_use_file_base, data, crops, elem_list, no_time_steps, dates)
        if verbose:
            print(f'  Wrote land use area tables to {land_use_file_base}_*.dat')

    # Future: write to excel workbook
    # write_2_excel(land_use_file_base,data,crops,max_elem,time_steps,dates)
    # if verbose:
    #  print('  Wrote land use area tables to {}.xlsx'.format(land_use_file_base))

    logger.debug(f'lu2tables: processed {land_use_file} with {no_crops} crops, {no_elems} elements, {no_time_steps} time steps')

    return


if __name__ == '__main__':
    ''' Run lu2tables() from command line 

    SUGGESTED FUTURE CHANGES TO IMPROVE THIS PROGRAM
      - allow multiple items: pop each item from arvg[] and process it

    '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    output_file_type = 'dat'  # default output file type
    if len(sys.argv) > 1:  # arguments are listed on the command line
        input_file = sys.argv[1]
        if len(sys.argv) > 2:  # output file tupe listed on command line
            output_file_type = sys.argv[2]
    else:  # ask for file names from terminal
        input_file = input('IWFM Land use file name: ')

    iwfm.file_test(input_file)

    idb.exe_time()  # initialize timer
    lu2tables(input_file, output_file_type, verbose=verbose)

    idb.exe_time()  # print elapsed time
