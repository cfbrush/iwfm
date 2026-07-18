# cfs2afd.py
# Convert cubic feet per second to acre-feet per day
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


def cfs2afd(cfs):
    '''Convert flow in CFS to daily volume in Acre-Feet.

    Parameters
    ----------
    cfs : float
        Value in cubic feet per minute

    Returns
    -------
    afd : float
        Value in acre-feet per day
    '''
    return cfs * 1.983


if __name__ == "__main__":
    " Run cfs2afd() from command line "
    import sys
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # argument is listed on the command line
        cfs = sys.argv[1]
    else:  # ask for argument from terminal
        cfs = input('Value in CFS: ')

    afd = cfs2afd(float(cfs))

    print(f'  {cfs} cfs = {afd} afd')

