import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import CheckButtons

file = np.load("ecg_ptbxl.npy", allow_pickle=True)
sample = file[0][:, 0]

fig, ax = plt.subplots()
l, = ax.plot(file[0][:, 0])

ax.text(x=3,
        y=3,
        s="RRRRR",
        fontsize=7,
        horizontalalignment="center",
        verticalalignment="center"
        )

print(f"0 / 21430\n 0 / 12")


class Index:
    def __init__(self, data, quantity_samples, sample_id, lead_id):
        self.data = data
        self.quantity_samples = quantity_samples
        self.lead_ind = lead_id
        self.sample_ind = sample_id
        self.to_plot = data[sample_id][:, lead_id]

    def lead_next(self, event):
        self.lead_ind += 1
        i = self.lead_ind % 12
        self.to_plot = self.data[self.sample_ind][:, i]
        l.set_ydata(self.to_plot)
        print(f"{self.sample_ind % self.quantity_samples} / 21430\n {self.lead_ind % 12} / 12")

        plt.draw()

    def lead_prev(self, event):
        self.lead_ind -= 1
        i = self.lead_ind % 12
        self.to_plot = self.data[self.sample_ind][:, i]
        l.set_ydata(self.to_plot)
        print(f"{self.sample_ind % self.quantity_samples} / 21430\n {self.lead_ind % 12} / 12")

        plt.draw()

    def sample_next(self, event):
        self.sample_ind += 1
        i = self.sample_ind % self.quantity_samples
        self.to_plot = self.data[i][:, 0]
        l.set_ydata(self.to_plot)
        print(f"{self.sample_ind % self.quantity_samples} / 21430\n {self.lead_ind % 12} / 12")

        plt.draw()

    def sample_prev(self, event):
        self.sample_ind -= 1
        i = self.sample_ind % self.quantity_samples
        self.to_plot = self.data[i][:, 0]
        l.set_ydata(self.to_plot)
        print(f"{self.sample_ind % self.quantity_samples} / 21430\n {self.lead_ind % 12} / 12")

        plt.draw()


callback = Index(file, 21430, 0, 0)

ax_lead_prev = fig.add_axes([0.1, 0.05, 0.1, 0.075])
ax_lead_next = fig.add_axes([0.4, 0.05, 0.1, 0.075])
ax_sample_prev = fig.add_axes([0.7, 0.05, 0.1, 0.075])
ax_sample_next = fig.add_axes([0.9, 0.05, 0.1, 0.075])

bln = Button(ax_lead_next, "LN")
blp = Button(ax_lead_prev, "LP")
sn = Button(ax_sample_next, "SN")
sp = Button(ax_sample_prev, "SP")

bln.on_clicked(callback.lead_next)
blp.on_clicked(callback.lead_prev)
sp.on_clicked(callback.sample_prev)
sn.on_clicked(callback.sample_next)

plt.show()


class Marker:
    def __init__(self, data_folder, sampling_rate):
        self.sample_box = np.load(data_folder, allow_pickle=True)
        self.sample_quan = self.sample_box.shape[0]
        self.sampling_rate = sampling_rate

        self.p_peaks = ...
        self.p_ons = ...
        self.p_offs = ...

        self.r_peaks = ...
        self.r_ons = ...
        self.r_offs = ...

        self.q_peaks = ...
        self.q_ons = ...
        self.q_offs = ...

        self.s_peaks = ...
        self.s_ons = ...
        self.s_offs = ...

        self.t_peaks = ...
        self.t_ons = ...
        self.t_offs = ...
