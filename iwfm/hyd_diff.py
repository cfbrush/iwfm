# hyd_diff.py
# Subtract the values in one hydrograph file from another
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


def hyd_diff(gwhyd_file_1, gwhyd_file_2, outname):
    ''' hyd_diff() - Subtract the values in one hydrograph file from another

    Parameters
    ----------
    gwhyd_file_1 : str
        name of IWFM hydrograph file to subtract from

    gwhyd_file_2 : str
        name of IWFM hydrograph file to subtract

    outname : str
        output file base name

    Return
    ------
    nothing

    '''

    import iwfm
    from iwfm.debug.logger_setup import logger

    iwfm.file_test(gwhyd_file_1)
    try:
        with open(gwhyd_file_1, encoding='utf-8') as f:
            gwhyd_lines_1 = (f.read().splitlines())
    except FileNotFoundError:
        logger.error(f'File not found: {gwhyd_file_1}')
        raise
    except PermissionError:
        logger.error(f'Permission denied reading file: {gwhyd_file_1}')
        raise
    except OSError as e:
        logger.error(f'OS error reading file {gwhyd_file_1}: {e}')
        raise
    logger.debug(f'Read {len(gwhyd_lines_1)} lines from {gwhyd_file_1}')

    iwfm.file_test(gwhyd_file_2)
    try:
        with open(gwhyd_file_2, encoding='utf-8') as f:
            gwhyd_lines_2 = (f.read().splitlines())
    except FileNotFoundError:
        logger.error(f'File not found: {gwhyd_file_2}')
        raise
    except PermissionError:
        logger.error(f'Permission denied reading file: {gwhyd_file_2}')
        raise
    except OSError as e:
        logger.error(f'OS error reading file {gwhyd_file_2}: {e}')
        raise
    logger.debug(f'Read {len(gwhyd_lines_2)} lines from {gwhyd_file_2}')

    gwhyd_lines_out = gwhyd_lines_1[0:9]

    for i in range(9, len(gwhyd_lines_1)):
      temp1 = gwhyd_lines_1[i].split()
      temp2 = gwhyd_lines_2[i].split()
      as_str = temp1[0] + '           '
      for j in range(1,len(temp1)):
        as_str += str(round(float(temp1[j]) - float(temp2[j]),4)).ljust(16)  # left-justify to 16 chars
      gwhyd_lines_out.append(as_str)

    try:
        with open(outname, 'w', encoding='utf-8') as f:
          for line in gwhyd_lines_out:
            f.write("%s\n" % line )
    except PermissionError:
        logger.error(f'Permission denied writing file: {outname}')
        raise
    except OSError as e:
        logger.error(f'OS error writing file {outname}: {e}')
        raise
    logger.debug(f'Wrote {len(gwhyd_lines_out)} lines to {outname}')

    return

if __name__ == '__main__':
    ' Run hyd_diff() from command line '
    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
      gwhyd_file_1 = sys.argv[1] 
      gwhyd_file_2 = sys.argv[2] 
      outname      = sys.argv[3]  

    else:  # get everything form the command line
      gwhyd_file_1 = input('Base IWFM hydrograph file name: ')
      gwhyd_file_2 = input('Comparison IWFM hydrograph file name: ')
      outname      = input('Output hydrograph file name: ')

    # test that the input files exist
    iwfm.file_test(gwhyd_file_1)
    iwfm.file_test(gwhyd_file_2)

    idb.exe_time()  # initialize timer
    hyd_diff(gwhyd_file_1, gwhyd_file_2, outname)
    print(f'  Created hydrograph file {outname}')  # update cli
    idb.exe_time()  # print elapsed time
