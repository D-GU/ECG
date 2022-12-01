import numpy as np

from neurokit2 import ecg_peaks, ecg_delineate, ecg_clean
from pandas import DataFrame, Series


def preprocess(_ecg_signal, _sampling_rate):
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

    # Get cleaned signal from the data frame, so we can find peaks

    _ecg_clean_signal = ecg_clean(_ecg_signal, sampling_rate=_sampling_rate)

    # Get peaks from the cleaned signal
    _instant_peaks, _r_peaks = ecg_peaks(_ecg_clean_signal,
                                         sampling_rate=_sampling_rate)

    # Getting the rate based on the signal peaks

    _signals = DataFrame({"ECG_Raw": _ecg_signal,
                          "ECG_Clean": _ecg_clean_signal
                          })

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
        _rr = [np.abs(_x_peaks[i] - _x_peaks[i + 1]) for i in range(len(_x_peaks) - 1)]
        _rr.append(0)
        return np.array(_rr)
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


def get_qst_peaks(_cleaned_signal: np.array, _r_peaks: np.array, _sampling_rate: int):
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
        sampling_rate=_sampling_rate,
        method="dwt",
        show=False,
        show_type="peaks"
    )

    return _signals, _waves_peak


def get_durations(_signal: np.array, _peaks: dict, _r_peaks: np.array):
    """
        Calculates intervals durations

        parameter:
            _signal: ECG signal data
            _all_peaks: All peaks that been found while preprocessing the data
            _r_peaks: R peaks that been found while preprocessing the data

        returns:
            _durations: A dict containing intervals durations
            _boundaries: A dict containing onsets and offsets of certain peaks

    """

    # Fix peaks values if they are not an integer
    _q_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in _peaks["ECG_Q_Peaks"]])
    _s_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in _peaks["ECG_S_Peaks"]])
    _p_peaks = np.array([peak if isinstance(peak, int) else 0 for peak in _peaks["ECG_P_Peaks"]])
    _t_peaks = np.array([peak if isinstance(peak, int) else 0 for peak in _peaks["ECG_T_Peaks"]])

    # Get Onsets and Offsets of certain peaks
    _t_ons = _peaks["ECG_T_Onsets"]
    _t_offs = _peaks["ECG_T_Offsets"]

    _p_ons = _peaks["ECG_P_Onsets"]
    _p_offs = _peaks["ECG_P_Offsets"]

    _r_ons = _peaks["ECG_R_Onsets"]
    _r_offs = _peaks["ECG_R_Offsets"]

    # Calculate Q boundaries
    _r_to_q = np.subtract(_r_peaks, _q_peaks)
    _q_start = np.subtract(_q_peaks, _r_to_q)
    _q_end = np.add(_q_peaks, _r_to_q)

    # Calculate S boundaries
    _r_to_s = np.subtract(_r_offs, _s_peaks)
    _s_start = np.subtract(_s_peaks, _r_to_s)
    _s_end = np.add(_s_peaks, _r_to_s)

    # Calculate peaks durations
    _q_dur = np.subtract(_q_end, _q_start)
    _r_dur = np.subtract(_r_offs, _r_ons)
    _t_dur = np.subtract(_t_offs, _t_ons)
    _p_dur = np.subtract(_p_offs, _p_ons)
    _s_dur = np.subtract(_s_end, _s_start)

    # Assign boundaries to a dictionary
    _boundaries = {
        "Q_Peaks": np.array([(_start, _end) for _start, _end in zip(_q_start, _q_end)]),
        "R_Peaks": np.array([(_start, _end) for _start, _end in zip(_r_ons, _r_offs)]),
        "S_Peaks": np.array([(_start, _end) for _start, _end in zip(_s_start, _s_end)]),
        "T_Peaks": np.array([(_start, _end) for _start, _end in zip(_t_ons, _t_offs)]),
        "P_Peaks": np.array([(_start, _end) for _start, _end in zip(_p_ons, _p_offs)])
    }

    # Assign durations to a dictionary
    _durations = {
        "Q_Durations": _q_dur,
        "R_Durations": _r_dur,
        "T_Durations": _t_dur,
        "P_Durations": _p_dur,
        "S_Durations": _s_dur,
        "Q_Onsets": _q_start,
        "Q_Offsets": _q_end
    }

    return _durations, _boundaries


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
        array: array of Mechanic Systole coefficients
    """

    _k_const = {
        "man": 0.37,
        "men": 0.37,
        "woman": 0.4,
        "women": 0.4
    }

    return np.array(
        [interval / (_k_const[_gen.lower()] * np.sqrt(_heart_cycle)) for interval in _qt]
    )


def get_dispersion(_peaks: np.array):
    _length = np.size(_peaks) - 1
    _std_deviation = 0
    mean = np.mean(_peaks)

    for i in range(_length + 1):
        _std_deviation += np.power(_peaks[i] - mean, 2)

    return _std_deviation / _length


def get_std_deviation(_peaks: np.array):
    dispersion = get_dispersion(_peaks)
    return np.sqrt(dispersion)
