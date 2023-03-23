import os

import functions
import matplotlib.markers
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from matplotlib.widgets import RadioButtons
from matplotlib.backend_bases import MouseButton


class ECGCleaner:
    def __init__(self, full_ecg, sampling_rate):
        self.full_ecg = full_ecg
        self.sampling_rate = sampling_rate

    def get_clean_signal(self, lc=0.5, hc=10):
        u, s, v = np.linalg.svd(self.full_ecg, full_matrices=False)


class BaseStructure:
    def __init__(self, database, sampling_rate, recording_speed, recording_time):
        self.sample_number = 0
        self.data = database
        self.quantity_samples = database.shape[0]
        self.leads_quantity = 12
        self.sampling_rate = sampling_rate
        self.recording_speed = recording_speed
        self.time_of_record = recording_time
        self.view_condition = 0

        self.view = {
            0: (6, 2),
            1: (12, 1)
        }

        # Set ecg channels as a matrix
        self.ecg_matrix = np.array([database[self.sample_number][:, i] for i in range(12)])

        self.x_limit = [150, (self.time_of_record * self.sampling_rate) - 300]

        self.lead_names = [
            "i", "ii", "iii", "aVF", "aVR", "aVL", "V1", "V2", "V3", "V4", "V5", "V6"
        ]

        self.fig, self.ax = plt.subplots(*self.view[self.view_condition])
        self.set_limits()

        plt.show()

    def set_limits(self):
        for ax in self.ax.ravel():
            ax.set_xlim(self.x_limit)


if __name__ == "__main__":
    ecg_file = np.load("ecg_ptbxl.npy", allow_pickle=True)

    x = BaseStructure(
        database=ecg_file, sampling_rate=100, recording_speed=25, recording_time=10
    )