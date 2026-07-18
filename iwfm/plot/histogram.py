# histogram.py
# Create a histogram of given data and determine the number of bins
# Copyright (C) 2023 University of California
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

'''Create a histogram of given data and determine the number of bins.'''

def histogram(data, name, unit, file, method='auto'):
    '''Create a histogram of given data and determine the number of bins.

    Parameters
    ----------
    data : list or array-like
        The dataset for which the histogram is to be created.

    method : str, optional
        Method for determining the number of bins. Options include:
        - 'auto': Automatically select an appropriate number of bins (default).
        - 'sturges': Use Sturges' rule to determine the number of bins.
        - 'sqrt': Use the square root rule to determine the number of bins.
        - 'rice': Use Rice's rule to determine the number of bins.
        - 'scott': Use Scott's rule to determine the number of bins.
        - 'fd': Use the Freedman-Diaconis rule to determine the number of bins.

    Returns
    -------
    histogram : array
        The histogram values, representing the frequency of data in each bin.

    bins : int
        The determined number of bins for the histogram.
    '''
    import numpy as np
    import matplotlib.pyplot as plt

    # Calculate the histogram and number of bins based on the selected method
    hist, bins = np.histogram(data, bins=method)

    # Plot the histogram
    plt.hist(data, bins=bins, edgecolor='black')
    plt.xlabel(f'Value ({unit})')
    plt.ylabel('Frequency')
    plt.title(f'Histogram of {name} ({unit})')

    #  Save histogram to file
    plt.savefig(file)
    plt.close()

    return hist, bins

if __name__ == "__main__":
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    
    #  Groundwater file info / Replace with info of file you want to plot
    gw_file = "C2VSimCG_Groundwater1974.dat"
    data = iwfm.iwfm_read_gw_params(gw_file)
    params = ["kh", "ss", "sy", "kq", "kv"]
    full_names = ["Hydraulic Conductivity", "Specific Storage", "Specific Yield", "Aquitard Vertical Hydraulic Conductivity", "Aquifer Vertical Hydraulic Conductivity"]
    units = ["L/T", "1/L", "L/L", "L/T", "L/T"]

    #  Plotting specifications / Replace with specifications of parameter you want to plot
    param = 0
    layer = 2

    #  Naming / Could stay the same
    full_name = full_names[param]
    unit = units[param]
    file_name = f"histogram_{params[param]}{layer}.png"

    #  Plot data
    data_to_plot = [node[layer] for node in data[param]]
    histogram(data_to_plot, full_name, unit, file_name)

