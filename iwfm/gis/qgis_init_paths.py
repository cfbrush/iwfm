# qgis_init_paths.py
# Query system and initialize QGIS paths
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

'''Initialize QGIS paths.'''
# Windows 10 paths - can they be read?
PYTHONPATH_W10 = r'C:\Programs\QGIS3.4\python'
PLUGINSPATH_W10 = r'C:\Programs\QGIS3.4\python\plugins'  # for processing module, etc
APPPATH_W10 = r'C:\Programs\QGIS3.4'

# Linux paths - can they be read?
PYTHONPATH_LIN = '--'
PLUGINSPATH_LIN = '--'  # for processing module, etc
APPPATH_LIN = '--'

# Mac paths - can they be read?
PYTHONPATH_MAC = '/Applications/QGIS3.4.app/Contents/Resources/python'
PLUGINSPATH_MAC = '/Applications/QGIS3.4.app/Contents/Resources/python/plugins'  # for processing module, etc
APPPATH_MAC = '/Applications/QGIS3.4.app/Contents/MacOS/'

'''Function definition'''


def qgis_init_paths(debug=0):  # must run this
    '''Initialize QGIS paths.

    Parameters
    ----------
    debug : int, default=0
        level of debug logging to CLI (0 = none)

    Returns
    -------
    app_path : str
        paths
    '''
    import sys
    import platform

    if debug:
        print('  => Before adding to paths:')  # debugging
        debug.print_env()  # debugging
        print('  => ---------------------------------------')  # debugging
    # -- Add QGIS paths to the shell path ----
    qos = platform.system()
    if debug:
        print('  => qos: {qos}')  # debugging
    if qos == 'Windows':  # - Windows 10 QGIS paths --
        sys.path.append(PYTHONPATH_W10)
        sys.path.append(PLUGINSPATH_W10)
        sys.path.append(APPPATH_W10)
        app_path = APPPATH_W10
    elif qos == 'Linux':  # - Linux QGIS paths --
        sys.path.append(PYTHONPATH_LIN)
        sys.path.append(PLUGINSPATH_LIN)
        sys.path.append(APPPATH_LIN)
        app_path = APPPATH_LIN
    elif qos == 'Darwin':  # - MacOS QGIS paths --
        sys.path.append(PYTHONPATH_MAC)
        sys.path.append(PLUGINSPATH_MAC)
        sys.path.append(APPPATH_MAC)
        app_path = APPPATH_MAC
    else:
        raise RuntimeError(f'qgis_init_paths() called with unsupported qos = {qos!r}')
    if debug:
        print('  => After adding to paths:')  # debugging
        debug.print_env()  # debugging
        print('  => ---------------------------------------')  # debugging
    return app_path
