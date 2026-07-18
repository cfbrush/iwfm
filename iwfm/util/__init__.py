# __init__.py for iwfm.util package
# Classes, methods and functions to read, write and modify IWFM and IGSM files
# Copyright (C) 2018-2021 University of California
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

"""Download external data (CDEC, NWIS, USACE, USBR)."""

# -- internet functions -----------------------------------
from iwfm.util.ftp_fetch import ftp_fetch
from iwfm.util.url_fetch import url_fetch
from iwfm.util.zip_unzip import zip_unzip

# -- data download functions -----------------------------------
from iwfm.util.get_cdec import get_cdec
from iwfm.util.get_usacoe import get_usacoe
from iwfm.util.get_nwis import get_nwis
from iwfm.util.get_usbr import get_usbr
