# iwfm_read_elempump.py
# read IWFM Simulation Element Pumping file
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


'''Read an IWFM Element Pumping file, and return lists for ICOLSK, FRACSK, IOPTSK, FRACSKL[Layer], TYPDSTSK, DSTSK, ICFIRIGSK, ICACJSK, ICSKMAX and FSKMAX for Ag and for Urban for each model element.'''

def iwfm_read_elempump(elempump_file_name, elem_ids, ag=1, ur=2, comment=0, verbose=False):
    '''Read an IWFM Element Pumping file, and return lists for ICOLSK, FRACSK, IOPTSK, FRACSKL[Layer], TYPDSTSK, DSTSK, ICFIRIGSK, ICACJSK, ICSKMAX and FSKMAX for Ag and for Urban for each model element.

    Parameters
    ----------
    elem_ids : list
        element IDs

    elempump_file_name : str
        IWFM Elemental Pumping file name

    ag : int, default = 1
        Ag value in icfirigsk field

    ur : int, default = 2
        Urban value in icfirigsk field

    comment : int, default = 0
        How many comment fields on each line?

    verbose : bool, default = False
        Print status messages

    Returns
    -------
    elempump_ag and elempump_ur : lists of lists
        containing lists of length elements:
            id : element number, int
            icolsk : Time Series Pumping File data column, int
            fracsk : Fraction of icolsk, float
            ioptsk : Pumping distribution flag, int
            typdstsk : Delivery destination type, int
            dstsk : Delivery destination ID, int
            icfirigsk : Irrigation Fractsions Data File column, int
            icacjsk : Supply Adjustment Data Column, int
            icskmax : Time Series Pumping Data Column containing maximum pumping, int
            fskmax : fraction of icskmax data value, float
            fracskl[layers] : list of lists of length elements

    header : list
        list of column headers
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from iwfm.debug.logger_setup import logger

    iwfm.file_test(elempump_file_name)
    try:
        with open(elempump_file_name, encoding='utf-8') as f:
            elempump_lines = f.read().splitlines()
    except FileNotFoundError:
        logger.error(f'File not found: {elempump_file_name}')
        raise
    except PermissionError:
        logger.error(f'Permission denied reading file: {elempump_file_name}')
        raise
    except OSError as e:
        logger.error(f'OS error reading file {elempump_file_name}: {e}')
        raise
    logger.debug(f'Read {len(elempump_lines)} lines from {elempump_file_name}')

    pump_lines, line_index = read_next_line_value(elempump_lines, -1, column=0)
    pump_lines = int(pump_lines)  # number of lines of pumping data

    _, line_index = read_next_line_value(elempump_lines, line_index, column=0)  

    layers = len(elempump_lines[line_index].split('\t')) - 10 - comment     # number of layers in the model
    
    elempump_init = [0 for i in range(10 + layers)]                                  # initialize lists

    elempump_ag = [elempump_init for i in elem_ids]                         # initialize lists
    elempump_ur = [elempump_init for i in elem_ids]                         # initialize lists
    elempump_other = [elempump_init for i in elem_ids]                      # initialize lists

    header = ['active','icolsk','fracsk','ioptsk','typdstsk','dstsk','icfirigsk','icacjsk','icskmax','fskmax']
    for i in range(0, layers):
        header.append(f'fracskl_{i+1}')

    for i in range(0, pump_lines):
        try:
            l = elempump_lines[line_index + i].split('\t')
            params, fracs, temp = [], [], [s for s in l[:-1]]
            elem_id = int(temp[0])-1

            params.append(int(temp.pop(0))) # active
            params.append(int(float(temp.pop(0)))) # icolsk
            params.append(float(temp.pop(0))) # fracsk
            if params[2] == 0:
                params[0]=0
            else:
                params[0]=1
            params.append(int(float(temp.pop(0)))) # ioptsk

            for j in range(0, layers):                  # fracskl in middle, collect and move to end
                fracs.append(float(temp.pop(0)))

            params.append(int(float(temp.pop(0)))) # typdstsk
            params.append(int(float(temp.pop(0)))) # dstsk
            params.append(int(float(temp.pop(0)))) # icfirigsk
            params.append(int(float(temp.pop(0)))) # icacjsk
            params.append(int(float(temp.pop(0)))) # icskmax
            params.append(float(temp.pop(0))) # fskmax

            for j in range(0, layers):                  # fracskl at end
                params.append(fracs.pop(0))

            ag_ur = params[6]                           # icfirigsk - destination type (1=ag, 2=urban)

            if ag_ur == ag:
                elempump_ag[elem_id] = params
            elif ag_ur == ur:
                elempump_ur[elem_id] = params
            else:
                elempump_other[elem_id] = params
        except (ValueError, IndexError) as e:
            logger.error(f'Error on line {line_index + i + 1} of {elempump_file_name}:')
            logger.error(f'Line content: {elempump_lines[line_index + i]}')
            logger.error(f'Error: {e}')
            logger.error(f'Parsed fields: {l}')
            raise

    return elempump_ag, elempump_ur, elempump_other, header


if __name__ == "__main__":
    ''' Run iwfm_read_elempump() from command line '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        elempump_file_name = sys.argv[1]
        elem_file_name     = sys.argv[2]
    else:  # ask for file names from terminal
        elempump_file_name = input('IWFM Element Pumping file name: ')
        elem_file_name     = input('IWFM Elements file name: ')

    iwfm.file_test(elempump_file_name)
    iwfm.file_test(elem_file_name)

    idb.exe_time()                                                                                        # initialize timer

    elem_ids, elem_nodes, elem_sub = iwfm.iwfm_read_elements(elem_file_name)                              # Read element file

    elempump_ag, elempump_ur, elempump_other, header = iwfm_read_elempump(elempump_file_name, elem_ids, comment=1, verbose=False)  # Read element pumping file

    # write results to text file
    elempump_ag_file = elempump_file_name.split('.')[0] + '_ag.txt'
    with open(elempump_ag_file, 'w', encoding='utf-8') as f:
        f.write(f'{header}\n')
        for i in range(0, len(elempump_ag)):
            f.write(f'{elempump_ag[i]}\n')
    print(f'  Created {elempump_ag_file} with agricultural elemental pumping')

    elempump_ur_file = elempump_file_name.split('.')[0] + '_urban.txt'
    with open(elempump_ur_file, 'w', encoding='utf-8') as f:
        f.write(f'{header}\n')
        for i in range(0, len(elempump_ur)):
            f.write(f'{elempump_ur[i]}\n')
    print(f'  Created {elempump_ur_file} with urban elemental pumping')

    elempump_other_file = elempump_file_name.split('.')[0] + '_other.txt'
    with open(elempump_other_file, 'w', encoding='utf-8') as f:
        f.write(f'{header}\n')
        for i in range(0, len(elempump_other)):
            f.write(f'{elempump_other[i]}\n')
    print(f'  Created {elempump_other_file} with other elemental pumping')

    idb.exe_time()                                                                                        # print elapsed time
