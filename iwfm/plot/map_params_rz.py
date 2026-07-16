# map_params_rz.py 
# Read root zone parameters and create figures of the parameters
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


def map_params_rz(node_file_name, elem_file_name, out_name, rz_file_name, 
                  format='tiff', point_width=100, verbose=False):
    ''' map_params_rz() - Read a shapefile of IWFM model elements and map IWFM 
                    Rootzone parameters to the elements

    Parameters
    ----------
    node_file_name : str
        IWFM Node.dat file name

    elem_file_name : str
        IWFM Element.dat file name

    out_name : str
        Output file base name

    rz_file_names : list
        list of rootzone file names

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


    # Read parameter values from rootzone files
    param_vals_rz = iwfm.iwfm_read_rz_params(rz_file_name[0])                          # Read rootzone parameters
    param_types_rz = ['wp', 'fc', 'tn', 'lambda', 'ksoil', 'rhc', 'cprise', 'irne', 'frne', 'imsrc', 'typdest', 'dest', 'kponded']
    if verbose: print(f'  Read root zone parameters from the Main Rootzone file {rz_file_name[0]}')

    if len(rz_file_name) > 1:
        # Get the root zone parameters from the non-ponded crop rootzone file
        crops_np, param_vals_np, _ = iwfm.iwfm_read_rz_npc(rz_file_name[1])        # Read parameters
        if verbose: print(f'  Read root zone parameters from the Non-ponded Crop rootzone file {rz_file_name[1]}')

        # Get the root zone parameters from the ponded crop rootzone file
        crops_pc, param_vals_pc, _ = iwfm.iwfm_read_rz_pc(rz_file_name[2])          # Read parameters
        if verbose: print(f'  Read root zone parameters from the Ponded Crop rootzone file {rz_file_name[2]}')

        # Get the root zone parameters from the urban rootzone file
        crops_u, param_vals_u, _  = iwfm.iwfm_read_rz_urban(rz_file_name[3])        # Read parameters
        if verbose: print(f'  Read root zone parameters from the Urban rootzone file {rz_file_name[3]}')

        # Get the root zone parameters from the native vegetation rootzone file
        crops_nr, param_vals_nr, _  = iwfm.iwfm_read_rz_nr(rz_file_name[4])         # Read parameters
        if verbose: print(f'  Read root zone parameters from the Native and Riparian rootzone file {rz_file_name[4]}')


    if verbose: print('')
    count = 0
    # --------------------------------------
    # create maps for basic rootzone parameters
    for i in range(len(param_vals_rz)):
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_rz[i][j]] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_{param_types_rz[i].upper()}.{format}'
        title = f'Rootzone {param_types_rz[i].upper()}'
        label=f'{param_types_rz[i].upper()} values'
        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                label=label, units='', format=format)
        count += 1
    if verbose: print('  Wrote Rootzone Parameters')

    if rz_npc_file_name:
        # --------------------------------------
        # Start wih the curve number parameters

        label='CN values'
        # non-ponded crops
        for i in range(len(crops_np)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_np[0][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_CN_{crops_np[i].upper()}.{format}'
            title = f'{crops_np[i].upper()} Curve Number'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # ponded crops
        for i in range(len(crops_pc)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_pc[0][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_CN_{crops_pc[i].upper()}.{format}'
            title = f'{crops_pc[i].upper()} Curve Number'             

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # urban
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,1][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_CN_Urban.{format}'
        title = 'Urban Curve Number'             

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # native vegetation
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,0][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_CN_Native.{format}'
        title = 'Native Vegetation Curve Number'             

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # riparian vegetation
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,1][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_CN_Riparian.{format}'
        title = 'Riparian Vegetation Curve Number'             

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        if verbose: print('  Wrote Curve Numbers')


        # --------------------------------------
        # Create images for all ET columns 
        label='ET Column'
        # non-ponded crops
        for i in range(len(crops_np)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_np[1][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_ETcol_{crops_np[i].upper()}.{format}'
            title = f'{crops_np[i].upper()} Evapotranspiration Column'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # ponded crops
        for i in range(len(crops_pc)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_pc[1][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_ETcol_{crops_pc[i].upper()}.{format}'
            title = f'{crops_pc[i].upper()} Evapotranspiration Column'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # urban
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,5][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_ETcol_Urban.{format}'
        title = 'Urban Evapotranspiration Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # native vegetation
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,2][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_ETcol_Native.{format}'
        title = 'Native Vegetation Evapotranspiration Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # riparian vegetation
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,3][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_ETcol_Riparian.{format}'
        title = 'Riparian Vegetation Evapotranspiration Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        if verbose: print('  Wrote ET columns')

        # --------------------------------------
        # non-ponded crops
        # irrigation periods
        for i in range(len(crops_np)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_np[3][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_IrrPd_{crops_np[i].upper()}.{format}'
            title = f'{crops_np[i].upper()} Irrigation Period Column'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # target soil moisture
        for i in range(len(crops_np)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_np[5][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_TSM_{crops_np[i].upper()}.{format}'
            title = f'{crops_np[i].upper()} Target Soil Moisture Column'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # return flow
        for i in range(len(crops_np)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_np[6][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_RF_{crops_np[i].upper()}.{format}'
            title = f'{crops_np[i].upper()} Return Flow Column'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # ponded crops
        # irrigation periods
        for i in range(len(crops_pc)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_pc[3][:,i][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_IrrPd_{crops_pc[i].upper()}.{format}'
            title = f'{crops_pc[i].upper()} Irrigation Period Column'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        label='Column'
        # urban pervious area
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,0][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_PervArea_Urban.{format}'
        title = 'Urban Pervious Area'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # urban population
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,2][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_PopCol_Urban.{format}'
        title = 'Urban Population Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # urban per capita demand
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,3][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_PerCapCol_Urban.{format}'
        title = 'Urban Per Capita Demand Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # urban demand fraction
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,4][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_DMFrac_Urban.{format}'
        title = 'Urban Demand Fraction Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # urban return flow fraction
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,6][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_RTFrac_Urban.{format}'
        title = 'Urban Return Flow Fraction Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # urban reuse fraction
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,7][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_RUFrac_Urban.{format}'
        title = 'Urban Reuse Fraction Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # urban indoor water use
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[0][:,8][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_Indoor_Urban.{format}'
        title = 'Urban Indoor Use Column'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # native vegetation
        # riparian stream node
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[0][:,4][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_Riparian_Stream_Node.{format}'
        title = 'Riparian Vegetation Source Stream Node'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        if verbose: print('  Wrote remaiing rootzone parameters')

        # --------------------------------------
        label='Initial Condition'
        # non-ponded crops
        for i in range(len(crops_np)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_np[8][:,i+1][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_IC_{crops_np[i].upper()}.{format}'
            title = f'{crops_np[i].upper()} Initial Conditions'

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # ponded crops
        for i in range(len(crops_pc)):
            dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_pc[8][:,i+1][j]] for j in range(len(elem_centroids))]
            image_name = f'{out_name}_IC_{crops_pc[i].upper()}.{format}'
            title = f'{crops_pc[i].upper()} Initial Conditions'             

            iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
            count += 1

        # urban
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_u[1][:,1][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_IC_Urban.{format}'
        title = 'Urban Initial Conditions'             

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # native vegetation
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[1][:,0][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_IC_Native.{format}'
        title = 'Native Vegetation Initial Conditions'             

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        # riparian vegetation
        dataset=[[elem_centroids[j][1], elem_centroids[j][2], param_vals_nr[1][:,1][j] ] for j in range(len(elem_centroids))]
        image_name = f'{out_name}_IC_Riparian.{format}'
        title = 'Riparian Vegetation Initial Conditions'

        iplot.map_to_nodes(dataset, boundary_coords, image_name, cmap='rainbow', marker_size = 10, title=title, 
                    label=label, units='', format=format)    
        count += 1

        if verbose: print('  Wrote Initial Conditions')


    return count


# Run map_params_rz() from command line
if __name__ == "__main__":
    import sys
    import iwfm.plot as iplot
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    point_width_default = 100
    point_width = point_width_default

    args = sys.argv

    if len(args) > 1:  # arguments are listed on the command line
        node_file_name          = args[1]
        elem_file_name          = args[2]
        out_name                = args[3]
        format                  = args[4].lower() # output file format: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
        rz_file_name            = args[5]
        if len(args) > 6:
            rz_npc_file_name    = args[6]
            rz_pc_file_name     = args[7]
            rz_ur_file_name     = args[8]
            rz_nv_file_name     = args[9]
        else:
            # Read the file names from the main rootzone file
            rz_npc_file_name, rz_pc_file_name, rz_ur_file_name, rz_nv_file_name = iwfm.iwfm_read_rz_file_names(rz_file_name)

        if(len(args) > 10):
            point_width = int(args[10])  # point width
        if point_width < 1:
            point_width = point_width_default  # default point width

    else:  # get everything form the command line
        node_file_name          = input('IWFM Node.dat file name: ')
        elem_file_name          = input('IWFM Element.dat file name: ')
        out_name                = input('Output file base name: ')
        rz_file_name       = input('IWFM Root Zone Main file name: ')
        answer             = input('Do you want to include the crop rootzone parameters? (y/n): ')
        if answer == 'y':
            # Read the file names from the main rootzone file
            rz_npc_file_name, rz_pc_file_name, rz_ur_file_name, rz_nv_file_name = iwfm.iwfm_read_rz_file_names(rz_file_name)
        format    = input('Output file format (pdf, png, tiff): ').lower()

    iwfm.file_test(node_file_name)
    iwfm.file_test(elem_file_name)
    iwfm.file_test(rz_file_name)
    if rz_npc_file_name:
        iwfm.file_test(rz_npc_file_name)
        iwfm.file_test(rz_pc_file_name)
        iwfm.file_test(rz_ur_file_name)
        iwfm.file_test(rz_nv_file_name)

    if rz_npc_file_name:
        rz_file_names = [rz_file_name, rz_npc_file_name, rz_pc_file_name, rz_ur_file_name, rz_nv_file_name]
    else:
        rz_file_names = [rz_file_name]

    idb.exe_time()  # initialize timer


    count = map_params_rz(node_file_name, elem_file_name, out_name, rz_file_names, 
                        format=format, point_width=point_width, verbose=verbose)
    
    print(f'  Wrote {count:,} {format.upper()} images')

    idb.exe_time()                                          # print elapsed time
