# map_params_rz_urban.py
# Create colored maps  representing urban rootzone parameters
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


def get_params_rz_urban(node_file_name, elem_file_name, rz_ur_file_name, verbose=False):
    ''' get_params_rz_urban() - Get urban rootzone parameters and node and element information

    Parameters
    ----------
    node_file_name : str
        IWFM Node.dat file name

    elem_file_name : str
        IWFM Element.dat file name

    rz_ur_file : str
        name of urban rootzone file

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

    # Get the root zone parameters from the non-ponded crop rootzone file
    crops_ur, param_vals_ur, _ = iwfm.iwfm_read_rz_urban(rz_ur_file_name)        # Read parameters
    param_types_ur = ['perv', 'cn', 'icpopul', 'icwtruse', 'fracdm', 'iceturb', 'icrtfurb', 'icrufurb', 'icurbspec']
    if verbose: print(f'  Read root zone parameters from the Urban rootzone file {rz_ur_file_name}')

    return elem_centroids, boundary_coords, crops_ur, param_vals_ur, param_types_ur


def map_params_rz_urban(node_file_name, elem_file_name, out_name, rz_ur_file_name, 
                  format='tiff', point_width=100, verbose=False):
    ''' map_params_rz_urban() -Create a colored image map representing urban data

    Parameters
    ----------
    node_file_name : str
        IWFM Node.dat file name

    elem_file_name : str
        IWFM Element.dat file name

    out_name : str
        Output file base name

    rz_ur_file_name : str
        urban rootzone file name

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

    elem_centroids, boundary_coords, crops_ur, param_vals_ur, param_types_pc = get_params_rz_urban(node_file_name, 
                elem_file_name, rz_ur_file_name, verbose=verbose)

    count = 0
    # Curve Numbers
    label='CN values'
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,1][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_CN_Urban.{format}'
    title = 'Urban Curve Number'             

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # Create images for all ET columns 
    label='ET Column'
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,5][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_ETcol_Urban.{format}'
    title = 'Urban Evapotranspiration Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    label='Column'
    # urban pervious area
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,0][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_PervArea_Urban.{format}'
    title = 'Urban Pervious Area'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # urban population
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,2][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_PopCol_Urban.{format}'
    title = 'Urban Population Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # urban per capita demand
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,3][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_PerCapCol_Urban.{format}'
    title = 'Urban Per Capita Demand Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # urban demand fraction
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,4][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_DMFrac_Urban.{format}'
    title = 'Urban Demand Fraction Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # urban return flow fraction
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,6][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_RTFrac_Urban.{format}'
    title = 'Urban Return Flow Fraction Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # urban reuse fraction
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,7][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_RUFrac_Urban.{format}'
    title = 'Urban Reuse Fraction Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    # urban indoor water use
    dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_ur[0][:,8][j] ] for j in range(len(elem_centroids))]
    image_name = f'{out_name}_Indoor_Urban.{format}'
    title = 'Urban Indoor Use Column'

    iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)    
    count += 1

    return count


    
# Run map_rz_params_npc() from command line
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
        rz_ur_file_name     = args[3]
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
        rz_ur_file_name     = input('IWFM Urban file name: ')
        out_name            = input('Output file base name: ')
        format              = input('Output file format (pdf, png, tiff): ').lower()

    iwfm.file_test(node_file_name)
    iwfm.file_test(elem_file_name)
    iwfm.file_test(rz_ur_file_name)

    idb.exe_time()  # initialize timer


    count = map_params_rz_urban(node_file_name, elem_file_name, out_name, rz_ur_file_name, 
                        format=format, point_width=point_width, verbose=verbose)
    
    print(f'  Wrote {count:,} {format.upper()} images')

    idb.exe_time()                                          # print elapsed time

    