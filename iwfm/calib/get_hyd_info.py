# get_hyd_info.py
# unpack control variables from file_dict for one hydrograph type
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


def get_hyd_info(ftype,file_dict,model_dir=''):
    ''' get_hyd_info() - unpack control variables from file_dict for one hydrograph type

    Parameters
    ----------
    ftype : str
        IWFM input file type

    file_dict : dictionary
        information for ftypes

    model_dir : str, default=''
        directory containing the model files, prepended to relative paths
        read from inside the IWFM files

    Returns
    -------
    hyd_file : str
        hydrograph file name

    hyd_names : list
        hydrograph names

    '''

    import os
    import iwfm
    from iwfm.file_utils import read_next_line_value

    main_file = file_dict[ftype][0]   # IWFM input file
    colid     = file_dict[ftype][8]   # col no of observation site name
    skips     = file_dict[ftype][9]   # lines to skip, different for each ftype
    logger.debug(f'get_hyd_info({ftype}): main_file={main_file}, colid={colid}, skips={skips}')

    iwfm.file_test(main_file)
    with open(main_file, encoding='utf-8') as f:
        in_lines = f.read().splitlines()                      # open and read input file
    line_index = 5  # skip first few lines
    logger.debug(f'  Read {len(in_lines):,} lines from {main_file}')

    if ftype == 'Tile drains':
        # -- the first part of the tile drain file is different
        td_no_str, line_index = read_next_line_value(in_lines, line_index - 1, column=0)
        td_no = int(td_no_str)                                # no. tile drain param rows
        # skip tile drain parameters + 3 lines
        _, line_index = read_next_line_value(in_lines, line_index - 1, skip_lines=td_no + 3)
        sd_no_str, line_index = read_next_line_value(in_lines, line_index - 1, column=0, skip_lines=1)
        sd_no = int(sd_no_str)                                # no. subsurface irrigation points
        # skip subsurface irrigation params + 4 lines
        _, line_index = read_next_line_value(in_lines, line_index - 1, skip_lines=sd_no + 4)
        logger.debug(f'  Tile drains: td_no={td_no}, sd_no={sd_no}, line_index={line_index}')
    elif ftype == 'Groundwater':
        # IWFM groundwater files vary between versions (optional IHTPFLAG,
        # KDEB, etc.), so search for the / NOUTH marker instead of using a
        # fixed skip count.
        found = False
        for i, line in enumerate(in_lines):
            if '/ NOUTH' in line:
                line_index = i
                found = True
                break
        if not found:                                                    # fallback to skip count
            _, line_index = read_next_line_value(in_lines, line_index - 1, skip_lines=skips[0])
            logger.debug(f'  Groundwater: NOUTH marker not found, used skip count, line_index={line_index}')
        else:
            logger.debug(f'  Groundwater: found NOUTH marker at line {line_index}')
    else:
        # -- Streams, Subsidence, and other types
        _, line_index = read_next_line_value(in_lines, line_index - 1, skip_lines=skips[0])
        logger.debug(f'  {ftype}: skipped {skips[0]} lines, line_index={line_index}')

    # -- get NOUT - number of hydrographs
    nout = int(in_lines[line_index].split()[0])
    logger.info(f'  {ftype}: {nout:,} hydrographs (NOUT)')

    # -- get hydrographs output file name
    hyd_file_raw, line_index = read_next_line_value(in_lines, line_index - 1, column=0, skip_lines=skips[1])
    hyd_file = hyd_file_raw.replace('\\', os.sep)
    if model_dir:
        hyd_file = os.path.normpath(os.path.join(model_dir, hyd_file))
    logger.info(f'  {ftype}: hydrograph output file: {hyd_file}')
    if not os.path.isfile(hyd_file):                                    # test for input file
        logger.error(f'  {ftype}: hydrograph file not found: {hyd_file}')
        iwfm.file_missing(hyd_file)                                     # stop

    # -- get hydrograph names and locations as list
    hyd_names = []
    for i in range(0, nout):
        name, line_index = read_next_line_value(in_lines, line_index - 1, column=colid, skip_lines=1)
        hyd_names.append(name)
    logger.debug(f'  {ftype}: read {len(hyd_names):,} hydrograph names')

    return hyd_file, hyd_names
