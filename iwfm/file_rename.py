# file_rename.py
# Rename file
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


'''Rename file.'''

from iwfm.debug.logger_setup import logger

def file_rename(filename, newname, force=0):
    '''Rename a file.

    Parameters
    ----------
    filename : str
        name of existing file

    newname : str
        new name for existing file

    force : int, default=0
        0 = don't force overwrite if another file named newname
                already exists
        1 = force overwrite if another file named newname
                already exists

    Returns
    -------
    nothing
    '''
    import os

    if os.path.isfile(newname):  # if file newname already exists
        if force:  # if force>0 then remove
            try:
                os.remove(newname)
            except (PermissionError, OSError) as e:
                logger.error(f'file_rename: failed to remove existing {newname}: {e}')
                raise
            logger.debug(f'file_rename: removed existing {newname} (force mode)')
        else:
            raise FileExistsError(
                f'Cannot rename {filename} to {newname}: destination already exists')
    try:
        os.rename(filename, newname)
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f'file_rename: failed to rename {filename} to {newname}: {e}')
        raise
    logger.debug(f'file_rename: renamed {filename} to {newname}')
