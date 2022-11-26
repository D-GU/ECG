import matplotlib.pyplot as plt

from functions import *
from processes import *
from raw_data import get_raw_data

# Get data
data = get_raw_data("train.npy")

# Init hyperparameters
sampling_rate = 100  # Sampling rate


def get_parameters(_signal: np.array, num_sample: int, _lead: int, _sampling_rate: int):
    _preprocessed, info = preprocess(_signal[num_sample][_lead], _sampling_rate)

