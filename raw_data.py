from pandas import DataFrame
from numpy import load


# Reading data from file
def get_raw_data(_path: str):
    return load(_path)


# Get raw data
ecg_raw_data = get_raw_data("ecg_ptbxl.npy")
