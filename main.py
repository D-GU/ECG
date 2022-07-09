import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

CHANEL = 12


# Reading data from file
def get_raw_data(_path: str):
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
                                            sampling_rate=100)

    # Getting the rate based on the signal peaks
    _rate = nk.ecg_rate(_r_peaks, sampling_rate=100,
                        desired_length=len(_ecg_clean_signal))

    _signals = pd.DataFrame({"ECG_Raw": _ecg_signal,
                             "ECG_Clean": _ecg_clean_signal,
                             "ECG_Rate": _rate})

    _info = _r_peaks

    return _signals, _info


def get_r_r_interval(_r_peaks: np.array) -> np.array:
    return np.array(
        [(60000 / np.abs(_r_peaks[i] - _r_peaks[i + 1]) / 1000) for i in range(len(_r_peaks) - 1)]
    )


def get_interval(_x_peaks: np.array, _y_peaks: np.array):
    return np.array(
        [(60000 / np.abs(_x_peaks[i] - _y_peaks[i]) / 1000) for i in range(len(_y_peaks))]
    )


def get_heart_cycle(_heart_rate: np.array):
    return 60 / np.mean(_heart_rate)


def get_qst_peaks(_cleaned_signal: np.array, _r_peaks: np.array):
    # Calculate and show QRS TP complex
    _signals, _waves_peak = nk.ecg_delineate(
        _cleaned_signal,
        rpeaks=_r_peaks,
        sampling_rate=100,
        method='dwt',
        show=True,
        show_type='peaks'
    )

    return _signals, _waves_peak


# Get raw data
ecg_raw_data = get_raw_data("ecg_ptbxl.npy")

# generated data
ecg_generated = nk.ecg_simulate(duration=10, sampling_rate=100)

# Take signal from data
raw_signal = ecg_raw_data[0][:, 0]

# Get preprocessed data, such as cleaned signal, R-Peaks etc
signals, info = preprocess(raw_signal)

# Cleaned ECG signal
clean_signal = signals['ECG_Clean']

# Get R-Peaks
r_peaks = info['ECG_R_Peaks']

# Get Q-Peaks, S-Peaks, T-Peaks
_, all_peaks = get_qst_peaks(raw_signal, r_peaks)

df = pd.DataFrame({
    "ECG_Q_Peaks": all_peaks['ECG_Q_Peaks'],
    "ECG_T_Peaks": all_peaks['ECG_T_Peaks'],
    "ECG_S_Peaks": all_peaks['ECG_S_Peaks'],
    "ECG_P_Peaks": all_peaks['ECG_P_Peaks']}
)

# Get heart rate and heart cycle
heart_rate = signals["ECG_Rate"]
heart_cycle = get_heart_cycle(heart_rate)

# Get r-r intervals in ms
r_r_intervals = get_r_r_interval(r_peaks)

# Get mean r-r value
r_r_mean = np.mean(r_r_intervals)

t_peaks = all_peaks['ECG_T_Peaks']
p_peaks = all_peaks['ECG_P_Peaks']
q_peaks = all_peaks['ECG_Q_Peaks']

t_rate = nk.signal_rate(t_peaks, sampling_rate=100)
p_rate = nk.signal_rate(p_peaks, sampling_rate=100)
q_rate = nk.signal_rate(q_peaks, sampling_rate=100)

t_period = nk.signal_period(t_peaks, sampling_rate=100)
p_period = nk.signal_period(p_peaks, sampling_rate=100)
q_period = nk.signal_period(q_peaks, sampling_rate=100)

qt = get_interval(t_peaks, q_peaks)