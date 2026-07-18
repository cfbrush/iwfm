# iwfm_read_uz_params.py 
# Read unsaturated zone parameters from a file and organize them into lists
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

'''Read unsaturated zone parameters from a file and organize them into lists.'''

def iwfm_read_uz_params(uz_file, verbose=False):
    '''Read an IWFM Simulation Unsaturated Zone file and return a list of parameters.

    Parameters
    ----------
    uz_file : str
        IWFM Simulation Unsaturated Zone file name

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    params : list
        A list containing parameter values. It consists of 6 sublists, each representing a different parameter.


    '''
    import iwfm

    iwfm.file_test(uz_file)

    uz_dict, params = iwfm.iwfm_read_uz(uz_file, verbose=verbose)
    
    #params = [pd, pn, pi, pk, prhc, ic]
    return params

