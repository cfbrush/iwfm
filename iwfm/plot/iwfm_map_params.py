# iwfm_map_params.py
# Create a contour map representing nodal values such as groundwater data.
# Copyright (C) 2024-2026 University of California
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

# ---- Module-level parameter dictionary ----
# Maps parameter keyword to [category, description]
INPUT_DICT = {
    'kh'     : ['Groundwater',  'Horizontal hydraulic conductivity'],
    'ss'     : ['Groundwater',  'Specific storage'],
    'sy'     : ['Groundwater',  'Specific yield'],
    'kv'     : ['Groundwater',  'Vertical hydraulic conductivity'],
    'kq'     : ['Groundwater',  'Aquiclude hydraulic conductivity'],
    'gwic'   : ['Groundwater',  'Initial groundwater head'],

    'nuz'    : ['Unsaturated',  'Unsaturated zone porosity'],
    'iuz'    : ['Unsaturated',  'Unsaturated zone pore-size distribution index'],
    'kuz'    : ['Unsaturated',  'Unsaturated zone hydraulic conductivity'],
    'rhcuz'  : ['Unsaturated',  'Method to represent hydraulic conductivity vs. moisture content curve'],
    'icuz'   : ['Unsaturated',  'Initial unsaturated zone moisture content'],

    'wp'     : ['Rootzone',     'Wilting point'],
    'fc'     : ['Rootzone',     'Field capacity'],
    'tn'     : ['Rootzone',     'Porosity'],
    'lambda' : ['Rootzone',     'Pore-size distribution index'],
    'ksoil'  : ['Rootzone',     'Rootzone hydraulic conductivity'],
    'rhc'    : ['Rootzone',     'Method to represent hydraulic conductivity vs. moisture content curve'],
    'cp'     : ['Rootzone',     'Capillary rise'],
    'irne'   : ['Rootzone',     'Precipitation column'],
    'frne'   : ['Rootzone',     'Precipitation multiplier'],
    'imsrc'  : ['Rootzone',     'Irrigation source column'],
    'tp'     : ['Rootzone',     'Runoff and return flow destination type'],
    'dest'   : ['Rootzone',     'Runoff and return flow destination value'],
    'kpond'  : ['Rootzone',     'Ponded hydraulic conductivity'],

    'cnnp'   : ['Non-ponded',   'Curve Number value'],
    'etnp'   : ['Non-ponded',   'ET column'],
    'ipnp'   : ['Non-ponded',   'Irrigation Period column'],
    'tsnp'   : ['Non-ponded',   'Target soil moisture column'],
    'rfnp'   : ['Non-ponded',   'Irrigation water return flow fraction column'],
    'icnp'   : ['Non-ponded',   'Initial soil moisture condition'],

    'cnpc'   : ['Ponded',       'Curve Number value'],
    'etpc'   : ['Ponded',       'ET column'],
    'wsppc'  : ['Ponded',       'Water Supply Requirement column'],
    'ippc'   : ['Ponded',       'Irrigation Period column'],
    'pdpc'   : ['Ponded',       'Ponding Depths column'],
    'adpc'   : ['Ponded',       'Application Depths column'],
    'rfpc'   : ['Ponded',       'Return Flow Depths column'],
    'rupc'   : ['Ponded',       'Reuse Flow Depths column'],
    'icpc'   : ['Ponded',       'Initial soil moisture condition'],

    'perv'   : ['Urban',        'Percent pervious'],
    'cnur'   : ['Urban',        'Curve Number value'],
    'pop'    : ['Urban',        'Population column'],
    'wtr'    : ['Urban',        'Water use column'],
    'frur'   : ['Urban',        'Urban demand population fraction'],
    'etur'   : ['Urban',        'ET column'],
    'rtur'   : ['Urban',        'Urban fraction to runoff column'],
    'ruur'   : ['Urban',        'Urban fraction reused column'],
    'riur'   : ['Urban',        'Urban fraction used indoors column'],
    'icur'   : ['Urban',        'Initial urban moisture content'],

    'cnnv'   : ['Native',       'Native Vegetation Curve Number value'],
    'cnrv'   : ['Native',       'Riparian Vegetation Curve Number value'],
    'etnv'   : ['Native',       'Native Vegetation ET column'],
    'etrv'   : ['Native',       'Riparian Vegetation ET column'],
    'strv'   : ['Native',       'Riparian Vegetation source stream node'],
    'icnv'   : ['Native',       'Initial native vegetation moisture content'],
    'icrv'   : ['Native',       'Initial riparian vegetation moisture content'],

    'et'     : ['ET',           'ET values'],
    'pr'     : ['Precip',       'Precipitation values'],
}

