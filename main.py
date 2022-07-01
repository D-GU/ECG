import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt


# Reading data from np.array file
def _get_raw_data(_path: str):
    return np.load(_path)


# Showing graphs of ECG(_plot1 - RAW file data, _plot2 - gen data)
def show_plot(_plot1: np.array, _plot2: np.array, _title: str) -> None:
    chanel = 12
    plt.title(_title)
    plt.rcParams['figure.figsize'] = [20, 5]
    plt.rcParams['font.size'] = 14

    plt.plot(_plot1[0][0::, chanel - 1], 'b-', label='Raw data')
    plt.plot(_plot2, 'r-', label='Generated data')

    plt.show()
    return None


_ecg_raw_data = _get_raw_data("/home/forest/Developer/Python Development/ECG/ecg_ptbxl.npy")
ecg12 = nk.ecg_simulate(duration=10, sampling_rate=100)

signals, info = nk.ecg_process(ecg12, sampling_rate=100)

show_plot(_ecg_raw_data, ecg12, "Plots")
