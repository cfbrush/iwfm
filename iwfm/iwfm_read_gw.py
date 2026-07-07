# iwfm_read_gw.py
# read IWFM simulation groundwater file for file names
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


def get_name(s):
    ''' get_name() - Read an IWFM Simulation Groundwater file and return
        a dictionary of sub-process file names, and arrays of parameters

    Parameters
    ----------
    s : str
        line from IWFM Simulation Groundwater file

    Returns
    -------
    name : string
        if file name: Groundwater sub-process file name
        if blank, 'none'
    '''

    temp = s.split()[0]
    if temp[0] == '/':   # check for presence of file name
        name = 'none'
    else:
        name = temp
    return name


def iwfm_read_gw(gw_file, verbose=False):
    ''' iwfm_read_gw() - Read an IWFM Simulation Groundwater file and return
        a dictionary of sub-process file names, and arrays of parameters

    Parameters
    ----------
    gw_file : str
        IWFM Simulation Groundwater file name

    Returns
    -------
    gw_files : GroundwaterFiles
        Groundwater sub-process file names

    node_id : list
        node numbers

    layers : int
        number of layers

    Kh : list
        hydraulic conductivity

    Ss : list
        specific storage

    Sy : list
        specific yield

    Kq : list
        horizontal anisotropy ratio

    Kv : list
        vertical anisotropy ratio

    init_cond : list
        initial groundwater heads

    units : list
        time units for Kh, Kv, and Ss

    hydrographs : dict
        dictionary mapping well_name to (order, layer, x, y)
        order: 1-based column index in hydrograph output
        layer: aquifer layer number
        x, y: coordinates (scaled by factxy)

    factxy : float
        (X,Y) scale factor for hydrographs
                
    '''
    import iwfm
    import numpy as np
    import re
    from iwfm.file_utils import read_next_line_value
    from iwfm.iwfm_dataclasses import GroundwaterFiles

    iwfm.file_test(gw_file)

    comments = 'Cc*#'

    with open(gw_file, encoding='utf-8') as f:
        file_lines = f.read().splitlines()

    # get sub-process file names (or 'none' if not present)
    _, line_index = read_next_line_value(file_lines, 0, column=0)
    bc_file = get_name(file_lines[line_index])

    line_index += 1
    drain_file = get_name(file_lines[line_index])

    line_index += 1
    pump_file = get_name(file_lines[line_index])

    line_index += 1
    subs_file = get_name(file_lines[line_index])

    line_index += 10
    headall = get_name(file_lines[line_index])

    # Read past output file options to find NOUTH
    # The number of lines between headall and NOUTH varies by IWFM version
    # (some files include IHTPFLAG, others don't), so read line by line
    # and look for the NOUTH value by scanning ahead for the / NOUTH comment
    htpoutfl_str, line_index = read_next_line_value(file_lines, line_index, column=0)  # HTPOUTFL
    vtpoutfl_str, line_index = read_next_line_value(file_lines, line_index, column=0)  # VTPOUTFL
    gwbudfl_str, line_index = read_next_line_value(file_lines, line_index, column=0)   # GWBUDFL
    zbudfl_str, line_index = read_next_line_value(file_lines, line_index, column=0)    # ZBUDFL
    fngwfl_str, line_index = read_next_line_value(file_lines, line_index, column=0)    # FNGWFL

    # Check for optional IHTPFLAG line (present in newer IWFM versions)
    # Then KDEB, then NOUTH. Read lines until we find one tagged with / NOUTH
    # or that appears to be the NOUTH line.
    # Strategy: read the next non-comment line. If it's followed by FACTXY and
    # GWHYDOUTFL, it's NOUTH. Otherwise, it's IHTPFLAG or KDEB — keep reading.
    _, line_index = read_next_line_value(file_lines, line_index, column=0)
    # Read remaining lines between FNGWFL and NOUTH by checking for NOUTH marker
    while line_index < len(file_lines):
        line_text = file_lines[line_index]
        # Check if the line after this one (skipping comments) contains FACTXY
        # which would confirm this line is NOUTH
        peek_idx = line_index + 1
        while peek_idx < len(file_lines) and file_lines[peek_idx].strip() and \
              file_lines[peek_idx].strip()[0] in comments:
            peek_idx += 1
        if peek_idx < len(file_lines) and 'FACTXY' in file_lines[peek_idx].upper():
            break
        # Also check inline comment for NOUTH
        if 'NOUTH' in line_text.upper():
            break
        # Not NOUTH yet, advance to next non-comment line
        _, line_index = read_next_line_value(file_lines, line_index, column=0)

    nouth = int(file_lines[line_index].split()[0])             # number of hydrograph locations

    factxy_str, line_index = read_next_line_value(file_lines, line_index, column=0)
    factxy = float(factxy_str)                                 # (X,Y) scale factor

    gwhyd_str, line_index = read_next_line_value(file_lines, line_index, column=0)
    # gwhyd output file name is parsed but not included in GroundwaterFiles

    # hydrographs - build dictionary: {well_name: (order, layer, x, y)}
    # IHYDTYP == 0: ID  HYDTYP  LAYER  X  Y  NAME  (6 fields)
    # IHYDTYP == 1: ID  HYDTYP  LAYER  NODE_NO  NAME  (5 fields)
    _, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=1)
    hydrographs = {}
    for i in range(nouth):
        if re.search(file_lines[line_index].split()[0], comments):
            line_index += 1   # if line starts with comment character, skip it
        fields = file_lines[line_index].split()
        order = int(fields[0])
        hydtyp = int(fields[1])
        layer = int(fields[2])
        if hydtyp == 0:
            # ID  HYDTYP  LAYER  X  Y  NAME
            x = float(fields[3])
            y = float(fields[4])
            name = fields[5] if len(fields) > 5 else f"Well_{order}"
        else:
            # ID  HYDTYP  LAYER  NODE_NO  NAME
            x = 0.0
            y = 0.0
            name = fields[4] if len(fields) > 4 else f"Well_{order}"
        hydrographs[name] = (order, layer, x, y)
        line_index += 1
    logger.debug(f'{gw_file} has {nouth} hydrograph(s)')

    # element face flow - skip
    _, line_index = read_next_line_value(file_lines, line_index - 1, column=0)
    noutf = int(file_lines[line_index].split()[0])                      # Element Face Flow lines
    logger.debug(f'{gw_file} has {noutf} face flow line(s)')
    _, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=noutf + 2)

    logger.debug(f'file_lines[{line_index}] = {file_lines[line_index]}')
    ngroup = int(file_lines[line_index].split()[0])                      # skip to Parameter Groups

    logger.debug(f'{gw_file} has {ngroup} parameter group(s)')

    _, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=2)
    logger.debug(f'file_lines[{line_index}] = {file_lines[line_index]}')

    # units
    tunitkh = file_lines[line_index].split()[0]                         # time unit for aquifer Kh
    line_index += 1
    logger.debug(f'{tunitkh=}')
    tunitv = file_lines[line_index].split()[0]                          # time unit for aquitard Kv
    line_index += 1
    logger.debug(f'{tunitv=}')
    tunitl = file_lines[line_index].split()[0]                          # time unit for aquifer Kv
    units=[tunitkh, tunitv, tunitl]
    logger.debug(f'{tunitl=}')

    _, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=1)
    logger.debug(f'file_lines[{line_index}] = {file_lines[line_index]}')

    if ngroup > 0:                                                      # parametric grid
        # skip range spec ("1-1393" or similar), read NDP and NEP
        ndp_str, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=1)
        ndp = int(ndp_str)                                              # NDP: parametric grid nodes
        nep_str, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=1)
        nep = int(nep_str)                                              # NEP: parametric grid elements
        logger.debug(f'{ndp=}')
        logger.debug(f'{nep=}')

        # skip NEP connectivity lines + separator (separator is a comment, auto-skipped)
        _, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=nep + 1)
        logger.debug(f'file_lines[{line_index}] = {file_lines[line_index]}')

        # determine layers from first parametric node data line
        layers = 1
        len1 = len(file_lines[line_index].split())
        len2 = len(file_lines[line_index + 1].split())
        if len2 < len1:
            while (line_index + layers < len(file_lines) and
                   len(file_lines[line_index + layers].split()) < len1):
                layers += 1
        logger.debug(f'{layers=} (parametric)')

        # skip all NDP * layers parametric data lines
        line_index += ndp * layers

        # parameter arrays unavailable — interpolation not yet implemented
        # TODO: implement parametric grid → model node interpolation:
        #   - read preprocessor node file for model node (x, y) coordinates
        #   - interpolate Kh, Ss, Sy, Kq, Kv from parametric nodes to model nodes
        logger.warning(
            f'{gw_file}: parametric grid (NGROUP={ngroup}) — '
            'aquifer parameters not interpolated to model nodes; '
            'Kh/Ss/Sy/Kq/Kv returned as empty lists.'
        )
        nodes = None
        Kh, Ss, Sy, Kq, Kv = [], [], [], [], []

    else:                                                               # read parameter values
        # how many layers?
        layers = 1
        len1 = len(file_lines[line_index].split())                      # includes node number
        len2 = len(file_lines[line_index+1].split())                    # does not include node number unless one layer
        if len2 == len1:
            layers = 1
        else:
            while (line_index + layers < len(file_lines) and
                   len(file_lines[line_index+layers].split()) < len1):
                layers += 1

            if line_index + layers >= len(file_lines):
                raise ValueError(
                    f"Unexpected end of file while determining layers at line {line_index}"
                )

        # how many nodes?
        nodes = 0
        while (line_index + (nodes * layers) < len(file_lines) and
               file_lines[line_index+(nodes*layers)].split()[0] != 'C'):
            nodes += 1

        if line_index + (nodes * layers) >= len(file_lines):
            raise ValueError(
                f"'C' marker not found while counting nodes at line {line_index}"
            )

        nodes -= 1

        # initialize parameter arrays
        Kh = [[0.0 for col in range(layers)] for row in range(nodes)]
        Ss = [[0.0 for col in range(layers)] for row in range(nodes)]
        Sy = [[0.0 for col in range(layers)] for row in range(nodes)]
        Kq = [[0.0 for col in range(layers)] for row in range(nodes)]
        Kv = [[0.0 for col in range(layers)] for row in range(nodes)]

        # read parameter values
        for node in range(nodes):
            for layer in range(layers):
                values = file_lines[line_index].split()
                if layer == 0:
                    _ = values.pop(0)                                   # discard node ID (derived from init_cond)
                Kh[node][layer] = float(values[0])
                Ss[node][layer] = float(values[1])
                Sy[node][layer] = float(values[2])
                Kq[node][layer] = np.float32(values[3])
                Kv[node][layer] = float(values[4])
                line_index += 1

    # -- Anomaly in Hydraulic Conductivity --
    _, line_index = read_next_line_value(file_lines, line_index - 1, column=0)
    logger.debug(f'file_lines[{line_index}] = {file_lines[line_index]}')
    nebk = int(file_lines[line_index].split()[0])                 # anomaly count
    logger.debug(f'{nebk=}')

    # Skip FACT, TUNITH, and nebk anomaly data lines (nebk + 2 non-comment lines)
    _, line_index = read_next_line_value(file_lines, line_index, column=0, skip_lines=nebk + 2)
    logger.debug(f'After anomaly section, line_index={line_index}: {file_lines[line_index][:80]}')

    # Check if this is IFLAGRF (Groundwater Return Flow) or FACTHP (Initial Conditions)
    # IFLAGRF is an integer 0 or 1; FACTHP is a float conversion factor (typically 1.0)
    # Distinguish by checking the inline comment or by checking if the line after this
    # one contains FACTHP-style data (node IDs with head values)
    current_val = file_lines[line_index].split()[0]
    line_upper = file_lines[line_index].upper()

    if 'IFLAGRF' in line_upper or 'RETURN' in line_upper:
        # Explicit IFLAGRF line
        iflagrf = int(current_val)
        logger.debug(f'{iflagrf=}')
        if iflagrf == 1:
            if nodes is not None:
                _, line_index = read_next_line_value(file_lines, line_index, column=0, skip_lines=nodes)
            else:
                _, line_index = read_next_line_value(file_lines, line_index, column=0)
                while line_index < len(file_lines):
                    ln = file_lines[line_index]
                    if not ln.strip() or ln.strip()[0] in comments:
                        line_index += 1
                        continue
                    parts = ln.split()
                    if len(parts) != 3:
                        break
                    try:
                        int(parts[0]); int(parts[1]); int(parts[2])
                        line_index += 1
                    except ValueError:
                        break
        else:
            _, line_index = read_next_line_value(file_lines, line_index, column=0)
        logger.debug(f'After return flow, line_index={line_index}: {file_lines[line_index][:80]}')
    elif 'FACTHP' in line_upper:
        # No IFLAGRF section, this is already FACTHP
        pass
    else:
        # Heuristic: check if the value is 0 or 1 (IFLAGRF) vs a float like 1.0
        # Look at the next few non-comment lines for structure clues
        try:
            test_val = int(current_val)
            # Check if the next non-comment line looks like return flow data (ID TYPDEST DEST)
            # or initial condition data (ID HEAD1 HEAD2 ...)
            peek_idx = line_index + 1
            while peek_idx < len(file_lines) and file_lines[peek_idx].strip() and \
                  file_lines[peek_idx].strip()[0] in comments:
                peek_idx += 1
            if peek_idx < len(file_lines):
                peek_parts = file_lines[peek_idx].split()
                # Return flow data has 3 columns (ID, TYPDEST, DEST)
                # Init cond data has layers+1 columns (ID, HEAD1, ..., HEADn)
                if test_val in (0, 1) and len(peek_parts) == 3:
                    # Likely IFLAGRF
                    iflagrf = test_val
                    logger.debug(f'{iflagrf=} (detected)')
                    if iflagrf == 1:
                        if nodes is not None:
                            _, line_index = read_next_line_value(file_lines, line_index, column=0, skip_lines=nodes)
                        else:
                            _, line_index = read_next_line_value(file_lines, line_index, column=0)
                            while line_index < len(file_lines):
                                ln = file_lines[line_index]
                                if not ln.strip() or ln.strip()[0] in comments:
                                    line_index += 1
                                    continue
                                parts = ln.split()
                                if len(parts) != 3:
                                    break
                                try:
                                    int(parts[0]); int(parts[1]); int(parts[2])
                                    line_index += 1
                                except ValueError:
                                    break
                    else:
                        _, line_index = read_next_line_value(file_lines, line_index, column=0)
                    logger.debug(f'After return flow, line_index={line_index}: {file_lines[line_index][:80]}')
                # else: not IFLAGRF, fall through to FACTHP
        except ValueError:
            pass  # Not an integer, must be FACTHP

    # -- Initial Groundwater Head Values --
    # FACTHP line
    facthp = float(file_lines[line_index].split()[0])
    logger.debug(f'{facthp=}')

    # Read initial heads: ID  HP[1]  HP[2]  ...  HP[layers]
    _, line_index = read_next_line_value(file_lines, line_index, column=0)
    logger.debug(f'Init cond start at line_index={line_index}: {file_lines[line_index][:80]}')

    init_cond = []
    if nodes is not None:
        for node in range(nodes):
            items = file_lines[line_index].split()
            temp = [int(items[0])]
            for l in range(layers):
                temp.append(float(items[l + 1]))
            init_cond.append(temp)
            line_index += 1
    else:
        # parametric case: init_cond is last section — read until EOF / non-matching line
        while line_index < len(file_lines):
            line = file_lines[line_index].strip()
            if not line or line[0] in comments:
                line_index += 1
                continue
            items = line.split()
            try:
                temp = [int(items[0])]
                for l in range(layers):
                    temp.append(float(items[l + 1]))
                init_cond.append(temp)
                line_index += 1
            except (ValueError, IndexError):
                break

    # derive node_id from init_cond for all ngroup values (single source of truth)
    node_id = [row[0] for row in init_cond]
    logger.debug('leaving iwfm_read_gw.py')

    gw_files = GroundwaterFiles(
        bc_file=bc_file,
        drain_file=drain_file,
        pump_file=pump_file,
        subs_file=subs_file,
        headall=headall,
    )

    return gw_files, node_id, layers, Kh, Ss, Sy, Kq, Kv, init_cond, units, hydrographs, factxy
