import matplotlib.pyplot as plt

from matplotlib.lines import Line2D
from functions import *
from processes import *
from raw_data import get_raw_data

# Get data
data = get_raw_data("ecg_ptbxl.npy")

# Init hyperparameters
sampling_rate = 100  # Sampling rate

fig, ax = plt.subplots(1, 1)

plt.rcParams["figure.dpi"] = 100
plt.subplots_adjust(
    left=0.002, bottom=0.298, right=1, top=0.693, wspace=0.2, hspace=0.2
)

plt.minorticks_on()

# Make the major grid
ax.grid(which='major', linestyle='-', color='red', linewidth=0.8)
# Make the minor grid
ax.grid(which='minor', linestyle=':', color='black', linewidth=0.3)


def visualize_peaks(_signal, _names, _amplitudes, *args):
    _color = ["ro", "yo", "mo", "go", "bo"]

    # Counter of args (Needed for appropriate names and peaks conformity)
    ax.plot(_signal, color="0.5", linewidth=1.25)

    for counter, (args, amps) in enumerate(zip(args, _amplitudes)):
        ax.plot(args, amps, _color[counter])

        # Put peak values in the markers
        for idx, amplitude in enumerate(amps):
            ax.text(
                args[idx],
                amplitude,
                s=str(f"{amps[idx]: .3f}"),
                fontsize=2.5,
                horizontalalignment="center",
                verticalalignment="center"
            )

    # Init the legend of the plot
    _legend = [
        Line2D([], [], marker="o", color="r", label="R_Peaks", markersize=4),
        Line2D([], [], marker="o", color="y", label="Q_Peaks", markersize=4),
        Line2D([], [], marker="o", color="m", label="S_Peaks", markersize=4),
        Line2D([], [], marker="o", color="g", label="T_Peaks", markersize=4),
        Line2D([], [], marker="o", color="b", label="P_Peaks", markersize=4)
    ]

    ax.legend(handles=_legend, loc="upper left", fontsize="x-small")

    return 0


def visualize_segments(_signal, _boundaries, _amplitudes):
    # Highest and lowest points of interval boundaries
    _highest_point = 0.02
    _lowest_point = -0.080

    # define colors
    _color = ["c", "y", "m", "g", "b"]

    # Assign each segment to their own kind
    _r_bound = _boundaries["R_Peaks"]
    _q_bound = _boundaries["Q_Peaks"]
    _s_bound = _boundaries["S_Peaks"]
    _t_bound = _boundaries["T_Peaks"]
    _p_bound = _boundaries["P_Peaks"]

    # Init the intervals, segments and complexes
    _pq_segment = np.array([(start[1], end[0]) for start, end in zip(_p_bound, _q_bound)])
    _pr_interval = np.array([(start[0], end[0]) for start, end in zip(_p_bound, _r_bound)])
    _qrs_complex = np.array([(start[0], end[1]) for start, end in zip(_q_bound, _s_bound)])
    _st_segment = np.array([(start[1], end[0]) for start, end in zip(_s_bound, _t_bound)])

    _names = [
        "Зубец P",
        "Интервал PR",
        "Сегмент PQ",
        "Комплекс QRS",
        "Сегмент ST",
        "Зубец T"
    ]

    np.set_printoptions(precision=3)

    _intervals_show_params = {
        0: (0 - np.max(_amplitudes[4])),
        1: (-0.2 + np.max(_amplitudes[4])),
        2: (np.max(_amplitudes[4])),
        3: (-0.03 + np.min(_amplitudes[2])),
        4: (-0.32 + np.max(_amplitudes[3])),
        5: (-0.2 + np.max(_amplitudes[3]))
    }

    # Collect intervals in array
    _intervals = np.array(
        [_p_bound,
         _pr_interval,
         _pq_segment,
         _qrs_complex,
         _st_segment,
         _t_bound]
    )

    for idx, intervals in enumerate(_intervals):
        for sub_interval in range(len(intervals)):
            _start, _end = intervals[sub_interval]
            _mid = (_end + _start) * 0.5

            _interval_len = (_end - _start) - 0.03

            # Plot vertical lines representing the boundaries of intervals
            ax.vlines(x=intervals, colors="k", ymin=-0.15, ymax=0.25, lw=0.60)

            # Plot arrows representing each individual interval

            # ax.annotate(
            #     f"{_names[idx]}",
            #     xy=(_start, _intervals_show_params[idx]),
            #     xytext=(_mid, _intervals_show_params[idx]),
            #     ha="center",
            #     va="center",
            #     arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0")
            # )

            ax.arrow(
                x=_start + 0.05,
                y=_intervals_show_params[idx],
                dx=np.abs(_interval_len) - 0.05,
                dy=0,
                width=0.0002,
                head_width=0.005,
                color="black",
                length_includes_head=True
            )

            ax.text(
                x=_mid,
                y=_intervals_show_params[idx],
                s=_names[idx],
                fontsize=6,
                horizontalalignment="center",
                verticalalignment="center"
            )

    return 0


def plots_parameters(_signal: np.array, _sampling_rate: int):
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


plots_parameters(data[0][:, 1], 100)
plt.show()
