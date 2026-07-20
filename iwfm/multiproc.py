# multiproc.py
# spreads function across multiple cpu cores
# Copyright (C) 2020-2021 University of California
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


'''Spread a function across multiple cpu cores.'''

def multiproc(function, inputlist):
    '''Spread a function across multiple cpu cores.

    Parameters
    ----------
    function : a function

    inputlist : list
        function input list

    Returns
    -------
    results : list
        function results
    '''
    import multiprocessing as mp  

    pool = mp.Pool(processes=mp.cpu_count())  
    results = pool.map(function, inputlist)
    return results
