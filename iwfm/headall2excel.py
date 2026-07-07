# headall2excel.py
# Write out IWFM Headall.out data for selected time steps to
# an excel workbook, one sheet per time step
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

class _Worksheet:
    ''' Worksheet with a write(row, col, value) method
        (0-based row/column indices). '''

    def __init__(self, ws):
        self._ws = ws

    def write(self, row, col, value):
        self._ws.cell(row=row + 1, column=col + 1, value=value)


class _Workbook:
    ''' Workbook where add_worksheet() creates a named sheet and
        close() saves to the file name given at construction. '''

    def __init__(self, filename):
        import openpyxl

        self._wb = openpyxl.Workbook()
        self._wb.remove(self._wb.active)  # drop the default empty sheet
        self._filename = filename

    def add_worksheet(self, name):
        return _Worksheet(self._wb.create_sheet(title=name))

    def close(self):
        if not self._wb.sheetnames:  # openpyxl cannot save a sheetless workbook
            self._wb.create_sheet(title='Sheet1')
        self._wb.save(self._filename)


def new_excel(outfile_name, verbose=False):
    ''' new_excel() - Create a new Excel workbook

    Parameters
    ----------
    outfile_name : str
        Output Excel file name (written when the workbook is closed)

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    workbook : object
        Excel workbook object with add_worksheet() and close() methods

    '''
    workbook = _Workbook(outfile_name)

    if verbose: print(f'  Created Excel workbook {outfile_name}')

    return workbook


def headall2excel(node_coords, data, dates, out_dates, outfile_name, verbose=False):
    ''' headall2excel() - Write out IWFM Headall.out data for selected time steps to
        an excel workbook, one sheet per time step

    Parameters
    ----------
    node_coords: list
        (x,y) coordinates of nodes
    
    data : list
        numpy array of floats, size nodes x layers
    
    dates : list
        list of simulated head dates
    
    out_dates: list
        dates for output
    
    outfile_name : str
        output excel file name
    
    verbose : bool, default=False
        True = command-line output on
    
    Return
    ------
    count : int
        Number of output files written
    
    '''
    count = 0

    # create new excel workbook
    workbook = new_excel(outfile_name, verbose=True)

    worksheets=[]

    for i in range(0, len(dates)): 
        if dates[i] in out_dates:
            tab_name = dates[i].replace('/','_')

            # create excel worksheet with name tab_name after last sheet
            wksheet = workbook.add_worksheet(tab_name)
            worksheets.append(wksheet)  # for future reference if needed

            # write node_coords to worksheet
            wksheet.write(0, 0, 'NodeID')
            wksheet.write(0, 1, 'X')
            wksheet.write(0, 2, 'Y')

            for j in range(0, len(node_coords)):
                wksheet.write(j + 1, 0, node_coords[j][0])
                wksheet.write(j + 1, 1, node_coords[j][1])
                wksheet.write(j + 1, 2, node_coords[j][2])

            # write data to worksheet
            for j in range(0, len(data[i])):
                wksheet.write(0, 3 + j, 'Layer '+ str(j + 1))

            for col_num, item in enumerate(data[i]):
                for row_num, cell in enumerate(item):
                    wksheet.write(row_num + 1, col_num + 3, cell)

            count += 1
            if verbose: print(f'  Added {dates[i]}')

    # save and close workbook
    workbook.close()

    return count


if __name__ == '__main__':
    ' Run headall2excel() from command line '
    import sys
    import os
    import iwfm
    import iwfm.debug as dbg
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    
    args = sys.argv[1:]  # get command line arguments
    if len(sys.argv) > 1:  # arguments are listed on the command line
        heads_file, pre_file, outfile_name, out_dates_file = args
    else:  # ask for file names from terminal
        heads_file     = input('IWFM Headall file name: ')
        pre_file       = input('IWFM Preprocessor main file name: ')
        outfile_name    = input('Output file rootname: ')
        out_dates_file = input('Output dates file name: ')

    iwfm.file_test(heads_file)
    iwfm.file_test(pre_file)
    iwfm.file_test(out_dates_file)

    # if outfile_name extension != '.xlsx' add '.xlsx'
    if outfile_name[-5:] != '.xlsx':
        outfile_name += '.xlsx'

    dbg.exe_time()  # initialize timer

    data, layers, dates, nodes = iwfm.headall_read(heads_file)

    # read dates to create ooutput files for
    with open(out_dates_file) as f:
        date_lines = f.read().splitlines() 
    out_dates = [line for line in date_lines]

    # get preprocessor file names
    pre_path, pre_proc = os.path.split(pre_file)
    pre_files, _ = iwfm.iwfm_read_preproc(pre_file)

    # read preprocessor node file
    node_file = os.path.join(pre_path, pre_files.node_file)
    node_coords, node_list, factor = iwfm.iwfm_read_nodes(node_file)

    # multiply noode_coords X and Y by factor
    for i in range(0, len(node_coords)):
        node_coords[i][1] *= factor
        node_coords[i][2] *= factor

    count = headall2excel(node_coords, data, dates, out_dates, outfile_name, verbose=verbose)

    print(f'  Created {outfile_name} with {count} worksheets.')

    dbg.exe_time()  # print elapsed time
