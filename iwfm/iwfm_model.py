# iwfm_model.py
# Python class for IWFM model information
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

import iwfm
import re
from pathlib import Path
from iwfm.file_utils import read_next_line_value
from iwfm.iwfm_dataclasses import PreprocessorFiles, SimulationFiles


class IWFMModelError(Exception):
    '''Custom exception for IWFM model operations.'''
    pass


def _safe_get_filename(line, line_num, field_name='filename'):
    """Safely extract filename from line with validation.

    Parameters
    ----------
    line : str
        Line to parse
    line_num : int
        Line number for error messages
    field_name : str
        Name of field for error messages

    Returns
    -------
    str
        Filename from line

    Raises
    ------
    ValueError
        If line is empty or contains only whitespace
    """
    parts = line.split()
    if not parts:
        raise ValueError(
            f"Line {line_num}: Expected {field_name}, got empty line or whitespace"
        )
    return parts[0]


class iwfm_model:
    def __init__(self, pre_fpath, sim_file, verbose=False):
        self.mtype = 'IWFM'
        fpath_line = pre_fpath.split('\\')  # Preprocessor file path to list
        self.pre_file = fpath_line.pop(
            len(fpath_line) - 1
        )  # pop preprocessor file name from list
        self.pre_folder = Path(
            '/'.join(fpath_line)
        )  # put back together as Path object for all OSs
        self.sim_file = sim_file  # simulation file name

        if verbose:
            print('\n  Reading IWFM Files')

        # -- read preprocessor main file
        currfile = self.pre_folder / self.pre_file
        if verbose:
            print(f'    IWFM pre-processor file: \t{currfile}')
        self.read_preproc(currfile)

        # -- read preprocessor node file
        currfile = self.pre_folder / self.pre_files.node_file
        if verbose:
            print(f'    IWFM node file:          \t{currfile}')
        self.read_nodes(currfile)

        # -- read preprocessor element file
        currfile = self.pre_folder / self.pre_files.elem_file
        if verbose:
            print(f'    IWFM elements file:      \t{currfile}')
        self.read_elements(currfile)

        # -- read preprocessor stratigraphy file
        currfile = self.pre_folder / self.pre_files.strat_file
        if verbose:
            print(f'    IWFM stratigraphy file:  \t{currfile}')
        self.read_strat(currfile)

        # -- read simulation main file 
        currfile = self.sim_file
        if verbose:
            print(f'    IWFM simulation main file:\t{currfile}')
        self.read_sim(currfile)
        return


    # -- functions to return information
    def get_nlayers(self):
        return self._nlayers

    def get_lse(self):
        return getattr(self, '_lse', None)

    def aquifer_thickness(self):
        return getattr(self, 'aquifer_thick', None)

    def get_aquifer_top(self):
        return getattr(self, '_aquifer_top', None)

    def get_aquifer_bottom(self):
        return getattr(self, '_aquifer_bottom', None)

    def aquitard_thickness(self):
        return getattr(self, 'aquitard_thick', None)

    def get_aquitard_top(self):
        return getattr(self, '_aquitard_top', None)

    def get_aquitard_bottom(self):
        return getattr(self, '_aquitard_bottom', None)

    # -- the functions that do the work 
    def read_preproc(self, pre_file):
        '''Read an IWFM Preprocessor main input file, and return a list of the files called and some settings.'''
        # -- read the preprocessor file into array file_lines
        iwfm.file_test(pre_file)
        with open(pre_file, encoding='utf-8') as f:
            pre_lines = f.read().splitlines()

        _, line_index = read_next_line_value(pre_lines, -1, column=0, skip_lines=3)  # skip comments

        # -- read input file names and build PreprocessorFiles dataclass -----
        preout = _safe_get_filename(pre_lines[line_index], line_index, 'preout')

        _, line_index = read_next_line_value(pre_lines, line_index, column=0)
        elem_file = _safe_get_filename(pre_lines[line_index], line_index, 'elem_file')

        _, line_index = read_next_line_value(pre_lines, line_index, column=0)
        node_file = _safe_get_filename(pre_lines[line_index], line_index, 'node_file')

        _, line_index = read_next_line_value(pre_lines, line_index, column=0)
        strat_file = _safe_get_filename(pre_lines[line_index], line_index, 'strat_file')

        _, line_index = read_next_line_value(pre_lines, line_index, column=0)
        stream_file = _safe_get_filename(pre_lines[line_index], line_index, 'stream_file')

        _, line_index = read_next_line_value(pre_lines, line_index, column=0)
        lake_file = _safe_get_filename(pre_lines[line_index], line_index, 'lake_file')
        if lake_file[0] == '/':
            lake_file = ''

        self.pre_files = PreprocessorFiles(
            preout=preout,
            elem_file=elem_file,
            node_file=node_file,
            strat_file=strat_file,
            stream_file=stream_file,
            lake_file=lake_file,
        )
        return


    def read_sim(self, sim_file):
        '''Read an IWFM Simulation main input file, and return a SimulationFiles dataclass with the files called and some settings.'''

        iwfm.file_test(sim_file)
        with open(sim_file, encoding='utf-8') as f:
            sim_lines = f.read().splitlines()

        _, line_index = read_next_line_value(sim_lines, -1, column=0, skip_lines=3)  # skip comments

        # -- read input file names and build SimulationFiles dataclass
        preout = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'preout')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        gw_file = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'gw_file')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        stream_file = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'stream_file')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        temp = _safe_get_filename(sim_lines[line_index], line_index, 'lake_file')
        if temp[0] == '/':
            lake_file = ''
        else:
            lake_file = str(Path(temp))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        root_file = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'root_file')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        swshed_file = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'swshed_file')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        unsat_file = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'unsat_file')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        irrfrac = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'irrfrac')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        supplyadj = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'supplyadj')))

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        precip = _safe_get_filename(sim_lines[line_index], line_index, 'precip')

        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        et = str(Path(_safe_get_filename(sim_lines[line_index], line_index, 'et')))

        # -- starting date
        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        start = _safe_get_filename(sim_lines[line_index], line_index, 'start')

        # -- time step
        _, line_index = read_next_line_value(sim_lines, line_index, column=0, skip_lines=1)
        step = _safe_get_filename(sim_lines[line_index], line_index, 'step')

        # -- ending date
        _, line_index = read_next_line_value(sim_lines, line_index, column=0)
        end = _safe_get_filename(sim_lines[line_index], line_index, 'end')

        self.sim_files = SimulationFiles(
            preout=preout,
            gw_file=gw_file,
            stream_file=stream_file,
            lake_file=lake_file,
            root_file=root_file,
            swshed_file=swshed_file,
            unsat_file=unsat_file,
            irrfrac=irrfrac,
            supplyadj=supplyadj,
            precip=precip,
            et=et,
            start=start,
            step=step,
            end=end,
        )
        return


    def read_nodes(self, node_file):
        '''Read an IWFM Node file, and return a list of the nodes and their coordinates.'''

        # -- read the Node file into array file_lines
        iwfm.file_test(node_file)
        with open(node_file, encoding='utf-8') as f:
            node_lines = f.read().splitlines()

        _, line_index = read_next_line_value(node_lines, -1, column=0)  # skip comments

        self.inodes = int(re.findall(r'\d+', node_lines[line_index])[0])

        _, line_index = read_next_line_value(node_lines, line_index, column=0)  # skip comments

        parts = node_lines[line_index].split()
        if not parts:
            raise ValueError(f"{node_file} line {line_index}: Expected factor value, got empty line")
        factor = float(parts[0])  # read factor

        _, line_index = read_next_line_value(node_lines, line_index, column=0)  # skip comments

        self.d_nodes = {}  # initialize nodal info dictionary
        self.d_nodexy = {}  # initialize elemental info dictionary
        for i in range(0, self.inodes):  # read nodes information
            l = node_lines[line_index + i].split()  # get next line
            inode = int(l.pop(0))  # node number
            self.d_nodes[i] = inode
            coords = [float(s) * factor for s in l]
            self.d_nodexy[inode] = coords
        return


    def read_elements(self, elem_file):
        '''Read an IWFM Element file, and return a list of the nodes making up each element.'''
        # -- read the Element file into array file_lines
        iwfm.file_test(elem_file)
        with open(elem_file, encoding='utf-8') as f:
            elem_lines = f.read().splitlines()

        _, line_index = read_next_line_value(elem_lines, -1, column=0)

        self.elements = int(re.findall(r'\d+', elem_lines[line_index])[0])

        _, line_index = read_next_line_value(elem_lines, line_index, column=0)

        subregions = int(re.findall(r'\d+', elem_lines[line_index])[0])

        _, line_index = read_next_line_value(elem_lines, line_index, column=0)
        _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=subregions - 1)

        self.e_nos = []  # initialize list of elem nos
        self.d_elem_nodes = {}  # initialize list of elem nodes
        self.d_elem_sub = {}  # initialize list of elem subregions
        for i in range(0, self.elements):  # read element information
            l = elem_lines[line_index + i].split()  # get the next line
            this_elem = int(l.pop(0))  # element no of this element
            self.e_nos.append(this_elem)  # add element no of this element
            nodes = [int(s) for s in l]
            self.d_elem_sub[this_elem] = nodes.pop(4)  # subregion of this element
            if nodes[3] == 0:
                nodes.pop(3)  # remove empty node on triangles
            self.d_elem_nodes[this_elem] = nodes  # nodes of this element
        self.elems2poly()  # build polygons
        return


    def read_chars(self, char_file, elem_nodes):
        '''Read an IWFM Element Characteristics file and return a list of characteristics for each element.'''

        iwfm.file_test(char_file)
        with open(char_file, encoding='utf-8') as f:
            char_lines = f.read().splitlines()

        _, char_index = read_next_line_value(char_lines, -1, column=0)  # skip comments
        self.elem_char = []
        for i in range(0, len(elem_nodes)):
            l = char_lines[char_index + i].split()
            l.pop(0)  # element ID
            chars = []
            chars.append(int(l.pop(0)))  # rain station
            chars.append(float(l.pop(0)))  # rain factor
            chars.append(int(l.pop(0)))  # drainage
            chars.append(int(l.pop(0)))  # subregion
            l.pop(0)  # don't use
            chars.append(float(l.pop(0)))  # soil type
            self.elem_char.append(chars)
        return


    def read_lake_pre(self, lake_file):
        '''Read an IWFM Lake file and return (a) a list of elements and (b) a list of properties for each lake.'''
        iwfm.file_test(lake_file)
        with open(lake_file, encoding='utf-8') as f:
            lake_lines = f.read().splitlines()
        _, lake_index = read_next_line_value(lake_lines, -1, column=0)  # skip comments
        parts = lake_lines[lake_index].split()
        if not parts:
            raise ValueError(f"{lake_file} line {lake_index}: Expected number of lakes, got empty line")
        self.nlakes = int(parts[0])
        self.lakes = []
        self.lake_elems = []
        for i in range(0, self.nlakes):
            _, lake_index = read_next_line_value(lake_lines, lake_index, column=0)  # skip comments
            l = lake_lines[lake_index].split()  # read first line of lake description
            lake_id = int(l.pop(0))
            max_elev = float(l.pop(0))
            next = int(l.pop(0))
            nelem = int(l.pop(0))
            self.lakes.append([lake_id, max_elev, next, nelem])
            for j in range(0, nelem):
                e = []
                if j > 0:  # need to read next line
                    _, lake_index = read_next_line_value(lake_lines, lake_index, column=0)
                    l = lake_lines[lake_index].split()  # get next line
                e.append(lake_id)  # lake number
                e.append(int(l[0]))  # element number
                self.lake_elems.append(e)
        return


    def read_streams_pre(self, stream_file):
        '''Read an IWFM Stream Geometry file and compile a list of stream reaches and (b) a dictionary of stream nodes, and return the number of stream nodes.'''
        iwfm.file_test(stream_file)
        with open(stream_file, encoding='utf-8') as f:
            stream_lines = f.read().splitlines()

        _, stream_index = read_next_line_value(stream_lines, -1, column=0)
        parts = stream_lines[stream_index].split()
        if not parts:
            raise ValueError(f"{stream_file} lineine {stream_index}: Expected number of reaches, got empty line")
        self.nreach = int(parts[0])  # no reaches

        stream_index += 1
        parts = stream_lines[stream_index].split()
        if not parts:
            raise ValueError(f"{stream_file} line {stream_index}: Expected rating table count, got empty line")
        self.n_rating = int(parts[0])

        self.sreach_list = []
        snodes_list = []
        for i in range(0, self.nreach):  # cycle through stream reaches
            # read reach information
            _, stream_index = read_next_line_value(stream_lines, stream_index, column=0)
            l = stream_lines[stream_index].split()
            # streams package version 4.2
            reach = int(l.pop(0))
            snodes = int(l.pop(0))

            # ** FUTURE ** modify to work with all versions of stream package
            # streams package version 5
            # upper = int(l.pop(0))
            # lower = int(l.pop(0))
            # snodes = lower - upper + 1

            oflow = int(l.pop(0))
            # read stream node information
            for j in range(0, snodes):
                _, stream_index = read_next_line_value(stream_lines, stream_index - 1, column=0, skip_lines=1)
                l = stream_lines[stream_index].split()
                t = [int(l[0]), int(l[1]), reach]  #  snode, GW Node, reach
                snodes_list.append(t)
                if j == 0:
                    upper = int(l[0])
                else:
                    lower = int(l[0])
            self.sreach_list.append([reach, upper, lower, oflow])

        _, stream_index = read_next_line_value(stream_lines, stream_index, column=0, skip_lines=3)
        selev = []
        for i in range(0, len(snodes_list)):
            l = stream_lines[stream_index].split()
            selev.append(float(l[1]))
            stream_index = stream_index + self.n_rating
            if i < len(snodes_list) - 1:  # stop at end
                _, stream_index = read_next_line_value(stream_lines, stream_index - 1, column=0)

        # put stream node info into a dictionary
        self.stnodes_dict = {}
        for i in range(0, len(snodes_list)):
            j = 0
            while snodes_list[j][0] != i + 1:  # find info for i in snodes list
                j += 1
            key, values = i + 1, [
                snodes_list[j][1],
                snodes_list[j][2],
                selev[i],
            ]  # key = snode, values = GW Node, Reach, Bottom
            self.stnodes_dict[key] = values
        return len(snodes_list)


    def read_strat(self, strat_file):

        iwfm.file_test(strat_file)
        with open(strat_file, encoding='utf-8') as f:
            strat_lines = f.read().splitlines()

        _, line_index = read_next_line_value(strat_lines, -1, column=0)  # skip comments

        _, line_index = read_next_line_value(strat_lines, line_index, column=0)  # skip comments
        factor = float(re.findall(r'[-+]?\d*\.?\d+', strat_lines[line_index])[0])  # read factor

        _, line_index = read_next_line_value(strat_lines, line_index, column=0)  # skip comments
        self.strat = []  # initialize list
        for i in range(0, len(self.d_nodes)):
            l = strat_lines[line_index + i].split()
            s = []  # initialize accumulator
            s.append(int(l.pop(0)))  # node no
            for j in range(0, len(l)):
                s.append(factor * float(l.pop(0)))  # lse, etc as floats
            self.strat.append(s)

        self._nlayers = int((len(self.strat[0]) - 1) / 2)
        self.elevation = [i[0] for i in self.strat]

        self.d_nodeelev = {}
        for i in range(0, len(self.strat)):  # cycle through stratigraphy of each node
            l = self.strat[i]

            this_node = l.pop(0)
            lse = l.pop(0)

            depth = 0
            n_strat = []
            n_strat.append(lse)
            for j in range(0, self._nlayers):  # cycle through layers for each node
                t = l.pop(0)  # thickness of aquitard
                depth += t  # add to total depth
                n_strat.append(lse - depth)  # bottom of aquitard/top of aquifer
                a = l.pop(0)  # thickness of aquifer
                depth += a  # add to total depth
                n_strat.append(lse - depth)  # bottom of aquifer/top of next aqiutard
            self.d_nodeelev[this_node] = n_strat
        return


    def elems2poly(self):
        '''Compile a dictionary of model elements as shapely polygons.'''
        from shapely.geometry import Point, Polygon

        self.d_elem_polys = {}
        for key in self.d_elem_nodes:  # for each element ...
            elem = key
            nodes = self.d_elem_nodes[key]

            coords = []
            for node in nodes:  # for each node in the element ...
                # tuple of (x,y) coordinates
                coords.append(Point(self.d_nodexy[node][0], self.d_nodexy[node][1]))  
            # close the polygon
            coords.append(Point(self.d_nodexy[nodes[0]][0], self.d_nodexy[nodes[0]][1]))

            new_poly = Polygon([[p.x, p.y] for p in coords])
            self.d_elem_polys[elem] = new_poly  # list of coords for all elements
        return


    def point_in_elem(self, x, y):
        '''Return the element number if the point (x,y) is in an element, 0 otherwise.'''
        from shapely.geometry import Point

        p = Point(x, y)
        for key in self.d_elem_polys:  # for each element ...
            elem = key
            if p.within(self.d_elem_polys[elem]):
                return elem
        return 0

    def elem_coords(self):
        '''Return a list of coordinates of an element [[x0,y0],[x1,y1],[x2,y2]<,...>].'''
        polys = []
        for i in range(0, len(self.elem_nodes)):  # for each element ...
            coords = []
            # for each node in the element ...
            for j in range(0, len(self.elem_nodes[i])):  
                coords.append(
                    (
                        self.node_coords[self.elem_nodes[i][j] - 1][0],
                        self.node_coords[self.elem_nodes[i][j] - 1][1],
                    )
                )
            coords.append(
                (
                    self.node_coords[self.elem_nodes[i][0] - 1][0],
                    self.node_coords[self.elem_nodes[i][0] - 1][1],
                )
            )  # close the polygon
            polys.append(coords)
        return polys
