import os

import matplotlib.markers
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from matplotlib.widgets import RadioButtons

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
    def __init__(self, data, quantity_samples, sample_id, lead_id, plot, fig):
        self.fig = fig
        self.ax = plot  # plot itself
        self.data = data  # data file containing samples to plot
        self.quantity_samples = quantity_samples  # quantity of samples
        self.lead_id = lead_id  # current lead id
        self.sample_id = sample_id  # current sample id
        self.parameter_id = "P"  # current parameter to mark

        self.to_plot = data[sample_id][:, lead_id]  # current data to plot on the plot
        self.transparent_color = (1, 1, 0, 0)  # transparent color to hide marked up data

        # Dict of parameters to mark
        self.parameters = {
            "P": [[[(np.random.randint(12, 189), 0.2), (100, 0.2), (1000, 0.2)] for _ in range(12)] for _ in
                  range(self.quantity_samples)],
            "Q": [[[(100, 0.2), (250, 0.5), (340, 0.43)] for _ in range(12)] for _ in range(self.quantity_samples)]
        }

        # Set different markers to each parameter
        self.markers_box = {
            "P": matplotlib.markers.CARETUPBASE,
            "P interval": (matplotlib.markers.CARETLEFT, matplotlib.markers.CARETRIGHT, "blue"),
            "Q": "X",
            "QRS": (matplotlib.markers.CARETLEFT, matplotlib.markers.CARETRIGHT, "red")
        }

        self.checkbox_labels = ["P", "Q"]  # list of labels for checkbox
        self.activated_checkbox = [False, False]  # list of activation in checkbox

        # A list of color to plot
        self.color_list = (
            "red",
            "blue",
            "black",
            "green",
            "orange",
        )

        # Plot chosen parameter as point with specific marker
        scatter_p = plt.scatter(
            x=self.get_parameter_xdata("P"),
            y=self.get_parameter_ydata("P"),
            marker="X",
            c="red",
        )

        scatter_q = plt.scatter(
            x=self.get_parameter_xdata("Q"),
            y=self.get_parameter_ydata("Q"),
            marker="D",
            c="blue",
        )

        self.scatters = np.array([scatter_p, scatter_q])

        for scatter in self.scatters:
            scatter.set_visible(False)

    def get_parameter_ydata(self, parameter_id):
        sample_id = self.sample_id
        lead_id = self.lead_id
        current = np.array(self.parameters[parameter_id][sample_id][lead_id])

        return np.array([data[1] for data in current])

    def get_parameter_xdata(self, parameter_id):
        sample_id = self.sample_id
        lead_id = self.lead_id
        current = np.array(self.parameters[parameter_id][sample_id][lead_id])
        return np.array([data[0] for data in current])

    def lead_next(self, event):
        self.lead_id += 1
        i = self.lead_id % 12
        self.to_plot = self.data[self.sample_id][:, i]

        self.ax.clear()
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{i % 12} / 11")
        self.ax.plot(self.to_plot)

        plt.draw()

    def lead_prev(self, event):
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

    def get_scatter_update(self, scatter_id):
        self.scatters[scatter_id].set_offsets(
            [self.get_parameter_xdata(self.checkbox_labels[scatter_id]),
             self.get_parameter_ydata(self.checkbox_labels[scatter_id])]
        )

    def check_box_click(self, label):
        self.parameter_id = label
        index = self.checkbox_labels.index(label)

        for indx, value in enumerate(self.parameters):
            if indx == index:
                self.get_scatter_update(index)
                self.scatters[indx].set_visible(True)
            else:
                self.scatters[indx].set_visible(False)

        plt.draw()


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
        callback = Callback(self.data, 21430, 0, 0, self.ax, self.fig)

        # Init cursor
        # cursor = Cursor(self.ax, horizOn=False, vertOn=False)

        # Connect cursor to specific event
        # cursor.connect_event("button_press_event", callback.mouse_click)

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

        # Init radio button axes and labels
        ax_radio = self.fig.add_axes([0.7, 0.05, 0.1, 0.075])
        labels = ["P", "Q"]
        activated = [False, False]

        # Init radio button
        radio_button = RadioButtons(ax_radio, labels, activated)

        # Connect radio button to callback function
        radio_button.on_clicked(callback.check_box_click)

        plt.show()


mm = MarkUpper(file, "user_session.dat")
mm.run_markup()
