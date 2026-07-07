# tables2lu.py
# Read individual tables of elemental land use data and write 
# to a single IWFM land use file
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

def tables2lu(header, template_lines, initial_acreage, factor_tables, output_file_name, start_date, elems):
    '''tables2lu() - Read an IWFM land use file and write contents to a 
       separate file for each land use type

    Parameters
    ----------
    header : list
        header lines of the IWFM land use file

    template_lines : list
        template lines of the IWFM land use file

    initial_acreage : list
        initial crop acreages

    factor_tables : list
        tables of crop acreage multipilers for each year

    output_file_name : str
        output file name

    start_date : str
        date of initial land use data in DSS format

    elems : list
        element numbers

    Returns
    -------
    nothing


    '''

    month_day = start_date[0:5]
    start_year = int(start_date[6:10])

    # open output_file_name for writing inside with loop
    line_count = 0
    try:
        with open(output_file_name, 'w', encoding='utf-8') as fp:

            # write the header to the output file
            for line in header:
                fp.write(f'{line}\n')
                line_count += 1

            # if template_lines contain data, write the template lines to the output file
            if len(template_lines) > 0:
                for line in template_lines:
                    fp.write(f'{line}\n')
                    line_count += 1

            for i in range(len(factor_tables)):
                year = start_year + i + 1               # calculate the year from start_year
                if year != start_year:                  # skip because we already wrote the initial acreage
                    date = month_day + '/' + str(year) + '_24:00'

                    # multiply initial_acreage by factor_tables[i]
                    new_acreage = []
                    for row in range(0, len(initial_acreage)):
                        new_acreage.append([round(initial_acreage[row][j] * factor_tables[i][row][j],2) for j in range(0,len(initial_acreage[row]))])

                    for j in range(0, len(new_acreage)):
                        if j == 0:
                            fp.write(f'{date}\t{elems[j]}\t' + '\t'.join([str(x) for x in new_acreage[j]]) + '\n')
                        else:
                            fp.write(f'\t{elems[j]}\t' + '\t'.join([str(x) for x in new_acreage[j]]) + '\n')
                        line_count += 1
    except (PermissionError, OSError) as e:
        logger.error(f'tables2lu: failed to write {output_file_name}: {e}')
        raise

    logger.debug(f'tables2lu: wrote {line_count} lines to {output_file_name}')

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

    args = sys.argv[1:]  # get command line arguments
    if len(sys.argv) > 1:  # arguments are listed on the command line
        template_file_name, input_file, output_file_name = args
    else:  # ask for file names from terminal
        template_file_name = input('IWFM Land use file name: ')
        input_file         = input('Text file containing input file names: ')
        output_file_name   = input('Output file name: ')

    iwfm.file_test(template_file_name)
    iwfm.file_test(input_file)

    idb.exe_time()  # initialize timer

    # open and read template file
    with open(template_file_name, encoding='utf-8') as f:
        template_lines = f.read().splitlines()

    # copy header to variable with the same name
    t_line = 0
    while template_lines[t_line][0] == 'C':
        t_line += 1
    t_line += 4             # skip the Land USe Data Specification lines
    while template_lines[t_line][0] == 'C':
        t_line += 1
    header = template_lines[0:t_line]
    template_lines = template_lines[t_line:]

    # extract starting date, element numbers, and initial crop acreages
    # from the template file
    elems, initial_acreage = [], []
    for line in template_lines:
        line = line.split('\t')
        if len(elems) == 0:
            start_date = line.pop(0)
        else:
            t = line.pop(0)     # discard empty string
        elems.append(int(line.pop(0)))
        ac = []
        for item in line:
            ac.append(float(item))
        initial_acreage.append(ac)

    # open and read factor files listed in input file
    with open(input_file, encoding='utf-8') as f:
        input_files = f.read().splitlines()
    input_tables = []
    for file in input_files:
        iwfm.file_test(file)
        with open(file, encoding='utf-8') as f:
            in_lines = f.read().splitlines()
        table = []
        for line in in_lines:
            new_line = line.split(',')
            if len(table) == 0:
                for i in range(1, len(new_line)):
                    new_line[i] = int(new_line[i])
            else:
                new_line[0] = int(new_line[0])            
                for i in range(1, len(new_line)):
                    new_line[i] = float(new_line[i])
            table.append(new_line)
        input_tables.append(table)

    # use input_tables to create factor_tables
    years = [int(input_tables[0][0][i]) for i in range(1, len(input_tables[0][0]))]     # get years from first input_tables table
    elements = [int(input_tables[0][i][0]) for i in range(1, len(input_tables[0]))]     # get elements from first input_tables table

    ncrops = len(input_tables)

    factor_tables = []
    for year in range(0, len(years)):
        factors = []
        for row in range(0, len(elements)):
            row_factors = []
            for crop in range(0, ncrops):
                row_factors.append(input_tables[crop][row+1][year+1])
            factors.append(row_factors)
        factor_tables.append(factors)

    tables2lu(header, template_lines, initial_acreage, factor_tables, output_file_name, start_date, elems)

    idb.exe_time()  # print elapsed time
