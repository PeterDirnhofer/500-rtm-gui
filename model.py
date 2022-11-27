""" RTM data plotter script
License:
    Copyright (C) 2022 Marten Scheuck

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import gc

import numpy as np
import pandas as pd
import warnings
import csv
from typing import List, Optional
from configurations import *


class Model:
    data_sets_received = 0
    scan_file = None
    data_frame = None
    writer = None

    @staticmethod
    def get_data_from_scan(csv_file: str, exclude_extremes: Optional[bool] = True,
                           scan_length_x: Optional[int] = 200) -> List:
        """Gets the data from the (.csv)-file and reforms it. So it can be used for
        a 3D contour plot, it then returns a list containing the x, y and z
        component as numpy arrays

        :param csv_file: The path to the (.csv)-file
        :param exclude_extremes: If 'True' replaces extreme values with the median value to make the
            plot look better
        :param scan_length_x: The index/length after the STM starts a new x-axis for the next 3D
            measurement (important for the refactoring so the 2D-numpy arrays for
            the plot can be generated from the .csv)-file
        :return: A list containing 2D-np.ndarrays containing the x, y and z
            information
        """

        break_line = None  # last valid line

        x, y, z = map(lambda n: np.array(n).astype(int),
                      map(list, zip(*np.genfromtxt(csv_file, delimiter=";"))))

        # Plausibility check. After scan_length x must be 0 or scan_length-1.
        # break_line contains last valid line
        for i, o in enumerate(x):
            if i % scan_length_x == 0:
                if o in [0, scan_length_x - 1]:
                    break_line = i
                if o not in [0, scan_length_x - 1]:
                    warnings.warn(f"From line {i} datastructure is not of form [0,"
                                  f" {scan_length_x - 1}] in x anymore... "
                                  f" Values from then on will be discarded")
                    break

        # If last line not reached, then use only data from start to break_line.
        # new_dimension 0 number of valid datasets from beginning
        if break_line != x.shape[0]:
            h1 = x[:break_line].shape[0]
            new_dimensions = x[:break_line].shape[0] // scan_length_x
            x, y, z = map(lambda n: n[:break_line], [x, y, z])
        else:
            if x.shape[0] % scan_length_x != 0:

                raise IOError(f"The input (.csv)-file is not of the right form"
                              f" for the given scan length: {scan_length_x}")
            else:
                new_dimensions = x.shape[0] // scan_length_x

        x, y, z = map(lambda n: n.reshape(new_dimensions, scan_length_x), [x, y, z])

        if exclude_extremes:
            ind_max = np.where(z.copy() / np.mean(z) > 1.)
            z[ind_max] = np.median(z).astype(int)
            warnings.warn(f"Replaced extreme values at indices {ind_max}, with the"
                          f" median value {np.median(z).astype(int).astype(int)}",
                          category=Warning)
            warnings.warn("CAUTION: The inserted values may lead to wrong"
                          " estimations of the surface profile",
                          category=FutureWarning)
        print("Refactoring (.csv)-file into dictionary done!")
        return [x, y, z]

    @classmethod
    def clear_data_frame(cls):
        try:
            del cls.data_frame
            gc.collect()
        finally:
            cls.data_frame = pd.DataFrame(columns=['X', 'Y', 'Z'])


    @classmethod
    def write_to_file(cls, ln: str):
        # DATA,X,Y,Z
        s_split = ln.split(",")
        if len(s_split) == 4:
            cls.data_frame.loc[len(cls.data_frame.index)] = [s_split[1],s_split[2],s_split[3]]
            if s_split[1] == '0':
                cls.data_sets_received += 1
                return
            return

        if s_split[1] != 'DONE':
            # ERROR

            return

        cls.data_frame.to_csv(SCAN_FILE_NAME,index=false,sep=',')











