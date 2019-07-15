import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import psycopg2
from collections import Counter


def get_csv_list(csv_dir):
    """Input:
        csv_dir: string - the path to a directory.
    Output:
        A list containing the relative paths to every .csv file in the given
        subdirectory
    """
    try:
        dir_list = [os.path.join(csv_dir, i)
                    for i in os.listdir(csv_dir) if i[-3:]=='csv']
    except FileNotFoundError:
        print('Error in get_csv_list: given directory path does not exist.')
    # this last line is only here to make the paths shorter.
    return [os.path.relpath(i) for i in dir_list]

def make_geoid(df, c_vals=None, g='geo'):
    """This function takes a column "g" from a given dataframe which is
    formatted as:
        - "05000US"
        - followed by the 2 digit Fips State Code
        - followed by the 3 digit Fips County Code
    and it transforms the values into GEOIDs that match the map files by
    combining the state and county Fips codes.
    map files downloaded from:
        https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html
    Input:
        df: a pandas dataframe
        c_vals:
        g (string): the name of the column containing the geo data.
    Output:
        df (pandas dataframe): the dataframe given by the user, but with the
            geo column replaced with a geoid column
    """
    try:
        df['geoid'] = [i[7:13] for i in df[g]]
        df = df.drop(g, axis = 1)
        try:
            return df,np.intersect1d(c_vals,df.geoid)
        except TypeError:
            return df
    except IndexError:
        print('This file has an incorrect format')
