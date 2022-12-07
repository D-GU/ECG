import random

import matplotlib.pyplot as plt
import numpy as np

import raw_data

from matplotlib.ticker import AutoMinorLocator
from matplotlib.lines import Line2D
from functions import *
from processes import *
from raw_data import get_raw_data

# Get data
data = get_raw_data("ecg_ptbxl.npy")

# Init hyperparameters
sampling_rate = 100  # Sampling rate


def get_amplitude(_signal, _time_coordinates: np.array):
    return np.array([_signal[i] for i in _time_coordinates])


def visualize_peaks(_signal, _names, _amplitudes, *args):
    _color = ["ro", "yo", "mo", "go", "bo"]

    # Set resolution of the plots
    plt.rcParams["figure.figsize"] = [35, 35]
    plt.rcParams["figure.dpi"] = 300

    plt.minorticks_on()

    # Make the major grid
    # plt.grid(which='major', linestyle='-', color='red', linewidth=0.75)
    # Make the minor grid
    # plt.grid(which='minor', linestyle=':', color='black', linewidth=0.5)

    # Counter of args (Needed for appropriate names and peaks conformity)
    plt.plot(_signal, color="0.5", linewidth=1.25)

    for counter, (args, amps) in enumerate(zip(args, _amplitudes)):
        plt.plot(args, amps, _color[counter])

        # Put peak values in the markers
        for idx, amplitude in enumerate(amps):
            plt.text(
                args[idx],
                amplitude,
                s=str(f"{amps[idx]: .3f}"),
                fontsize=2.5,
                horizontalalignment="center",
                verticalalignment="center"
            )

    _legend = [Line2D([], [], marker="o", color="r", label="R_Peaks", markersize=4),
               Line2D([], [], marker="o", color="y", label="Q_Peaks", markersize=4),
               Line2D([], [], marker="o", color="m", label="S_Peaks", markersize=4),
               Line2D([], [], marker="o", color="g", label="T_Peaks", markersize=4),
               Line2D([], [], marker="o", color="b", label="P_Peaks", markersize=4)]

    plt.legend(handles=_legend, loc="upper left", fontsize="x-small")

    return 0


def visualize_segments(_signal, _boundaries, _amplitudes):
    # Highest and lowest points of interval boundaries
    _highest_point = 0.099
    _lowest_point = _highest_point * -1

    # define colors
    _color = ["c", "y", "m", "g", "b"]

    # Assign each segment to their own kind
    _r_bound = _boundaries["R_Peaks"]
    _q_bound = _boundaries["Q_Peaks"]
    _s_bound = _boundaries["S_Peaks"]
    _t_bound = _boundaries["T_Peaks"]
    _p_bound = _boundaries["P_Peaks"]

    # Make the intervals
    _qt_interval = np.array([(_start[0], _end[1]) for _start, _end in zip(_q_bound, _t_bound)])
    _pq_interval = np.array([(_start[1], _end[0]) for _start, _end in zip(_p_bound, _q_bound)])
    _rr_interval = np.array([(_start[0], _end[1]) for _start, _end in zip(_r_bound, _r_bound)])
    _pr_interval = np.array([(_start[1], _end[0]) for _start, _end in zip(_p_bound, _r_bound)])
    _qrs_interval = np.array([(_start[0], _end[1]) for _start, _end in zip(_q_bound, _s_bound)])

    # Names of the intervals
    _names = ["QT", "PQ", "RR", "PR", "QRS"]

    # Collect intervals in array
    _intervals = np.array([
        _qt_interval,
        _pq_interval,
        _rr_interval,
        _pr_interval,
        _qrs_interval]
    )

    for idx, (amplitudes, intervals) in enumerate(zip(_amplitudes, _intervals)):
        for sub_interval in range(len(intervals)):
            _start, _end = intervals[sub_interval]
            _mid = (_end + _start) / 2

            _interval_len = _end - _start
            _interval_name = _names[idx]

            print(f"start = {_start}, end = {_end}, interval len = {_interval_len}")

            # Plot vertical lines representing the boundaries of intervals
            plt.vlines(x=intervals, colors="k", ymin=-0.15, ymax=0.15, lw=0.52)
            _lowest_point_arrow = random.uniform(-0.090, -0.099)

            # Plot arrows representing each individual interval
            plt.arrow(
                x=_start + 0.3,
                y=_lowest_point_arrow,
                dx=_interval_len - 0.3,
                dy=0,
                width=0.0001,
                head_width=1e-13,
                color="green",
                length_includes_head=True
            )

            plt.text(
                x=_mid,
                y=_lowest_point - 0.001,
                s=_interval_name,
                fontsize=2.5,
                horizontalalignment="center",
                verticalalignment="center"
            )

    return 0


def get_parameters(_signal: np.array, _sampling_rate: int):
    # Names of the peaks to display them on the plot
    _names_peaks = ["R Peaks", "Q Peaks", "S Peaks", "T Peaks", "P Peaks"]

    # Names of the segments to display them on the plot
    _names_segments = ["qt_interval", "pq_interval", "rr_interval", "pr_interval", "QRS_interval"]

    _preprocessed, info = preprocess(_signal, _sampling_rate)  # preprocessed data and R Peaks
    _cleaned_signal = _preprocessed["ECG_Clean"]
    _r_peaks = info["ECG_R_Peaks"]

    _, _all_peaks = get_qst_peaks(_cleaned_signal, _r_peaks, _sampling_rate)

    # Assign each peak to their own kind
    _q_peaks = _all_peaks["ECG_Q_Peaks"]
    _p_peaks = _all_peaks["ECG_P_Peaks"]
    _s_peaks = _all_peaks["ECG_S_Peaks"]
    _t_peaks = _all_peaks["ECG_T_Peaks"]

    # Calculate amplitudes of all peaks
    _q_amplitudes = get_amplitude(_cleaned_signal, _q_peaks)
    _p_amplitudes = get_amplitude(_cleaned_signal, _p_peaks)
    _s_amplitudes = get_amplitude(_cleaned_signal, _s_peaks)
    _t_amplitudes = get_amplitude(_cleaned_signal, _t_peaks)
    _r_amplitudes = get_amplitude(_cleaned_signal, _r_peaks)

    # Collect all peaks amplitudes in array
    _amplitudes = np.array(
        [_r_amplitudes, _q_amplitudes, _s_amplitudes, _t_amplitudes, _p_amplitudes]
    )

    # Get peaks durations and boundaries
    _durations, _boundaries = get_durations(_signal, _all_peaks, _r_peaks)

    # Plot peaks
    visualize_peaks(
        _cleaned_signal,
        _names_peaks,
        _amplitudes,
        *(_r_peaks,
          _q_peaks,
          _s_peaks,
          _t_peaks,
          _p_peaks)
    )

    # Plot segments(intervals)
    visualize_segments(
        _cleaned_signal,
        _boundaries,
        _amplitudes
    )

    plt.show()


get_parameters(data[0][:, 0], 100)