# Maps category to sim_files key for the file containing that data
CATEGORY_TO_FILETYPE = {
    'Groundwater': 'gw_file',
    'Unsaturated': 'unsat_file',
    'Rootzone':    'root_file',
    'Non-ponded':  'root_file',
    'Ponded':      'root_file',
    'Urban':       'root_file',
    'Native':      'root_file',
    'ET':          'et_file',
    'Precip':      'precip_file',
}

# Maps category to (reader_function_name, param_index_dict, data_format)
CATEGORY_DISPATCH = {
    'Groundwater': ('iwfm_read_gw_params',
                    {'kh': 0, 'ss': 1, 'sy': 2, 'kq': 3, 'kv': 4, 'gwic': 5},
                    'nodes'),
    'Rootzone':    ('iwfm_read_rz_params',
                    {'wp': 0, 'fc': 1, 'tn': 2, 'lambda': 3, 'ksoil': 4,
                     'rhc': 5, 'cp': 6, 'irne': 7, 'frne': 8, 'imsrc': 9,
                     'tp': 10, 'dest': 11, 'kpond': 12},
                    'elements'),
    'Non-ponded':  ('iwfm_read_rz_npc',
                    {'cnnp': 0, 'etnp': 1, 'wspnp': 2, 'ipnp': 3,
                     'msnp': 4, 'tsnp': 5, 'rfnp': 6, 'runp': 7, 'icnp': 8},
                    'elements'),
    'Ponded':      ('iwfm_read_rz_pc',
                    {'cnpc': 0, 'etpc': 1, 'wsppc': 2, 'ippc': 3,
                     'pdpc': 4, 'adpc': 5, 'rfpc': 6, 'rupc': 7, 'icpc': 8},
                    'elements'),
    'Urban':       ('iwfm_read_rz_urban',
                    {'perv': 0, 'cnur': 1, 'pop': 2, 'wtr': 3, 'frur': 4,
                     'etur': 5, 'rtur': 6, 'ruur': 7, 'riur': 8, 'icur': 9},
                    'elements'),
    'Native':      ('iwfm_read_rz_nr',
                    {'cnnv': 0, 'cnrv': 1, 'etnv': 2, 'etrv': 3,
                     'strv': 4, 'icnv': 5, 'icrv': 6},
                    'elements'),
    'Unsaturated': ('iwfm_read_uz_params',
                    {'thkuz': 0, 'nuz': 1, 'iuz': 2, 'kuz': 3,
                     'rhcuz': 4, 'icuz': 5},
                    'elements'),
    'ET':          ('iwfm_read_et_vals',
                    {'et': 0},
                    'elements'),
    'Precip':      ('iwfm_read_precip_vals',
                    {'pr': 0},
                    'elements'),
}

# Maps rootzone sub-category to rz_files key
RZ_SUBFILE_MAP = {
    'Non-ponded': 'np_file',
    'Ponded':     'p_file',
    'Urban':      'ur_file',
    'Native':     'nr_file',
}


def get_params(data_filename, param_type, param_values, layer=0, verbose=False):
    """Get parameter values from the data file.

    Parameters
    ----------
    data_filename : str
        Path to the file containing the parameter values.

    param_type : str
        The parameter keyword to be mapped (e.g. 'kh', 'sy', 'wp').

    param_values : list
        [category, description] from INPUT_DICT.

    layer : int, default=0
        Layer index (0-based) for multi-layer data. Default is first layer.

    verbose : bool, default=False
        If True, print status messages.

    Returns
    -------
    data : list or numpy array
        Parameter values (one per node or element).

    data_format : str
        'nodes' or 'elements'
    """
    import numpy as np
    import iwfm

    if verbose:
        print(f"Reading parameter values from {data_filename}")
        print(f"Parameter type: {param_type}")

    category = param_values[0]

    if category not in CATEGORY_DISPATCH:
        raise ValueError(
            f"Unknown category '{category}' for parameter '{param_type}'. "
            f"Valid categories: {list(CATEGORY_DISPATCH.keys())}"
        )

    reader_name, param_index, data_format = CATEGORY_DISPATCH[category]
    reader_func = getattr(iwfm, reader_name)
    data = reader_func(data_filename)
    data = data[param_index[param_type]]

    if verbose:
        print(f"Read parameter values")

    # Handle multi-layer data: select requested layer
    if isinstance(data, np.ndarray) and len(data.shape) == 2:
        if layer >= data.shape[1]:
            raise ValueError(
                f"Requested layer {layer + 1} but data only has "
                f"{data.shape[1]} layer(s)."
            )
        if verbose:
            print(f"Data has {data.shape[1]} layer(s). Using layer {layer + 1}.")
        data = data[:, layer]
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], (list, np.ndarray)):
        if verbose:
            print(f"Data has multiple values per location. Using layer {layer + 1}.")
        data = [d[layer] if isinstance(d, (list, np.ndarray)) and len(d) > layer
                else d for d in data]

    return data, data_format


