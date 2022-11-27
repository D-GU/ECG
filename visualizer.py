import matplotlib.pyplot as plt

from neurokit2 import ecg_plot
from functions import *
from processes import *
from raw_data import get_raw_data

# Get data
data = get_raw_data("train.npy")

# Init hyperparameters
sampling_rate = 100  # Sampling rate


def get_plots():
    return 0


def get_parameters(_signal: np.array, _leads: int, _sampling_rate: int):
    _preprocessed, info = preprocess(_signal, _sampling_rate)
    plt.plot(_preprocessed["ECG_Raw"])
    plt.show()


get_parameters(data[0][:, 0], 1, 100)
