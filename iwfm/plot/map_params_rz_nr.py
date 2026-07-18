# map_params_rz_nr.py
# Create colored maps representing native and riparian rootzone parameters
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


'''Create colored maps representing native and riparian rootzone parameters.'''

def get_params_rz_nr(node_file_name, elem_file_name, rz_nr_file_name, verbose=False):
    '''Get native and riparian vegetation rootzone parameters and node and element information.

    Parameters
    ----------
    node_file_name : str
        IWFM Node.dat file name

    elem_file_name : str
        IWFM Element.dat file name

    rz_nr_file_name : str
        name of native and riparian vegetation rootzone file

    verbose : bool, default = False
        Print status messages

    Return
    ------
    nothing
    '''                
    import iwfm
    import iwfm.gis as igis

    # Get info from read nodal file 
    node_coords, node_list, factor = iwfm.iwfm_read_nodes(node_file_name)

    # Get info from element file 
    elem_ids, elem_nodes, elem_sub = iwfm.iwfm_read_elements(elem_file_name)

    # use elem_nodes and node_coords to caclculate the centroid of each element
    elem_centroids = iwfm.get_elem_centroids(elem_ids, elem_nodes, node_coords)

    # Use elem_nodes and node_coords to get the boundary coordinates
    boundary_coords = igis.get_boundary_coords(elem_nodes, node_coords)

    # Get the root zone parameters from the native vegetation rootzone file
    crops_nr, param_vals_nr, _  = iwfm.iwfm_read_rz_nr(rz_nr_file_name)         # Read parameters
    param_types_nr = ['cnnv', 'cnrv', 'icetnv', 'icetrv', 'istrmrv']
    if verbose: print(f'  Read root zone parameters from the Native and Riparian rootzone file {rz_nr_file_name}')

    return elem_centroids, boundary_coords, crops_nr, param_vals_nr, param_types_nr


def map_params_rz_nr(node_file_name, elem_file_name, out_name, rz_nr_file_name, 
                  format='tiff', point_width=100, verbose=False):
    '''Create a colored image map representing native and riparian rootzone parameters.

    Parameters
    ----------
    node_file_name : str
        IWFM Node.dat file name

    elem_file_name : str
        IWFM Element.dat file name

    out_name : str
        Output file base name

    rz_nr_file_name : str
        native and riparian vegetation crop rootzone file name

    format : str, default = 'png'
        output file format: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp

    point_width : int, default = 100
        point width

    verbose : bool, default = False
        Print status messages

    Return
    ------
    nothing
    '''                

    elem_centroids, boundary_coords, crops_nr, param_vals_nr, param_types_nr = get_params_rz_nr(node_file_name, 
                elem_file_name, rz_nr_file_name, verbose=verbose)

    count = 0
    # Curve Numbers
    label='Curve Number'
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,0][j]] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_CN_NAT.{format}'
    title = 'Native Vegetation Curve Number'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,1][j]] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_CN_RIP.{format}'
    title = 'Riparian Vegetation Curve Number'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # ET Columns
    label='ET Column'
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,2][j]] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_ET_NAT.{format}'
    title = 'Native Vegetation Evapotranspiration Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,3][j]] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_ET_RIP.{format}'
    title = 'Riparian Vegetation Evapotranspiration Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # riparian stream node
    label='Stream Node'
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,4][j]] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_IP_SNODE.{format}'
    title = 'Riparian Vegataion Source Stream Node'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # initial condition
    label='Initial Condition'
    rz_name, short_name = ['Native Vegetation', 'Riparian Vegetation'], ['NAT','RIP']
    for i in range(2):
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[1][:,i][j]] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_IC_{short_name[i]}.{format}'
        title = f'{rz_name[i]} Initial Conditions'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
        count += 1

    return count


    
# Run map_params_rz_nr() from command line
if __name__ == "__main__":
    import sys
    import iwfm
    import iwfm.plot as iplot
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    point_width_default = 100
    point_width = point_width_default

    args = sys.argv

    if len(args) > 1:  # arguments are listed on the command line
        node_file_name      = args[1]
        elem_file_name      = args[2]
        rz_nr_file_name     = args[3]
        out_name            = args[4]

        if(len(args) > 5): 
            format          = args[5].lower() # output file format: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp

        if(len(args) > 6): 
            point_width     = int(args[6])  # point width
        if point_width < 1: 
            point_width = point_width_default  # default point width

    else:  # get everything form the command line
        node_file_name      = input('IWFM Node.dat file name: ')
        elem_file_name      = input('IWFM Element.dat file name: ')
        rz_nr_file_name     = input('IWFM Native and Riparian Vegetation file name: ')
        out_name            = input('Output file base name: ')
        format              = input('Output file format (pdf, png, tiff): ').lower()

    iwfm.file_test(node_file_name)
    iwfm.file_test(elem_file_name)
    iwfm.file_test(rz_nr_file_name)

    idb.exe_time()  # initialize timer


    count = map_params_rz_nr(node_file_name, elem_file_name, out_name, rz_nr_file_name, 
                        format=format, point_width=point_width, verbose=verbose)
    
    print(f'  Wrote {count:,} {format.upper()} images')

    idb.exe_time()                                          # print elapsed time

    