import numpy as np
import string
import neurokit2 as nk


def _get_raw_data(_path: str):
    return np.array(np.load(_path))


_ecg_raw_data = _get_raw_data("../ecg_ptbxl.npy")
_ecg = nk.ecg_simulate(duration=15, sampling_rate=1000, heart_rate=80)

signal, info = nk.ecg_process(_ecg, sampling_rate=1000)

nk.ecg_plot(signal)
