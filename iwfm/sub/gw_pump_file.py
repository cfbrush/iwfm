# sub_gw_pump_file.py
# Copies the old groundwater pumping main file and replaces the contents 
# with those of the new submodel, and writes out the new file
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


'''Read the original groundwater main pumping file, determine which pumping components are in the submodel, and write out a new file.'''

def sub_gw_pump_file(old_filename, sim_files_new, elems, bounding_poly, base_path=None, verbose=False):
    '''Read the original groundwater main pumping file, determine which pumping components are in the submodel, and write out a new file.

    Parameters
    ----------
    old_filename : str
        name of existing groundwater pumping main file

    sim_files_new : SimulationFiles
        new submodel file names

    elems : list of ints
        list of existing model elements in submodel

    bounding_poly : shapely.geometry Polygon
        submodel boundary from model nodes

    base_path : Path, optional
        base path for resolving relative file paths

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered sub_gw_pump_file() with {old_filename}")

    # Check if pumping file exists using iwfm utility
    iwfm.file_test(old_filename)

    with open(old_filename, encoding='utf-8') as f:
        pump_lines = f.read().splitlines()
    pump_lines.append('')

    # -- file names --

    # well specification file
    well_file, line_index = read_next_line_value(pump_lines, -1)
    have_well = True
    if well_file[0] == '/':
        have_well = False
    else:
        well_file = well_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            well_file = str(base_path / well_file)
        pump_lines[line_index] = '   ' + sim_files_new.well_file + '\t\t        / WELLFL'
    well_index = line_index  # in case no wells in submodel, return and set blank file name

    # element pumping file
    epump_file, line_index = read_next_line_value(pump_lines, line_index)
    have_epump = True
    if epump_file[0] == '/':
        have_epump = False
    else:
        epump_file = epump_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            epump_file = str(base_path / epump_file)
        pump_lines[line_index] = '   ' + sim_files_new.epump_file + '\t\t        / ELEMPUMPFL'
    epump_index = line_index  # in case no element pumping in submodel, return and set blank file name

    # pumping rates file
    prate_file, line_index = read_next_line_value(pump_lines, line_index)
    if prate_file[0] != '/':
        prate_file = prate_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            prate_file = str(base_path / prate_file)
        pump_lines[line_index] = '   ' + sim_files_new.prate_file + '\t\t        / PUMPFL'


    # -- modify other pumping files for submodel
    if have_well:                                   # process well specification file
        have_well = iwfm.sub_gw_pump_well_file(well_file, sim_files_new.well_file, elems, bounding_poly, verbose)
    if not have_well:
        pump_lines[well_index] = '                                          / WELLFL'


    if have_epump:                                  # process element pumping file
        have_epump = iwfm.sub_gw_pump_epump_file(epump_file, sim_files_new.epump_file, elems, verbose)
    if not have_epump:
        pump_lines[epump_index] = '                                         / ELEMPUMPFL'

    # -- write out the modified pumping file
    with open(sim_files_new.pump_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(pump_lines))

    if verbose:
        print(f'      Wrote pumping main file {sim_files_new.pump_file}')
        print("Leaving sub_gw_pump_file()")

    return
