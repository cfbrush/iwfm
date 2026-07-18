# closest_list.py
# Given two lists A[] and B[] of form (ID, X, Y), returns a list of len(A)
# with the item of B closest to each item in A
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


'''Given two lists A[] and B[] of form (ID, X, Y), returns a list of len(A) with the item of B closest to each item in A.'''

def closest_list(A, B, verbose=False):
    '''Given two lists A[] and B[] of form (ID, X, Y), return a list of len(A) with the item of B closest to each item in A.

    Parameters
    ----------
    A : list
        Each list item contains [id, x, y]
            id : int
            x, y: float

    B : list
        Each list item contains [id, x, y, ...]
            id : int
            x, y: float
            ...: any number and type of values

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    C : list
        Each list item contains [id,x,y,...]
            id : int, id from A
            x, y: float, x,y from A
            ...: items [3:] of B from point closest to A point
    '''
    C = []
    for a in A:
        C.append(nearest(a, B))
    return C


def nearest(a, B):
    '''Item of B[points] nearest to point a.

    Parameters
    ----------
        a: [id, x,y] where id: int, x, y: float

        B: list of [id, x, y] where id: int, x,y: float 

    Returns
    -------
        index of point in B closest to a
    '''
    import math
    close_dist = float('inf')
    close_index = -1

    a = a.split(',')

    ax = float(a[1])
    ay = float(a[2])
    for i in range(len(B)):
        b = B[i].split(',')
        x, y = float(b[1]), float(b[2])
        dist = math.sqrt( (x - ax)**2 + (y - ay)**2 )
        if dist < close_dist:
            close_dist = dist
            close_index = i

    c = []
    for item in a:
        c.append(item)
    for item in B[close_index].split(','):
        c.append(item)

    return c


if __name__ == "__main__":
    " Run closest_list() from command line "
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        inpfile_1 = sys.argv[1]
        inpfile_2 = sys.argv[2]
        outfile = sys.argv[3]
    else:  # ask for file names from terminal
        inpfile_1 = input('Name of file containing 1st set of points: ')
        inpfile_2 = input('Name of file containing 2nd set of points: ')
        outfile = input('Output file name: ')

    iwfm.file_test(inpfile_1)
    with open(inpfile_1, encoding='utf-8') as f:
        file_lines = f.read().splitlines()
    header = file_lines[0][1:]
    A = file_lines[1:]  # split off header

    iwfm.file_test(inpfile_2)
    with open(inpfile_2, encoding='utf-8') as f:
        file_lines = f.read().splitlines()
    header = ','.join([header, file_lines[0][1:]])
    B = file_lines[1:]  # split off header

    idb.exe_time()  # initialize timer
    C = closest_list(A, B, verbose=verbose)


    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(header+'\n')
        for c in C:
            c = ','.join(c) + '\n'
            f.write(c[:])
    print(f'  Wrote output file {outfile}')
    idb.exe_time()  # print elapsed time
