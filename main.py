import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

_CHANEL = 12


# Reading data from np.array file
def _get_raw_data(_path: str):
    return np.load(_path)


# Showing graphs of ECG(_plot1 - RAW file data, _plot2 - gen data)
def show_plot(_plot1: np.array, _plot2: np.array, _title: str) -> None:
    plt.rcParams['figure.figsize'] = [20, 5]
    plt.rcParams['font.size'] = 14

    plt.plot(_plot1, 'b-', label='Raw data')
    plt.plot(_plot2, 'r-', label='Clean data')
    plt.legend(["Raw data", "Clean data"])
    plt.show()

    return None


def show_multiple_plots(_plots: np.array, _titles: np.array):
    plt.rcParams['figure.figsize'] = [20, 5]
    plt.rcParams['font.size'] = 14

    for plots, titles in zip(_plots, _titles):
        plt.plot(plots, label=titles )
        plt.legend(np.array(_titles))

    plt.show()


# Get raw data
_ecg_raw_data = _get_raw_data("ecg_ptbxl.npy")

# generated data
_ecg_generated = nk.ecg_simulate(duration=10, sampling_rate=100)

# Get pre-processed data from one of the signals
signals, info = nk.ecg_process(_ecg_raw_data[0][0:, _CHANEL - 1], sampling_rate=100)

# Get cleaned signal
_ecg_clean_data = np.array(signals["ECG_Clean"])

df = pd.DataFrame(signals)

_plots = np.array((_ecg_raw_data[0][0:, _CHANEL - 1], _ecg_clean_data))
_titles = np.array(("Raw data", "Clean data"))

show_multiple_plots(_plots, _titles)
