import numpy as np
import string
import neurokit2 as nk


def _get_raw_data(_path: str):
    return np.load(_path)


_ecg_raw_data = _get_raw_data("ecg_ptbxl.npy")
