import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import CheckButtons

class Index:
    def __init__(self, data, quantity_samples):
        self.data = data
        self.quantity_samples = quantity_samples

    lead_ind = 0
    sample_ind = 0

    def lead_next(self, event):
        self.lead_ind += 1
        i = self.lead_ind % 12
        plt.show(data[])

    def lead_prev(self, event):
        self.lead_ind -= 1
        i = self.lead_ind % 12
        self.data = self.data[::][:, i]
        plt.plot(self.data)

    def sample_next(self, event):
        self.sample_ind += 1
        i = self.sample_ind % self.quantity_samples
        self.data = self.data[i][:, 0]
        plt.plot(self.data)

    def sample_prev(self, event):
        self.sample_ind -= 1
        i = self.sample_ind % self.quantity_samples
        self.data = self.data[i][:, 0]
        plt.plot(self.data)


file = np.load("ecg_ptbxl.npy", allow_pickle=True)
sample = file[0][:, 0]
callback = Index(sample, 21430)

fig, ax = plt.subplots()
ax.plot(sample)
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

