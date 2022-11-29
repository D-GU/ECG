import matplotlib.pyplot as plt

from functions import *
from processes import *
from raw_data import get_raw_data

# Get data
data = get_raw_data("train.npy")

# Init hyperparameters
sampling_rate = 100  # Sampling rate


def get_amplitude(_signal, _time_coordinates: np.array):
    return np.array([_signal[i] for i in _time_coordinates])


def visualize_peaks(_signal, *args):
    _names = ["R Peaks", "Q Peaks", "S Peaks", "T Peaks", "P Peaks"]

    # Set resolution of the plots
    plt.rcParams['figure.dpi'] = 300

    # Quantity of graphs
    _graphs_quan = len(args)

    # How many rows on subplots
    _x = _graphs_quan // 2

    # How many columns of subplots
    _y = _graphs_quan - _x

    # Init the sheet and plots
    fig, ax = plt.subplots(_x, _y)

    # Distance between plots
    fig.tight_layout(pad=1.70)

    # Get amplitudes of peaks
    _amp = get_amplitude(_signal, args[0])

    # Counter of args (Needed for appropriate names and peaks conformity)
    counter = -1

    for x in range(_x):
        for y in range(_y):

            # If x and y == 0 then the plot is just signal
            if 0 == x == y:
                ax[x, y].set_title("ECG Signal")
                ax[x, y].plot(_signal, color="red")
                continue

            counter += 1
            _amp = get_amplitude(_signal, args[counter])

            # Put peaks amplitudes on the signal
            ax[x, y].plot(_signal, color="red")
            ax[x, y].plot(args[counter], _amp, "yo")

            # Put peak values on the "dots"
            for amplitude in range(len(_amp)):
                ax[x, y].text(
                    args[counter][amplitude],
                    _amp[amplitude],
                    s=str(f"{_amp[amplitude]: .3f}"),
                    fontsize=4,
                    horizontalalignment='center',
                    verticalalignment='center'
                )

            # Put the title on the subplot
            ax[x, y].set_title(f"{_names[counter]}", fontdict={"size": 10})

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

    visualize_peaks(
        _cleaned_signal,
        _r_peaks,
        _q_peaks,
        _s_peaks,
        _t_peaks,
        _p_peaks,
    )


get_parameters(data[0][:, 5], 100)
