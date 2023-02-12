import os

import matplotlib.markers
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from matplotlib.widgets import Cursor
from matplotlib.widgets import CheckButtons

# If session file is already exists then
# read the data from it and continue markup it
# if not os.path.isfile("user_session.dat"):
#     with open("user_session.dat", "wb") as session_file:
#         session_file.write(bytearray([0, 0]))

file = np.load("ecg_ptbxl.npy", allow_pickle=True)
sample = file[0][:, 0]


# fig, ax = plt.subplots()

# Get figure manager
# fig_manager = plt.get_current_fig_manager()

# Put the figure on full screen mode
# fig_manager.full_screen_toggle()

# Adjust the subplots to make it wider
# plt.subplots_adjust(
#     left=0.002, bottom=0.298, right=1, top=0.693, wspace=0.2, hspace=0.2
# )

# ax.set_xlabel("0 / 21429\n0 / 11")
# ax.plot(sample)


class Callback:
    def __init__(self, data, quantity_samples, sample_id, lead_id, plot):
        self.ax = plot
        self.data = data
        self.quantity_samples = quantity_samples
        self.lead_id = lead_id
        self.sample_id = sample_id
        self.parameter_id = "P"
        self.to_plot = data[sample_id][:, lead_id]

        self.slider_sample_values = np.array([_ for _ in range(self.quantity_samples)])
        self.slider_lead_values = np.array([_ for _ in range(12)])

        self.parameters = {
            "P": [[[] for _ in range(12)] for _ in range(self.quantity_samples)]
        }

        # self.scatter = self.ax.scatter(
        #     x=0,
        #     y=0,
        #     marker=matplotlib.markers.CARETDOWNBASE
        # )
        #
        # self.annotation = self.ax.annotate(
        #     text='',
        #     xy=(0, 0),
        #     xytext=(1, 1)
        # )
        # self.annotation.set_visible(False)

    def lead_next(self, event):
        self.lead_id += 1
        i = self.lead_id % 12
        self.to_plot = self.data[self.sample_id][:, i]

        self.ax.clear()
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{i % 12} / 11")
        self.ax.plot(self.to_plot)

        plt.draw()

    def lead_prev(self, event):
        df = pd.DataFrame(self.parameters["P"])
        print(self.parameters["P"][self.quantity_samples - 1])
        self.lead_id -= 1
        i = self.lead_id % 12
        self.to_plot = self.data[self.sample_id][:, i]

        self.ax.clear()
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{i % 12} / 11")
        self.ax.plot(self.to_plot)

        plt.draw()

    def sample_next(self, event):
        self.sample_id += 1
        i = self.sample_id % self.quantity_samples
        self.to_plot = self.data[i][:, 0]

        self.ax.clear()
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
        self.ax.plot(self.to_plot)

        plt.draw()

    def sample_prev(self, event):
        self.sample_id -= 1
        i = self.sample_id % self.quantity_samples
        self.to_plot = self.data[i][:, 0]

        self.ax.clear()
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
        self.ax.plot(self.to_plot)

        plt.draw()

    def submit_sample_data(self, text):
        if not text.isnumeric():
            self.sample_id = self.sample_id
            self.to_plot = self.data[self.sample_id][:, 0]

            self.ax.clear()
            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.ax.plot(self.to_plot)

            plt.draw()

        if int(text) < 0 or int(text) > self.quantity_samples - 1:
            self.sample_id = self.sample_id
            self.to_plot = self.data[self.sample_id][:, 0]

            self.ax.clear()
            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.ax.plot(self.to_plot)

            plt.draw()

        else:
            self.sample_id = int(text)
            self.to_plot = self.data[self.sample_id][:, 0]

            self.ax.clear()
            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.ax.plot(self.to_plot)

            plt.draw()

    def submit_lead_data(self, text):
        if not text.isnumeric():
            self.lead_id = self.lead_id
            self.to_plot = self.data[self.sample_id][:, self.lead_id]

            self.ax.clear()
            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.ax.plot(self.to_plot)

            plt.draw()

        if int(text) < 0 or int(text) > self.quantity_samples - 1:
            self.lead_id = self.lead_id
            self.to_plot = self.data[self.sample_id][:, self.lead_id]

            self.ax.clear()
            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.ax.plot(self.to_plot)

            plt.draw()

        else:
            self.lead_id = int(text)
            self.to_plot = self.data[self.sample_id][:, self.lead_id]

            self.ax.clear()
            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.ax.plot(self.to_plot)

            plt.draw()

    def p_peak_markup(self, event):
        self.parameter_id = "P"

    def show_markup(self, event):
        ...

    def onclick(self, event):
        self.parameters[self.parameter_id][self.sample_id][self.lead_id].append(event.xdata)
        self.ax.scatter(x=event.xdata, y=event.ydata, marker=matplotlib.markers.CARETDOWNBASE)


