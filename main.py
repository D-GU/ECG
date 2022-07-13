import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

CHANEL = 12


# Reading data from file
def get_raw_data(_path: str):
    return np.load(_path)


def preprocess(_ecg_signal):
    """
    Processing the signal to get first pieces of data to analyze

    parameter:
        _ecg_signal: Raw ecg signal

    returns:
        _signals: A data frame containing information about the signal
            ECG_Clean: Clean ECG signal
            ECG_Rate: Heart rate that been found on each beat
            ECG_Raw: Raw ECG signal

        _info: A dictionary containing info about R peaks
    """
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


def get_intervals(_x_peaks: np.array, _interval_name: str, *_y_peaks: np.array):
    """
    Calculating interval longevity between peaks

    parameters:
        _x_peaks: The start of the interval
        _interval_name: String, that represents the name of the interval
        _y_peaks: The end of the interval, use if you need to calculate any interval but RR

    return:
        an array of change between peaks

    """
    if _interval_name.lower() in ["rr", "r-r", "r_r"]:
        return np.array(
            [np.abs(_x_peaks[i] - _x_peaks[i + 1]) for i in range(len(_x_peaks) - 1)]
        )
    else:
        return np.array(
            [np.abs(_x_peaks[i] - _y_peaks[i]) for i in range(len(_x_peaks))]
        )


def get_heart_cycle(_heart_rate: np.array):
    """
    Calculate heart cycle. The cardiac cycle is a series of electrical and mechanical events
    that occur during the phases of heart relaxation (diastole) and contraction (systole)

    parameter:
        _heart_rate: Heart rate, that been found within each beat

    return:
        _heart_cycle = 60 / np.mean(_heart_rate)
    """
    return 60 / np.mean(_heart_rate)


def get_qst_peaks(_cleaned_signal: np.array, _r_peaks: np.array):
    """
    Calculate and show QRS TP complexes

    parameter:
        _cleaned_signal: Clean ECG signal data
        _r_peaks: R peaks that been found while preprocessing the data

    returns:
        _waves_peak: A dict containing main peaks information
        _signal: A data frame containing main peaks information
    """
    _signals, _waves_peak = nk.ecg_delineate(
        _cleaned_signal,
        rpeaks=_r_peaks,
        sampling_rate=100,
        method="dwt",
        show=True,
        show_type="peaks"
    )

    return _signals, _waves_peak


def get_pct_change(peaks: np.array):
    """
    Percentage change between cur and prev element

    parameters:
        peaks: an array of peaks

    return:
        array: array of pct changes
    """
    return pd.Series(peaks).pct_change()


def get_mech_systole(_qt: np.array, _heart_cycle: np.float64, _gen: str):
    """
    Calculating the Mechanic systole coefficient using
    Bazzet's formula

    parameters:
        _qt: An QT interval (array)
        _heart_cycle: Constant, representing heart cycle

    return:
        array: array of MS coefficients
    """
    _k_const = {
        "man": 0.37,
        "men": 0.37,
        "woman": 0.4,
        "women": 0.4
    }

    return np.array(
        [interval / (_k_const[_gen] * np.sqrt(heart_cycle)) for interval in _qt]
    )


# Get raw data
ecg_raw_data = get_raw_data("ecg_ptbxl.npy")

# generated data
ecg_generated = nk.ecg_simulate(duration=10, sampling_rate=100)

# Take signal from data. Taking this lead(I) for tests and examples
raw_signal = ecg_raw_data[0][:, 0]

# Get preprocessed data, such as cleaned signal, R-Peaks etc
signals, info = preprocess(raw_signal)

# Cleaned ECG signal
clean_signal = signals["ECG_Clean"]

# Get R-Peaks
r_peaks = info["ECG_R_Peaks"]

# Get Q-Peaks, S-Peaks, T-Peaks
_, all_peaks = get_qst_peaks(raw_signal, r_peaks)

df = pd.DataFrame({
    "ECG_Q_Peaks": all_peaks["ECG_Q_Peaks"],
    "ECG_T_Peaks": all_peaks["ECG_T_Peaks"],
    "ECG_S_Peaks": all_peaks["ECG_S_Peaks"],
    "ECG_P_Peaks": all_peaks["ECG_P_Peaks"]}
)

# Get heart rate and heart cycle
heart_rate = signals["ECG_Rate"]
heart_cycle = get_heart_cycle(heart_rate)

# Get Q, R, S, P peaks
q_peaks = np.array([peak / 100 for peak in all_peaks["ECG_Q_Peaks"]])
r_peaks = np.array([peak / 100 for peak in info["ECG_R_Peaks"]])
s_peaks = np.array([peak / 100 for peak in all_peaks["ECG_S_Peaks"]])
p_peaks = np.array([peak / 100 for peak in all_peaks["ECG_P_Peaks"]])

# Get T peaks + T period
t_peaks = np.array([peak / 100 for peak in all_peaks["ECG_T_Peaks"]])
t_peaks += nk.signal_period(t_peaks, sampling_rate=100)

# Get main intervals lengths (use mean in future analysis)
qt_interval = get_intervals(q_peaks, "qt", *t_peaks)
pq_interval = get_intervals(p_peaks, "pq", *q_peaks)
rr_interval = get_intervals(r_peaks, 'rr')

# Get QRS complex length and mechanic systole coefficient
qrs_complex = get_intervals(q_peaks, 'qrs', *s_peaks)
mech_sys = get_mech_systole(qt_interval, heart_cycle, "women")

interval_df = pd.DataFrame({"QT_Interval": qt_interval,
                            "Mechanical systole": mech_sys,
                            "PQ_Interval": pq_interval,
                            "QRS_Complex": qrs_complex})
