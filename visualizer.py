import matplotlib.pyplot as plt
import ecg_plot
import raw_data

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


def visualize_peaks(_signal, *args):
    _names = ["R Peaks", "Q Peaks", "S Peaks", "T Peaks", "P Peaks"]
    _color = ["ro", "yo", "rd", "go", "bo"]

    # Set resolution of the plots
    plt.rcParams["figure.dpi"] = 250

    plt.minorticks_on()

    # Make the major grid
    plt.grid(which='major', linestyle='-', color='red', linewidth='0.5')
    # Make the minor grid
    plt.grid(which='minor', linestyle=':', color='black', linewidth='0.25')

    # Counter of args (Needed for appropriate names and peaks conformity)
    plt.plot(_signal, color="black", linewidth=1.25)

    for counter, args in enumerate(args):
        _amp = get_amplitude(_signal, args)
        plt.plot(args, _amp, _color[counter])

        # Put peak values in the markers
        for idx, amplitude in enumerate(_amp):
            plt.text(
                args[idx],
                amplitude,
                s=str(f"{_amp[idx]: .3f}"),
                fontsize=2,
                horizontalalignment="center",
                verticalalignment="center"
            )

    _legend = [Line2D([], [], marker="o", color="red", label="R_Peaks", markersize=4),
               Line2D([], [], marker="o", color="yellow", label="Q_Peaks", markersize=4),
               Line2D([], [], marker="d", color="red", label="S_Peaks", markersize=4),
               Line2D([], [], marker="o", color="green", label="T_Peaks", markersize=4),
               Line2D([], [], marker="o", color="blue", label="P_Peaks", markersize=4)]

    plt.legend(handles=_legend, loc="upper left", fontsize="x-small")

    plt.show()

    return 0


def get_parameters(_signal: np.array, _sampling_rate: int):
    _preprocessed, info = preprocess(_signal, _sampling_rate)
    _cleaned_signal = _preprocessed["ECG_Clean"]
    _r_peaks = info["ECG_R_Peaks"]

    _, _all_peaks = get_qst_peaks(_cleaned_signal, _r_peaks, _sampling_rate)

    _q_peaks = _all_peaks["ECG_Q_Peaks"]
    _p_peaks = _all_peaks["ECG_P_Peaks"]
    _s_peaks = _all_peaks["ECG_S_Peaks"]
    _t_peaks = _all_peaks["ECG_T_Peaks"]

    _durations, _boundaries = get_durations(_signal, _all_peaks, _r_peaks)

    visualize_peaks(
        _cleaned_signal,
        _r_peaks,
        _q_peaks,
        _s_peaks,
        _t_peaks,
        _p_peaks,
    )


get_parameters(data[0][:, 0], 100)
