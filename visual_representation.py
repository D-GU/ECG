import matplotlib.pyplot as plt

from matplotlib.lines import Line2D
from functions import *
from raw_data import get_raw_data


class Visualizer:
    def __init__(self, signal, sampling_rate, seconds, recording_speed):
        self.signal = signal

        self.sampling_rate = sampling_rate
        self.recording_speed = recording_speed
        self.seconds = seconds

        self.grid_major_bound = self.sampling_rate * self.seconds
        self.grid_minor_bound = self.sampling_rate * self.recording_speed
        self.step_minor = (self.grid_minor_bound / self.recording_speed) / self.recording_speed

        self.clean_signal = self.get_peaks()[0]
        self.peaks = self.get_peaks()[1]
        self.amplitudes = self.get_amplitudes()
        self.intervals = self.get_intervals()

        # Name of each peak to plot
        self.peaks_names = np.array(["R Peaks", "Q Peaks", "S Peaks", "T Peaks", "P Peaks"])

        # Name of each interval(segment) to plot
        self.intervals_names = np.array([
            "Зубец P",
            "Интервал PR",
            "Сегмент PQ",
            "Комплекс QRS",
            "Сегмент ST",
            "Зубец T"
        ])

        # Set intervals show parameters
        self.intervals_show_params = {
            0: (np.max(self.amplitudes[4])) + 0.05,
            1: (0 - np.max(self.amplitudes[4])) + 0.20,
            2: (0 - np.max(self.amplitudes[4])) + 0.17,
            3: (-0.03 + np.min(self.amplitudes[2])),
            4: (-0.03 + np.min(self.amplitudes[2])),
            5: (-0.03 + np.min(self.amplitudes[2]))
        }

        # Set a color to each peak to plot
        self.colors = ["r", "y", "m", "g", "b"]

        # Init canvas and plot
        self.fig, self.ax = plt.subplots(1, 1)

        # Init figure manager
        self.fig_manager = plt.get_current_fig_manager()

        # Set full_screen_toggle to show image in full screen
        # self.fig_manager.full_screen_toggle()

        # Subplots adjustment
        plt.subplots_adjust(
            left=0.002, bottom=0.298, right=1, top=0.693, wspace=0.2, hspace=0.2
        )

        # Plot the signal
        self.ax.plot(self.clean_signal, color="0.350", linewidth=1.25)

        # Turn on minor-ticks to draw small grid
        plt.minorticks_on()

        # Init grid parameters
        self.major_ticks = np.arange(0, self.grid_major_bound, self.sampling_rate)
        self.minor_ticks = np.arange(0, self.grid_minor_bound, self.step_minor)

        # Set major grid show parameters
        self.ax.set_xticks(self.major_ticks)

        # Set minor grid show parameters
        self.ax.set_xticks(self.minor_ticks, minor=True)

        # Make the major grid
        self.ax.grid(which='major', linestyle='-', color='red', linewidth=0.8)

        # Make the minor grid
        self.ax.grid(which='minor', linestyle=':', color='black', linewidth=0.3)

    def get_peaks(self):
        """A method fo get peaks"""

        # preprocessed data and R Peaks
        _preprocessed, info = preprocess(self.signal, self.sampling_rate)

        _cleaned_signal = _preprocessed["ECG_Clean"]
        _r_peaks = info["ECG_R_Peaks"]

        all_peaks = [_r_peaks]

        # Get all peaks
        _, _peaks = get_qst_peaks(_cleaned_signal, _r_peaks, self.sampling_rate)

        # Put each peak in to an array
        all_peaks.append(_peaks["ECG_Q_Peaks"])
        all_peaks.append(_peaks["ECG_S_Peaks"])
        all_peaks.append(_peaks["ECG_T_Peaks"])
        all_peaks.append(_peaks["ECG_P_Peaks"])

        return _cleaned_signal, np.array(all_peaks), _peaks

    def get_amplitudes(self):
        """ A method fo get the amplitudes of all peaks """

        _amplitudes = []

        for peak in self.peaks:
            _amplitudes.append(get_amplitude(self.clean_signal, peak))

        return np.array(_amplitudes)

    def get_intervals(self):
        """A method to get the intervals to plot"""

        _all_peaks = self.get_peaks()[2]
        _durations, _boundaries = get_durations(self.signal, _all_peaks, self.peaks[0])

        # Assign each segment to their own kind
        _r_bound = _boundaries["R_Peaks"]
        _q_bound = _boundaries["Q_Peaks"]
        _s_bound = _boundaries["S_Peaks"]
        _t_bound = _boundaries["T_Peaks"]
        _p_bound = _boundaries["P_Peaks"]

        # Init the intervals, segments and complexes
        _pq_segment = np.array([(start[1], end[0]) for start, end in zip(_p_bound, _r_bound)])
        _pr_interval = np.array([(start[0], end[0]) for start, end in zip(_p_bound, _r_bound)])
        _qrs_complex = np.array([(start[0], end[1]) for start, end in zip(_r_bound, _s_bound)])
        _st_segment = np.array([(start[1], end[0]) for start, end in zip(_s_bound, _t_bound)])

        # Collect intervals in array
        _intervals = np.array(
            [_p_bound,
             _pr_interval,
             _pq_segment,
             _qrs_complex,
             _st_segment,
             _t_bound]
        )

        return _intervals

    def peaks_data_visualizer(self):
        for counter, (peaks, amps) in enumerate(zip(self.peaks, self.amplitudes)):
            self.ax.scatter(peaks, amps, facecolor=self.colors[counter])
            # self.ax.plot(peaks, amps, self.colors[counter])

            # Put peak values in the markers
            for idx, amplitude in enumerate(amps):
                # Apply bias to a peak to make it look readable
                bias = 0.03 * (amplitude / np.abs(amplitude))

                self.ax.text(
                    peaks[idx],
                    amplitude + bias,
                    s=str(f"{amps[idx]: .3f}"),
                    fontsize=8.5,
                    horizontalalignment="center",
                    verticalalignment="center"
                )

        # Init the legend of the plot

        _legend = [
            Line2D([], [], marker="o", color="r", label="R_Peaks", markersize=4),
            Line2D([], [], marker="o", color="y", label="Q_Peaks", markersize=4),
            Line2D([], [], marker="o", color="m", label="S_Peaks", markersize=4),
            Line2D([], [], marker="o", color="g", label="T_Peaks", markersize=4),
            Line2D([], [], marker="o", color="b", label="P_Peaks", markersize=4),
            Line2D([], [], marker="", color="black", label=f"{self.sampling_rate}kHZ", markersize=4)
        ]

        self.ax.legend(handles=_legend, loc="upper left", fontsize="x-small")

    def intervals_data_visualizer(self):
        for idx, intervals in enumerate(self.intervals):
            for sub_interval in range(len(intervals)):
                _start, _end = intervals[sub_interval]
                _mid = (_end + _start) * 0.5

                _interval_len = (_end - _start) - 1

                # Plot vertical lines representing the boundaries of intervals
                self.ax.vlines(
                    x=intervals,
                    colors="k",
                    ymin=self.intervals_show_params[idx],
                    ymax=0.15,
                    lw=0.60
                )

                self.ax.arrow(
                    x=_start + 0.3,
                    y=self.intervals_show_params[idx],
                    dx=_interval_len,
                    dy=0,
                    width=0.0002,
                    head_width=0.005,
                    color="black",
                    length_includes_head=True,
                    rasterized=True
                )

                # ax.annotate(
                #     f"{_names[idx]}",
                #     xy=(_start, _intervals_show_params[idx]),
                #     xytext=(_mid, _intervals_show_params[idx]),
                #     ha="center",
                #     va="center",
                #     arrowprops=
                #     ]dict(arrowstyle="->", connectionstyle="arc3,rad=0")
                # )

                self.ax.text(
                    x=_mid,
                    y=self.intervals_show_params[idx] + 0.015,
                    s=self.intervals_names[idx],
                    fontsize=7,
                    horizontalalignment="center",
                    verticalalignment="center"
                )

    def onclick(self, event):
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.button, event.x, event.y, event.xdata, event.ydata))

        self.ax.scatter(event.xdata, event.ydata, facecolor='green')
        self.ax.plot(event.xdata, event.ydata, ',')
        self.fig.canvas.draw()

    def visualizer(self):
        self.peaks_data_visualizer()
        self.intervals_data_visualizer()
        # cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)

        plt.show()


def main():
    data = get_raw_data("ecg_ptbxl.npy")
    signal = data[0][:, 4]
    sampling_rate = 100
    seconds = 10
    recording_speed = 25

    x = Visualizer(signal, sampling_rate, seconds, recording_speed)
    x.visualizer()


if __name__ == "__main__":
    main()
