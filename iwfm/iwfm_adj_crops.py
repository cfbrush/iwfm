# iwfm_adj_crops.py
# Use change factors to modify IWFM land use files
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


def iwfm_adj_crops(
    in_year,
    in_zone_file,
    in_chg_file_NV,
    in_chg_file_UR,
    in_area_npag,
    in_area_nvrv,
    in_area_urban,
    out_basename,
    skip=4,
    date_head_tail=['09/30/', '_24:00'],
    verbose=False,
):
    ''' iwfm_adj_crops() - Use change factors to modify IWFM 
        land use files

    Parameters
    ----------
    in_year : str
        water year of output land use
    
    in_zone_file : str
        zones file name
    
    in_chg_file_NV : str
        Ag to Native factors file name
    
    in_chg_file_UR : str
        Ag to Urban factors file name
    
    in_area_npag : str
        Non-Ponded Ag Area file name
    
    in_area_nvrv : str
        Native and Riparian Area file name
    
    in_area_urban : str
        Urban Area file name
    
    out_basename : str
        output land use files basename
    
    skip : int, default=4
        number of non-comment lines to skip in each file (header)
    
    date_head_tail : list, default=['09/30/', '_24:00']
        info to turn in_year into a model-readable date in DSS format

    verbose: bool, default=False
        True = write to cli

    Returns
    -------
    nothing
    
    '''
    import iwfm

    elem_zones = iwfm.read_lu_change_zones(in_zone_file)

    npag_table, dates, npag_elems = iwfm.read_lu_file(in_area_npag, skip)   # read ag
    nvrv_table, _, nvrv_elems = iwfm.read_lu_file(in_area_nvrv, skip)       # read nv
    urban_table, _, urban_elems = iwfm.read_lu_file(in_area_urban, skip)    # read urban

    changes_NV = iwfm.read_lu_change_factors(in_chg_file_NV)
    changes_UR = iwfm.read_lu_change_factors(in_chg_file_UR)

    # - get column index for NV and UR factor for water year
    chg_col_nv = iwfm.get_change_col(changes_NV, in_year, in_chg_file_NV)
    chg_col_ur = iwfm.get_change_col(changes_UR, in_year, in_chg_file_UR)

    # change-factor rows keyed by zone ID (row = [zone_id, factor, factor, ...])
    changes_nv_by_zone = {row[0]: row for row in changes_NV[1:]}
    changes_ur_by_zone = {row[0]: row for row in changes_UR[1:]}

    for i in range(0, len(npag_table)):
        # map element ID to table row index for each land-use table
        ag_row = {e: n for n, e in enumerate(npag_elems[i])}
        nv_row = {e: n for n, e in enumerate(nvrv_elems[i])}
        ur_row = {e: n for n, e in enumerate(urban_elems[i])}

        for j in range(0, len(elem_zones)):  # cycle through elements in zone list
            elem, zone = elem_zones[j][0], elem_zones[j][1]
            ag2nv, ag2ur = (
                1.0 - changes_nv_by_zone[zone][chg_col_nv],
                1.0 - changes_ur_by_zone[zone][chg_col_ur],
            )  # factors for this zone

            ag = ag_row[elem]

            # reduce ag area and add to NV area
            if ag2nv < 1 and sum(npag_table[i][ag]) > 0:
                ag_start = sum(npag_table[i][ag])
                npag_table[i][ag] = [round(a * ag2nv, 2) for a in npag_table[i][ag]]
                ag_change = ag_start - sum(npag_table[i][ag])
                nv = nv_row[elem]
                nvrv_table[i][nv][0] = round(nvrv_table[i][nv][0] + ag_change, 2)

            # reduce ag area and add to Urban area
            if ag2ur < 1 and sum(npag_table[i][ag]) > 0:
                ag_start = sum(npag_table[i][ag])
                npag_table[i][ag] = [round(a * ag2ur, 2) for a in npag_table[i][ag]]
                ag_change = ag_start - sum(npag_table[i][ag])
                ur = ur_row[elem]
                urban_table[i][ur][0] = round(urban_table[i][ur][0] + ag_change, 2)

    # -- create the output file names
    out_file_ag = out_basename + '_AG_' + in_year + '.dat'
    out_file_nv = out_basename + '_NV_' + in_year + '.dat'
    out_file_ur = out_basename + '_UR_' + in_year + '.dat'

    # -- test if each output file exists, if so delete
    iwfm.file_delete(out_file_ag)
    iwfm.file_delete(out_file_nv)
    iwfm.file_delete(out_file_ur)

    years = []
    years.append(in_year)

    # -- write out new data 
    iwfm.write_lu2file(npag_table, out_file_ag, years, lu_type = 'Ag', verbose=verbose)
    iwfm.write_lu2file(nvrv_table, out_file_nv, years, lu_type = 'Native', verbose=verbose)
    iwfm.write_lu2file(urban_table, out_file_ur, years, lu_type = 'Urban', verbose=verbose)

    return 


if __name__ == '__main__':
    ' Run iwfm_adj_crops() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        in_year = sys.argv[1]
        in_zone_file = sys.argv[2]
        in_chg_file_NV = sys.argv[3]
        in_chg_file_UR = sys.argv[4]
        in_area_npag = sys.argv[5]
        in_area_nvrv = sys.argv[6]
        in_area_urban = sys.argv[7]
        out_basename = sys.argv[8]
    else:  # ask for file names from terminal
        in_year        = input('Year: ')
        in_zone_file   = input('Zone file name: ')
        in_chg_file_NV = input('Ag to Native change factors file name: ')
        in_chg_file_UR = input('Ag to Urban change factors file name: ')
        in_area_npag   = input('Input Ag file name: ')
        in_area_nvrv   = input('Input Native file name: ')
        in_area_urban  = input('Input Urban file name: ')
        out_basename   = input('Output file base name: ')

    iwfm.file_test(in_zone_file)
    iwfm.file_test(in_chg_file_NV)
    iwfm.file_test(in_chg_file_UR)
    iwfm.file_test(in_area_npag)
    iwfm.file_test(in_area_nvrv)
    iwfm.file_test(in_area_urban)

    idb.exe_time()  # initialize timer
    iwfm_adj_crops(
        in_year,
        in_zone_file,
        in_chg_file_NV,
        in_chg_file_UR,
        in_area_npag,
        in_area_nvrv,
        in_area_urban,
        out_basename,
        verbose=True,
    )  

    idb.exe_time()  # print elapsed time
