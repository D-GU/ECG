import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import CheckButtons

file = np.load("ecg_ptbxl.npy", allow_pickle=True)
sample = file[0][:, 0]

fig, ax = plt.subplots()

fig_manager = plt.get_current_fig_manager()

fig_manager.full_screen_toggle()
plt.subplots_adjust(
    left=0.002, bottom=0.298, right=1, top=0.693, wspace=0.2, hspace=0.2
)

ax.set_xlabel("0 / 21429\n0 / 12")
ax.plot(sample)


class Index:
    def __init__(self, data, quantity_samples, sample_id, lead_id):
        self.data = data
        self.quantity_samples = quantity_samples
        self.lead_ind = lead_id
        self.sample_ind = sample_id
        self.to_plot = data[sample_id][:, lead_id]

        self.p_peaks = []
        self.q_peaks = []
        self.r_peaks = []
        self.s_peaks = []
        self.t_peaks = []

        self.p_ons = []
        self.p_offs = []

        self.q_ons = []
        self.q_offs = []

        self.r_ons = []
        self.r_offs = []

        self.s_ons = []
        self.s_offs = []

        self.t_ons = []
        self.t_offs = []

    def lead_next(self, event):
        self.lead_ind += 1
        i = self.lead_ind % 12
        self.to_plot = self.data[self.sample_ind][:, i]

        ax.clear()
        ax.set_xlabel(f"{self.sample_ind % self.quantity_samples} / 21429\n{i % 12} / 11")
        ax.plot(self.to_plot)

        # l.set_ydata(self.to_plot)
        plt.draw()

    def lead_prev(self, event):
        self.lead_ind -= 1
        i = self.lead_ind % 12
        self.to_plot = self.data[self.sample_ind][:, i]

        ax.clear()
        ax.set_xlabel(f"{self.sample_ind % self.quantity_samples} / 21429\n{i % 12} / 11")
        ax.plot(self.to_plot)

        # l.set_ydata(self.to_plot)
        plt.draw()

    def sample_next(self, event):
        self.sample_ind += 1
        i = self.sample_ind % self.quantity_samples
        self.to_plot = self.data[i][:, 0]

        ax.clear()
        ax.set_xlabel(f"{self.sample_ind % self.quantity_samples} / 21429\n{0} / 11")
        ax.plot(self.to_plot)

        # l.set_ydata(self.to_plot)
        plt.draw()

    def sample_prev(self, event):
        self.sample_ind -= 1
        i = self.sample_ind % self.quantity_samples
        self.to_plot = self.data[i][:, 0]

        ax.clear()
        ax.set_xlabel(f"{self.sample_ind % self.quantity_samples} / 21429\n{0} / 11")
        ax.plot(self.to_plot)

        # l.set_ydata(self.to_plot)
        plt.draw()

    def peak_markup(self, event):
        ...


callback = Index(file, 21430, 0, 0)

ax_lead_prev = fig.add_axes([0.1, 0.05, 0.1, 0.075])
ax_lead_next = fig.add_axes([0.2, 0.05, 0.1, 0.075])
ax_sample_prev = fig.add_axes([0.3, 0.05, 0.1, 0.075])
ax_sample_next = fig.add_axes([0.4, 0.05, 0.1, 0.075])

bln = Button(ax_lead_next, "lead >>")
blp = Button(ax_lead_prev, "lead <<")
sn = Button(ax_sample_next, "sample >>")
sp = Button(ax_sample_prev, "sample <<")

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
