# seek_proc.py
# IWFM DLL: check to see if IWFM procedure is available in user's version of IWFM DLL
# Copyright (C) 2021 University of California
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

def seek_proc(iwfm_dll, seek_proc):
    '''IWFM DLL: check to see if IWFM procedure is available in user's version of IWFM DLL.

    Parameters
    ----------
    iwfm_dll :  IWFM DLL object
        instantiated IWFM DLL object

    seek_proc : str
        name of procedure


    Returns
    -------
    nothing
    '''

    if not hasattr(iwfm_dll, seek_proc):
        raise AttributeError(f'\n\t ** IWFM DLL does not have the "{seek_proc}" procedure.\n\t ** Check for an updated version of the DLL')
