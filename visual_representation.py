import matplotlib.pyplot as plt

from matplotlib.lines import Line2D
from functions import *
from processes import *
from raw_data import get_raw_data

# Subplots adjustment
plt.subplots_adjust(
    left=0.002, bottom=0.298, right=1, top=0.693, wspace=0.2, hspace=0.2
)


class Visualizer:
    def __init__(self, signal, sampling_rate):
        self.signal = signal
        self.sampling_rate = sampling_rate
        self.clean_signal = self.get_peaks()[0]
        self.peaks = self.get_peaks()[1]
        self.amplitudes = self.get_amplitudes()
        self.intervals = self.get_intervals()

        # Name of each peak to plot
        self.peaks_names = np.array({"R Peaks", "Q Peaks", "S Peaks", "T Peaks", "P Peaks"})

        # Name of each interval(segment) to plot
        self.intervals_names = np.array({
            "Зубец P",
            "Интервал PR",
            "Сегмент PQ",
            "Комплекс QRS",
            "Сегмент ST",
            "Зубец T"
        })

        # Set a color to each peak to plot
        self.colors = ["r", "y", "m", "g", "b"]

        self.fig, self.ax = plt.subplots(1, 1)

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
        all_peaks.append(_peaks["ECG_P_Peaks"])
        all_peaks.append(_peaks["ECG_S_Peaks"])
        all_peaks.append(_peaks["ECG_T_Peaks"])

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
        _pq_segment = np.array([(start[1], end[0]) for start, end in zip(_p_bound, _q_bound)])
        _pr_interval = np.array([(start[0], end[0]) for start, end in zip(_p_bound, _r_bound)])
        _qrs_complex = np.array([(start[0], end[1]) for start, end in zip(_q_bound, _s_bound)])
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


def main():
    data = get_raw_data("ecg_ptbxl.npy")
    signal = data[0][:, 1]
    sampling_rate = 100

    x = Visualizer(signal, sampling_rate)
    print(x.intervals)


main()
