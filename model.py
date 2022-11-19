""" RTM data plotter script

This script is a simple plotting tool for RTM data provided to it in form of a
(.csv)-file

This file can also be imported as a module and contains the following functions
and class:
    * get_data_from_scan
    * plot_3d
    * plot_single_scan
    * plotter

Examples of Usage:

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

import numpy as np
import warnings

from typing import List, Optional


class Model:

    def get_data_from_scan(self, csv_file: str, exclude_extremes: Optional[bool] = True,
                           scan_length_x: Optional[int] = 200) -> List:
        """Gets the data from the (.csv)-file and reforms it. So it can be used for
        a 3D contour plot, it then returns a list containing the x, y and z
        component as numpy arrays

        Parameters
        ----------
        csv_file: str
            The path to the (.csv)-file
        exclude_extremes: bool, optional
            If 'True' replaces extreme values with the median value to make the
            plot look better
        scan_length_x: int, optional
            The index/length after the STM starts a new x-axis for the next 3D
            measurement (important for the refactoring so the 2D-numpy arrays for
            the plot can be generated from the .csv)-file

        Returns
        -------
        List
            A list containing 2D-np.ndarrays containing the x, y and z
            information
        """
        break_line = None

        x, y, z = map(lambda n: np.array(n).astype(int),
                      map(list, zip(*np.genfromtxt(csv_file, delimiter=";"))))

        for i, o in enumerate(x):
            if i % scan_length_x == 0:
                if o in [0, scan_length_x - 1]:
                    break_line = i
                if o not in [0, scan_length_x - 1]:
                    warnings.warn(f"From line {i} datastructure is not of form [0," 
                                  f" {scan_length_x - 1}] in x anymore... " 
                                  f" Values from then on will be discarded")
                    break

        if break_line != x.shape[0]:
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
