# geop_saveplot.py
# Create and save a plot from a geopandas dataframe
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



def geop_saveplot(gdf, outname, **kwargs):
    '''Create and save plot from geopandas dataframe.

    Parameters
    ----------
    gdf : geopandas dataframe object

    outname : str
        output file name

    **kwargs : dict, optional
        Additional keyword arguments to pass to gdf.plot()
        (e.g., column='name', cmap='viridis', etc.)

    Returns
    -------
    nothing
    '''
    import matplotlib.pyplot as plt
    gdf.plot(**kwargs)
    plt.savefig(outname)
    plt.close()
    return
