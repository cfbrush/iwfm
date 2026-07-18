# __init__.py for iwfm.debug package
# Classes, methods and functions for debugging scripts to use IWFM and IGSM files
# Copyright (C) 2018-2026 University of California
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

# program/function timer
'''Classes, methods and functions for debugging scripts to use IWFM and IGSM files.'''

from iwfm.debug.exe_time import exe_time
from iwfm.debug.print_exe_time import print_exe_time
from iwfm.debug.timer import timer

# test dictionary
from iwfm.debug.test_dict import test_dict
from iwfm.debug.print_dict import print_dict
from iwfm.debug.check_key import check_key

# logging
from iwfm.debug.logger_setup import setup_debug_logger
from iwfm.debug.logger_setup import parse_cli_flags

# system and python version information
from iwfm.debug.this_sys import this_sys
from iwfm.debug.this_sys_version import this_sys_version
from iwfm.debug.this_python import this_python
from iwfm.debug.print_env import print_env

