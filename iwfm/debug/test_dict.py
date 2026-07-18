# test_dict.py
# test that key is in dictionary, for debugging
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


'''Test that key is in dictionary, for debugging.'''

def test_dict(name, d, key):  # test dictionary
    '''Print dictionary value for key.

    Normal usage is to set name to the dictionary name so the printed output has meaning

    Parameters
    ----------
    name : str
        Name of dictionary

    d : dict
        Dictionary

    key : (any type)  
        Dictionary key value

    Return
    ------
    nothing
    '''
    
    print(f'   dictionary {name}, key: {key} returns: {d.get(key)}')
    return

