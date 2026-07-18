# overlay_histograms.py 
# Overlay histograms of two parameters to visualize the distribution of two datasets.
# Copyright (C) 2023-2026 University of California
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


'''Overlay histograms of two parameters to visualize the distribution of two datasets.'''

def overlay_histograms(data1, data2, file_name, label1='Data 1', label2='Data 2', format='pdf', alpha=0.5, bins='auto'):
    '''
    Overlay two histograms to visualize the distribution of two datasets.

    Parameters
    ----------
    data1 : list or array-like
        The first dataset.

    data2 : list or array-like
        The second dataset.

    label1 : str, optional
        Label for the first dataset.

    label2 : str, optional
        Label for the second dataset.

    format: str, optional, default = 'pdf'
        output file format: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
        
    alpha : float, optional, default = 0.5
        Transparency level for histograms. Value ranges from 0 (completely transparent) to 1 (fully opaque).

    bins : int or str, optional, default = 'auto'
        Number of bins for the histograms. Can be an integer specifying the number of bins, or a method like 'auto'
        to automatically determine the number of bins.

    Returns
    -------
    None

    Example
    -------
    overlay_histograms(data1, data2, label1='Dataset 1', label2='Dataset 2', alpha=0.5, bins='auto')
    '''
    import numpy as np
    import matplotlib.pyplot as plt

    data1 = np.array(data1)
    data2 = np.array(data2)
    
    plt.hist(data1, bins=bins, color = 'r', alpha=alpha, label=label1, log = True)
    plt.hist(data2, bins=bins, color = 'g', alpha=alpha, label=label2, log = True)

    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Overlayed Histograms')
    plt.legend()

    plt.grid(True)
    plt.savefig(file_name, format=format)
    plt.close()

#    plt.save options, potential future use
#    plt.savefig(file_name, 
#            format=format,       # Explicit format
#            dpi=300,             # Resolution (dots per inch)
#            bbox_inches="tight", # Trim whitespace
#            transparent=True,    # Transparent background
#            facecolor="white")   # Background color


if __name__ == "__main__":

    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    params = ["kh", "ss", "sy", "kq", "kv"]
    valid_formats = ['eps', 'jpeg', 'jpg', 'pdf', 'pgf', 'png', 'ps', 'raw', 'rgba', 'svg', 'svgz', 'tif', 'tiff', 'webp']

    args = sys.argv

    if len(args) > 1:  # arguments are listed on the command line
        gw_file   = args[1]
        param1    = args[2]
        layer1    = args[3]
        param2    = args[4]
        layer2    = args[5]
        format    = args[6].lower() # output file format: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp

    else:  # get everything form the command line
        gw_file   = input('IWFM Groundwater.dat file name: ')
        param1    = input('Parameter 1 (kh, ss, sy, kq, kv): ')
        layer1    = input('Model layer for Parameter 1: ')
        param2    = input('Parameter 2 (kh, ss, sy, kq, kv): ')
        layer2    = input('Model layer for Parameter 2: ')
        format    = input('Output file format (pdf, png, tiff): ').lower()


    # check for valid parameters
    if param1.lower() in params:
        param_index1 = params.index(param1.lower())
    else:
        print(f"Exiting: '{param1}' not a valid parameter: kh, ss, sy, kq, kv")
        sys.exit()
    if param2.lower() in params:
        param_index2 = params.index(param2.lower())
    else:
        print(f"Exiting: '{param2}' not a valid parameter: kh, ss, sy, kq, kv")
        sys.exit()

    # check for valid output format
    if format.lower() not in valid_formats:
        print(f"Warning: '{format}' not a valid output file format: pdf, png, tiff")
        format = 'pdf'
        print(f"          Will save as {format}.")

    iwfm.file_test(gw_file)

    layer1, layer2 = int(layer1), int(layer2)

    #  Set image file name
    image_name = f"histogram_{params[param_index1]}{layer1}_vs_{params[param_index2]}{layer2}.{format}"

    #  Read all relevant values from Groundwater.dat
    values = iwfm.iwfm_read_gw_params(gw_file)

    data1 = [node[layer1] for node in values[param_index1]]
    data2 = [node[layer2] for node in values[param_index2]]

    idb.exe_time()  # initialize timer

    overlay_histograms(data1, data2, image_name, label1='Data 1', label2='Data 2', format=format, alpha=0.5, bins='auto')

    print(f'  Wrote {image_name}')

    idb.exe_time()  # report execution time

