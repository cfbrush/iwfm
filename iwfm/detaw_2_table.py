# detaw_2_table.py
# Convert DETAW files to tables and write to text files
# Copyright (C) 2020-2021 Hydrolytics LLC
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


def detaw_2_table(dir_name, outfile_name, verbose=False, debug=0):
    """detaw_2_table() Convert DETAW files to tables and write to text files """
    import os, csv

    input_files = os.listdir(dir_name)
    out_file = open(outfile_name, "w", newline="")
    out_writer = csv.writer(out_file)

    header, data = 0, []
    for file_name in input_files:
        if file_name[0] != ".":
            file_name = os.path.join(dir_name, file_name)
            file_lines = open(file_name).read().splitlines()  # open and read input file
            if header == 0:  # first file so get header
                header = 1
                out_writer.writerow(file_lines[0].split(","))
                out_writer.writerow(file_lines[1].split(","))
            temp = []
            for line in file_lines[2:]:
                temp.append(line)
            data.append(temp)
    if verbose:
        print("  Read {} files each with {} data lines".format(len(data), len(data[0])))

    for i in range(0, len(data[0])):
        for j in range(0, len(data)):
            temp = data[j][i].split(",")
            year = temp[0]
            temp.pop(0)  # remove year
            temp.insert(0, j + 1)  # add subarea number (adjusted for zero-indexing)
            if j == 0:
                ins = year
            else:
                ins = " "
            temp.insert(0, ins)
            out_writer.writerow(temp)
    out_file.close()
    if verbose:
        print("  Wrote crop data to {} ".format(outfile_name))


if __name__ == "__main__":
    " Run detaw_2_table() from command line "
    import sys
    import iwfm.debug as idb
    import iwfm as iwfm

    if len(sys.argv) > 1:  # arguments are listed on the command line
        dir_name = sys.argv[1]
        outfile_name = sys.argv[2]
    else:  # ask for file names from terminal
        dir_name = input("Input directory name: ")
        outfile_name = input("Output file name: ")

    idb.exe_time()  # initialize timer
    detaw_2_table(dir_name, outfile_name, verbose=True)
    idb.exe_time()  # print elapsed time