def iwfm_map_params(dataset, bounding_poly, image_basename, cmap='rainbow',
                    title='Parameter values', label='Z values', units='',
                    no_levels=20, contour='line', output_dir='.', verbose=False):
    """Create a contour map representing nodal or element values.

    Parameters
    ----------
    dataset : list of lists
        [[x, y, value], ...] for each node or element centroid.

    bounding_poly : shapely Polygon or list of (x, y) tuples
        Boundary polygon for masking the contour map.

    image_basename : str
        Base name for the output image file (without extension).

    cmap : str, default='rainbow'
        Matplotlib colormap name.

    title : str, default='Parameter values'
        Title for the plot.

    label : str, default='Z values'
        Label for the colorbar.

    units : str, default=''
        Units for the colorbar.

    no_levels : int, default=20
        Number of contour levels.

    contour : str, default='line'
        'line' for contour lines, 'filled' for filled contours.

    output_dir : str, default='.'
        Directory for output image file.

    verbose : bool, default=False
        If True, print status messages.

    Returns
    -------
    str
        Path to the saved image file.
    """
    import os
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.path import Path as MplPath
    from matplotlib.patches import PathPatch
    from scipy.interpolate import griddata
    import numpy as np
    from iwfm.plot import get_XYvalues, contour_levels

    from pathlib import Path
    image_name = str(Path(output_dir) / f'{image_basename}.png')

    X, Y, Z = get_XYvalues(dataset)

    # Define the contour levels
    levels = contour_levels(Z, no_levels=no_levels, verbose=verbose)

    # Create a regular grid for interpolation
    ratio = (X.max() - X.min()) / (Y.max() - Y.min())
    grid_res = 200
    xi = np.linspace(X.min(), X.max(), int(grid_res * ratio))
    yi = np.linspace(Y.min(), Y.max(), grid_res)
    Xi, Yi = np.meshgrid(xi, yi)

    # Interpolate the irregular data onto the regular grid
    Zi = griddata((X, Y), Z, (Xi, Yi), method='linear')

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create path from boundary polygon
    if hasattr(bounding_poly, 'exterior'):
        boundary_coords = list(bounding_poly.exterior.coords)
        path = MplPath(boundary_coords)
    else:
        path = MplPath(bounding_poly)

    # Create and apply mask from boundary polygon
    mask = path.contains_points(
        np.column_stack((Xi.ravel(), Yi.ravel()))
    ).reshape(Xi.shape)
    Zi = np.ma.masked_array(Zi, mask=~mask)

    # Plot the masked data
    if contour == 'filled':
        plt.contourf(Xi, Yi, Zi, levels=levels, cmap=cmap)
    else:
        plt.contour(Xi, Yi, Zi, levels=levels, cmap=cmap)

    # Add colorbar
    cb_label = f'{label} {units}'.strip()
    plt.colorbar(label=cb_label, shrink=0.5, fraction=0.046, pad=0.04)

    # Display boundary polygon
    patch = PathPatch(path, facecolor='none')
    ax.add_patch(patch)

    ax.set_title(title)
    plt.axis('off')

    # Create output directory if needed
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    plt.savefig(image_name)
    plt.close('all')

    if verbose:
        print(f"Image saved to {image_name}")

    return image_name


