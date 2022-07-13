import numpy as np
import matplotlib.pyplot as plt

from neurokit2 import ecg_process, ecg_peaks, ecg_delineate, ecg_rate, signal_period
from pandas import DataFrame, Series


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
    _ecg_data, _ = ecg_process(_ecg_signal,
                               sampling_rate=100)

    # Get cleaned signal from the data frame, so we can find peaks
    _ecg_clean_signal = np.array(_ecg_data["ECG_Clean"])

    # Get peaks from the cleaned signal
    _instant_peaks, _r_peaks = ecg_peaks(_ecg_clean_signal,
                                         sampling_rate=100)

    # Getting the rate based on the signal peaks
    _rate = ecg_rate(_r_peaks,
                     sampling_rate=100,
                     desired_length=len(_ecg_clean_signal))

    _signals = DataFrame({"ECG_Raw": _ecg_signal,
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
    _signals, _waves_peak = ecg_delineate(
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
    Percentage change between cur and prev elements

    parameters:
        peaks: an array of peaks

    return:
        array: array of pct changes
    """
    return Series(peaks).pct_change()


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
        [interval / (_k_const[_gen] * np.sqrt(_heart_cycle)) for interval in _qt]
    )
