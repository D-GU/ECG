import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

_CHANEL = 12


# Reading data from file
def _get_raw_data(_path: str):
    return np.load(_path)


def show_multiple_plots(_plots: np.array, _titles: np.array):
    plt.rcParams['figure.figsize'] = [20, 5]
    plt.rcParams['font.size'] = 14

    for plots, titles in zip(_plots, _titles):
        plt.plot(plots, label=titles)
        plt.legend(np.array(_titles))

    plt.show()


def preprocess(_ecg_signal):
    # Get preprocessed data from the signal
    _ecg_data, _ = nk.ecg_process(_ecg_signal,
                                  sampling_rate=100)

    # Get cleaned signal from the data frame, so we can find peaks
    _ecg_clean_signal = np.array(_ecg_data["ECG_Clean"])

    # Get peaks from the cleaned signal
    _instant_peaks, _r_peaks = nk.ecg_peaks(_ecg_clean_signal,
                                            sampling_rate=100,
                                            method='hamilton2002')

    # Getting the rate based on the signal peaks
    rate = nk.ecg_rate(_r_peaks, sampling_rate=100,
                       desired_length=len(_ecg_clean_signal))

    _signals = pd.DataFrame({"ECG_Raw": _ecg_signal,
                             "ECG_Clean": _ecg_clean_signal,
                             "ECG_Rate": rate})

    _info = _r_peaks

    return _signals, _info


# Get raw data
ecg_raw_data = _get_raw_data("ecg_ptbxl.npy")

# generated data
ecg_generated = nk.ecg_simulate(duration=10, sampling_rate=100)

# Take signal from data
_signal = ecg_raw_data[0][:, _CHANEL - 1]

signals, r_peaks = preprocess(_signal)

_signal_cleaned = nk.ecg_clean(_signal, sampling_rate=100)

# show_multiple_plots((_signal, _signal_cleaned), ("Raw signal", "Cleaned signal"))

# for i in range(len(info['ECG_R_Peaks']) - 1):
# print(f"R = {info['ECG_R_Peaks'][i]}, R1 = {info['ECG_R_Peaks'][i + 1]}")

# show_multiple_plots((_signal, signals['ECG_Clean']), ("r", "g"))


# nk.events_plot(info['ECG_R_Peaks'], signals['ECG_Clean'])
# print(ecg_generated)

# wd, m = hp.process(_signal, sample_rate=100)

# plt.figure(figsize=(12, 4))
# hp.plotter(wd, m)