class MarkUpper:
    def __init__(self, data_path, session_file_path):
        self.session_file_path = session_file_path
        self.data = data_path

        self.sample_id = ...  # Should be reading it from the session file
        self.lead_id = ...  # Should be reading it from the session file

        # Init plot and figure
        self.fig, self.ax = plt.subplots()

        # Get figure manager
        self.fig_manager = plt.get_current_fig_manager()

        # Put the figure on full screen mode
        self.fig_manager.full_screen_toggle()

        # Adjust the subplots to make it wider
        plt.subplots_adjust(
            left=0.002, bottom=0.298, right=1, top=0.693, wspace=0.2, hspace=0.2
        )

        self.ax.set_xlabel("0 / 21429\n0 / 11")
        self.ax.plot(sample)

    def run_markup(self):
        # Call callback function class
        callback = Callback(self.data, 21430, 0, 0, self.ax)

        # Init cursor
        cursor = Cursor(self.ax, horizOn=False, vertOn=False)

        # Connect cursor to specific event
        cursor.connect_event("button_press_event", callback.onclick)

        # Init axes of text buttons
        ax_sample_text_box = self.fig.add_axes([0.1, 0.2, 0.03, 0.075])
        ax_lead_text_box = self.fig.add_axes([0.1, 0.15, 0.03, 0.075])

        # Init text buttons
        text_sample_button = TextBox(ax_sample_text_box, "Sample ID", initial=str(0))
        text_lead_button = TextBox(ax_lead_text_box, "Lead ID", initial=str(0))

        # Connect text buttons to callback function
        text_sample_button.on_submit(callback.submit_sample_data)
        text_lead_button.on_submit(callback.submit_lead_data)

        # Init prev and next buttons axes
        ax_lead_prev = self.fig.add_axes([0.1, 0.05, 0.1, 0.075])
        ax_lead_next = self.fig.add_axes([0.2, 0.05, 0.1, 0.075])
        ax_sample_prev = self.fig.add_axes([0.3, 0.05, 0.1, 0.075])
        ax_sample_next = self.fig.add_axes([0.4, 0.05, 0.1, 0.075])

        # Init prev and next buttons
        button_lead_next = Button(ax_lead_next, "lead >>")
        button_lead_prev = Button(ax_lead_prev, "lead <<")
        button_sample_next = Button(ax_sample_next, "sample >>")
        button_sample_prev = Button(ax_sample_prev, "sample <<")

        # Connect prev and next buttons to callback function
        button_lead_next.on_clicked(callback.lead_next)
        button_lead_prev.on_clicked(callback.lead_prev)
        button_sample_next.on_clicked(callback.sample_next)
        button_sample_prev.on_clicked(callback.sample_prev)

        # Init checkbox button axes and labels
        ax_checkbox = self.fig.add_axes([0.7, 0.05, 0.1, 0.075])
        labels = ["P"]
        activated = [False]

        # Init checkbox button
        checkbox_button = CheckButtons(ax_checkbox, labels, activated)

        plt.show()


mm = MarkUpper(file, "user_session.dat")
mm.run_markup()