if __name__ == "__main__":
    """Run iwfm_map_params() from command line."""
    import sys
    from pathlib import Path
    from shapely import geometry
    from iwfm.debug import exe_time
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) < 5:
        print("Usage: python iwfm_map_params.py <sim_file> <pre_file> <param_type> <image_basename> [layer] [contour] [output_dir]")
        print("  Create a contour map of IWFM model parameters")
        print("")
        print("  sim_file       : IWFM Simulation main file")
        print("  pre_file       : IWFM Preprocessor main file")
        print("  param_type     : Parameter keyword (see list below)")
        print("  image_basename : Output image base name (without extension)")
        print("  layer          : Layer number, 1-based (default: 1)")
        print("  contour        : 'line' or 'filled' (default: 'line')")
        print("  output_dir     : Output directory (default: '.')")
        print("")
        print("  Valid parameter keywords:")
        # Group by category for readability
        categories = {}
        for key, val in INPUT_DICT.items():
            categories.setdefault(val[0], []).append((key, val[1]))
        for cat, params in categories.items():
            print(f"    {cat}:")
            for key, desc in params:
                print(f"      {key:10s} - {desc}")
        sys.exit(1)

    sim_filename   = sys.argv[1]
    pre_filename   = sys.argv[2]
    param_type     = sys.argv[3]
    image_basename = sys.argv[4]
    layer          = int(sys.argv[5]) - 1 if len(sys.argv) > 5 else 0  # convert 1-based to 0-based
    contour_type   = sys.argv[6] if len(sys.argv) > 6 else 'line'
    output_dir     = sys.argv[7] if len(sys.argv) > 7 else '.'

    iwfm.file_test(sim_filename)
    iwfm.file_test(pre_filename)

    if param_type not in INPUT_DICT:
        print(f" ** Parameter type '{param_type}' is invalid **")
        print("Valid parameter types:")
        for key, val in INPUT_DICT.items():
            print(f"  {key:10s} - {val[0]:14s} {val[1]}")
        sys.exit(1)

    param_values = INPUT_DICT[param_type]
    category = param_values[0]

    exe_time()                                              # initialize timer

    # Determine the file containing the data
    data_filetype = CATEGORY_TO_FILETYPE[category]

    # Get file names from preprocessor and simulation files
    pre_files, have_lake = iwfm.iwfm_read_preproc(pre_filename)
    sim_files, have_lake = iwfm.iwfm_read_sim_file(sim_filename)

    sim_dir = Path(sim_filename).parent
    pre_dir = Path(pre_filename).parent

    # Resolve the data file path
    if data_filetype == 'root_file':
        rz_filename = sim_dir / Path(sim_files[data_filetype].replace('\\', '/'))
        rz_files = iwfm.iwfm_read_rz(rz_filename)

        if category in RZ_SUBFILE_MAP:
            data_filename = rz_files[RZ_SUBFILE_MAP[category]].replace('\\', '/')
        else:
            # 'Rootzone' category — the rootzone main file has the parameters
            data_filename = sim_files[data_filetype].replace('\\', '/')
    else:
        data_filename = sim_files[data_filetype].replace('\\', '/')

    data_filename = sim_dir / Path(data_filename)
    iwfm.file_test(data_filename)

    # Get the parameter values from the data file
    data, data_format = get_params(data_filename, param_type, param_values,
                                   layer=layer, verbose=True)

    # Read nodal X,Y coordinates from node file
    node_filename = pre_dir / Path(pre_files['node_file'].replace('\\', '/'))
    node_coord, node_list, factor = iwfm.iwfm_read_nodes(node_filename)

    # Read elements from elements file
    elem_filename = pre_dir / Path(pre_files['elem_file'].replace('\\', '/'))
    elem_ids, elem_nodes, elem_sub = iwfm.iwfm_read_elements(elem_filename)

    # Calculate element centroids
    elem_centroids = iwfm.get_elem_centroids(elem_ids, elem_nodes, node_coord)

    # Get boundary coordinates for masking
    boundary_coords = iwfm.iwfm_boundary_coords(node_filename, elem_filename)
    bounding_poly = geometry.Polygon(boundary_coords)

    # Build the title and label from the parameter description
    title = f"{param_values[1]}"
    if layer > 0 or data_format == 'nodes':
        title += f" - Layer {layer + 1}"
    label = param_values[1]

    image_name = image_basename + '_' + param_type

    if data_format == 'nodes':
        dataset = [[node_coord[i][1], node_coord[i][2], data[i]]
                   for i in range(len(node_list))]
    elif data_format == 'elements':
        dataset = [[elem_centroids[i][1], elem_centroids[i][2], data[i]]
                   for i in range(len(elem_centroids))]
    else:
        print(f"Error: Unknown data format '{data_format}'")
        sys.exit(1)

    iwfm_map_params(dataset, bounding_poly, image_name, title=title,
                    label=label, contour=contour_type, output_dir=output_dir,
                    verbose=True)

    exe_time()                                              # print elapsed time
