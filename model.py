
import numpy as np
import warnings
import matplotlib.pyplot as plt

from scipy import interpolate
from pathlib import Path
from matplotlib import cm
from typing import Any, Dict, List, Union, Optional



class Model:
    def __init__(self):
        self.__file = "plot_data/newScan.csv"
        pass

    def get_data_from_scan(self, csv_file: str, exclude_extrems: Optional[bool] = True,
                           scan_length_x: Optional[int] = 200) -> List:
        """Gets the data from the (.csv)-file and reforms is so it can be used for
        a 3D contour plot, it then returns a list containing the x, y and z
        component as numpy arrays

        Parameters
        ----------
        csv_file: str
            The path to the (.csv)-file
        exclude_extrems: bool, optional
            If 'True' replaces extreme values with the median value to make the
            plot look better
        scan_length_x: int, optional
            The index/length after the STM starts a new x-axis for the next 3D
            measurement (important for the refactoring so the 2D-numpy arrays for
            the plot can be generated from the (.csv)-file

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
                    warnings.warn(f"From line {i} datastructure is not of form [0," \
                                  f" {scan_length_x - 1}] in x anymore... " \
                                  f" Values from then on will be discarded")
                    break

        if break_line != x.shape[0]:
            new_dimensions = x[:break_line].shape[0] // scan_length_x
            x, y, z = map(lambda n: n[:break_line], [x, y, z])
        else:
            if x.shape[0] % scan_length_x != 0:

                raise IOError(f"The input (.csv)-file is not of the right form" \
                              f" for the given scan length: {scan_length_x}")
            else:
                new_dimensions = x.shape[0] // scan_length_x

        x, y, z = map(lambda n: n.reshape(new_dimensions, scan_length_x), [x, y, z])

        if exclude_extrems:
            ind_max = np.where(z.copy() / np.mean(z) > 1.)
            z[ind_max] = np.median(z).astype(int)
            warnings.warn(f"Replaced extreme values at indices {ind_max}, with the" \
                          f" median value {np.median(z).astype(int).astype(int)}",
                          category=Warning)
            warnings.warn("CAUTION: The inserted values may lead to wrong" \
                          " estimations of the surface profile",
                          category=FutureWarning)
        print("Refactoring (.csv)-file into dictionary done!")
        return [x, y, z]




