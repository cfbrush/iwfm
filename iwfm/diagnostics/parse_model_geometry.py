# parse_model_geometry.py
# Read IWFM model geometry files for node/element coordinates
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Read IWFM model geometry files for node/element coordinates.'''

import re


def parse_node_coords(node_file):
    """Read IWFM node coordinate file.

    Parameters
    ----------
    node_file : str
        Path to IWFM node file (e.g., C2VSimCG_Nodes.dat).

    Returns
    -------
    dict
        {node_id: (x, y)} for all nodes.
    """
    coords = {}
    with open(node_file, encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ('C', 'c', '*', '#'):
                continue
            parts = s.split()
            if len(parts) < 3:
                continue
            try:
                nid = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                coords[nid] = (x, y)
            except ValueError:
                continue

    return coords


def parse_pst_param_nodes(pst_file, prefix='PKH', layer=None):
    """Extract node IDs that have parameters in a .pst file.

    Parameters
    ----------
    pst_file : str
        Path to PEST .pst file.
    prefix : str
        Parameter prefix (e.g., 'PKH', 'PL', 'PN', 'PS', 'c_sn').
    layer : int, optional
        Filter to specific layer. If None, return all layers.

    Returns
    -------
    set of int
        Node IDs that have parameters matching prefix/layer.
    """
    nodes = set()

    if prefix == 'c_sn':
        pattern = re.compile(r'^c_sn_(\d+)')
    else:
        if layer is not None:
            pattern = re.compile(rf'^{prefix}(\d+)_L{layer}\b')
        else:
            pattern = re.compile(rf'^{prefix}(\d+)_L\d+')

    in_params = False
    with open(pst_file, encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s == '* parameter data':
                in_params = True
                continue
            if s.startswith('*') and in_params:
                break
            if not in_params:
                continue

            parts = s.split()
            if not parts:
                continue

            m = pattern.match(parts[0])
            if m:
                nodes.add(int(m.group(1)))

    return nodes


def parse_stream_nodes(stream_file):
    """Read stream node IDs and their associated GW nodes from IWFM stream file.

    Parameters
    ----------
    stream_file : str
        Path to IWFM stream specification or stream data file.

    Returns
    -------
    list of int
        Stream node IDs (1-based, sequential).
    dict
        {stream_node_id: gw_node_id} mapping.
    """
    stream_ids = []
    strm_to_gw = {}

    with open(stream_file, encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ('C', 'c', '*', '#'):
                continue
            parts = s.split()
            if len(parts) < 4:
                continue
            try:
                sn_id = int(parts[0])
                gw_node = int(parts[3])
                stream_ids.append(sn_id)
                strm_to_gw[sn_id] = gw_node
            except ValueError:
                continue

    return stream_ids, strm_to_gw
