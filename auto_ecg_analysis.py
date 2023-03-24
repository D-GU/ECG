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

        self.view_settings = {
            0: ((0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)),
            1: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        }

        # Set ecg channels as a matrix
        self.ecg_matrix = np.array([self.data[self.sample_number][:, i] for i in range(12)])

        self.x_limit = [400, (self.time_of_record * self.sampling_rate) - 200]

        self.lead_names = [
            "i", "ii", "iii", "aVF", "aVR", "aVL", "V1", "V2", "V3", "V4", "V5", "V6"
        ]

        self.fig, self.ax = plt.subplots(*self.view[self.view_condition])
        self.set_limits()
        self.set_ecg()

        ax_sample_prev = self.fig.add_axes([0.3, 0.05, 0.1, 0.075])
        ax_sample_next = self.fig.add_axes([0.4, 0.05, 0.1, 0.075])

        button_sample_next = Button(ax_sample_next, "sample >>")
        button_sample_prev = Button(ax_sample_prev, "sample <<")

        # Connect prev and next buttons to callback function
        button_sample_next.on_clicked(self.change_sample_next)
        button_sample_prev.on_clicked(self.change_sample_prev)

        plt.show()

    def set_limits(self):
        for ax in self.ax.ravel():
            ax.set_xlim(self.x_limit)

    def set_ecg(self):
        # _, _, V = np.linalg.svd(self.ecg_matrix, full_matrices=False)
        self.ecg_matrix = functions.get_clean_matrix(self.ecg_matrix, self.sampling_rate)

        # for x in range(6):
        #     self.ax[x][0].plot(functions.get_clean_signal(self.ecg_matrix[x % 12], _sampling_rate=self.sampling_rate))
        #     self.ax[x][1].plot(functions.get_clean_signal(self.ecg_matrix[x], _sampling_rate=self.sampling_rate))

        if not self.view_condition:
            for x in range(self.view[self.view_condition][0]):
                for y in range(self.view[self.view_condition][1]):
                    self.ax[x][y].plot(self.ecg_matrix[self.view_settings[self.view_condition][x][y]])
                    self.ax[x][y].axhline(
                        y=self.ecg_matrix[self.view_settings[self.view_condition][x][y]][0], color='g', linestyle="-"
                    )
        else:
            for lead, ax in enumerate(self.ax.ravel()):
                ax.plot(self.ecg_matrix[lead])
                ax.axhline(y=self.ecg_matrix[lead][0], color="g", linestyle="-")

    def set_clean(self):
        for ax in self.ax.ravel():
            ax.cla()
            self.set_limits()

    def change_sample_next(self, event):
        self.sample_number += 1
        i = self.sample_number % self.quantity_samples
        self.ecg_matrix = np.array([self.data[self.sample_number][:, i] for i in range(12)])

        self.set_clean()
        self.set_ecg()

        plt.draw()

    def change_sample_prev(self, event):
        self.sample_number -= 1
        i = self.sample_number % self.quantity_samples
        self.ecg_matrix = np.array([self.data[self.sample_number][:, i] for i in range(12)])

        self.set_clean()
        self.set_ecg()

        plt.draw()


if __name__ == "__main__":
    ecg_file = np.load("ecg_ptbxl.npy", allow_pickle=True)

    x = BaseStructure(
        database=ecg_file, sampling_rate=100, recording_speed=25, recording_time=10
    )
