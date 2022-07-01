import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

_CHANEL = 12


# Reading data from np.array file
def _get_raw_data(_path: str):
    return np.load(_path)


# Showing graphs of ECG(_plot1 - RAW file data, _plot2 - gen data)
def show_plot(_plot1: np.array, _title: str) -> None:
    plt.title(_title)
    plt.rcParams['figure.figsize'] = [20, 5]
    plt.rcParams['font.size'] = 14

    plt.plot(_plot1, 'b-', label='Raw data')
    plt.show()

    return None


# Get raw data
_ecg_raw_data = _get_raw_data("ecg_ptbxl.npy")

# Get pre-processed data from one of the signals
signals, info = nk.ecg_process(_ecg_raw_data[0][0:, _CHANEL - 1], sampling_rate=100)

df = pd.DataFrame(signals)
