import os

import matplotlib.markers
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import Cursor

# If session file is already exists then
# read the data from it and continue markup it
# if not os.path.isfile("user_session.dat"):
#     with open("user_session.dat", "wb") as session_file:
#         session_file.write(bytearray([0, 0]))

file = np.load("ecg_ptbxl.npy", allow_pickle=True)
sample = file[0][:, 0]


class Callback:
    def __init__(self, data, quantity_samples, sample_id, lead_id, plot, fig, line):
        self.fig = fig  # A figure
        self.line = line  # Line
        self.ax = plot  # plot itself
        self.data = data  # data file containing samples to plot
        self.quantity_samples = quantity_samples  # quantity of samples
        self.lead_id = lead_id  # current lead id
        self.sample_id = sample_id  # current sample id
        self.parameter_id = "P"  # current parameter to mark

        self.to_plot = data[sample_id][:, lead_id]  # current data to plot on the plot

        # Dict of parameters to mark
        self.parameters = {
            "P": [[[] for _ in range(12)] for _ in
                  range(self.quantity_samples)],
            "Q": [[[] for _ in range(12)] for _ in range(self.quantity_samples)]
        }

        # Set different markers to each parameter
        self.markers_box = {
            "P": matplotlib.markers.CARETUPBASE,
            "P interval": (matplotlib.markers.CARETLEFT, matplotlib.markers.CARETRIGHT, "blue"),
            "Q": "X",
            "QRS": (matplotlib.markers.CARETLEFT, matplotlib.markers.CARETRIGHT, "red")
        }

        self.radio_labels = ["P", "Q"]  # list of labels for checkbox
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
            picker=True,
            pickradius=5
        )

        scatter_q = plt.scatter(
            x=self.get_parameter_xdata("Q"),
            y=self.get_parameter_ydata("Q"),
            marker="D",
            c="blue",
            picker=True,
            pickradius=5
        )

        # Scatters array
        self.scatters = np.array([scatter_p, scatter_q])

        # Make every scatter in array invisible
        for scatter in self.scatters:
            scatter.set_visible(False)

    def get_parameter_ydata(self, parameter_id):
        # Collect current x data of given parameter
        current = np.array(
            self.parameters[self.parameter_id][self.sample_id % self.quantity_samples][self.lead_id % 12]
        )
        return np.array([data[1] for data in current])

    def get_parameter_xdata(self, parameter_id):
        # Collect current y data of given parameter
        current = np.array(
            self.parameters[self.parameter_id][self.sample_id % self.quantity_samples][self.lead_id % 12]
        )
        return np.array([data[0] for data in current])

    def lead_next(self, event):
        self.lead_id += 1  # Increment lead id
        i = self.lead_id % 12  # Make sure that lead id stays within the ring
        self.to_plot = self.data[self.sample_id][:, i]  # Update data to plot

        # Update scatter parameters to plot
        self.get_scatter_update(
            self.radio_labels.index(self.parameter_id)
        )

        # If scatters visibility is on -> set_visible(True)
        # else set_visible(False)
        self.scatters[
            self.radio_labels.index(self.parameter_id)
        ].set_visible(self.activated_checkbox[self.radio_labels.index(self.parameter_id)])

        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{i % 12} / 11")  # Update xlabel

        # Set updated data
        self.line.set_ydata(self.to_plot)

        plt.draw()

    def lead_prev(self, event):
        self.lead_id -= 1  # Decrement lead_id
        i = self.lead_id % 12  # Make sure lead id stays within the ring
        self.to_plot = self.data[self.sample_id][:, i]  # Current data to plot

        # Update scatter parameters to plot
        self.get_scatter_update(
            self.radio_labels.index(self.parameter_id)
        )

        # If scatters visibility is on -> set_visible(True)
        # else set_visible(False)
        self.scatters[
            self.radio_labels.index(self.parameter_id)
        ].set_visible(self.activated_checkbox[self.radio_labels.index(self.parameter_id)])

        # Update xlabel
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{i % 12} / 11")

        # Set updated data
        self.line.set_ydata(self.to_plot)

        plt.draw()

    def sample_next(self, event):
        self.sample_id += 1
        i = self.sample_id % self.quantity_samples
        self.to_plot = self.data[i][:, 0]

        # Update scatter parameters to plot
        self.get_scatter_update(
            self.radio_labels.index(self.parameter_id)
        )

        # If scatters visibility is on -> set_visible(True)
        # else set_visible(False)
        self.scatters[
            self.radio_labels.index(self.parameter_id)
        ].set_visible(self.activated_checkbox[self.radio_labels.index(self.parameter_id)])

        # Update xlabel
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")

        # Set updated data
        self.line.set_ydata(self.to_plot)

        plt.draw()

    def sample_prev(self, event):
        self.sample_id -= 1
        i = self.sample_id % self.quantity_samples
        self.to_plot = self.data[i][:, 0]

        # Update scatter parameters to plot
        self.get_scatter_update(
            self.radio_labels.index(self.parameter_id)
        )

        # If scatters visibility is on -> set_visible(True)
        # else set_visible(False)
        self.scatters[
            self.radio_labels.index(self.parameter_id)
        ].set_visible(self.activated_checkbox[self.radio_labels.index(self.parameter_id)])

        # Update xlabel
        self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")

        # Set updated data
        self.line.set_ydata(self.to_plot)

        plt.draw()

    def submit_sample_data(self, text):
        if not text.isnumeric():
            self.sample_id = self.sample_id
            self.to_plot = self.data[self.sample_id][:, 0]

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        if int(text) < 0 or int(text) > self.quantity_samples - 1:
            self.sample_id = self.sample_id
            self.to_plot = self.data[self.sample_id][:, 0]

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        else:
            self.sample_id = int(text)
            self.to_plot = self.data[self.sample_id][:, 0]

            # Update scatter parameters to plot
            self.get_scatter_update(
                self.radio_labels.index(self.parameter_id)
            )

            # If scatters visibility is on -> set_visible(True)
            # else set_visible(False)
            self.scatters[
                self.radio_labels.index(self.parameter_id)
            ].set_visible(self.activated_checkbox[self.radio_labels.index(self.parameter_id)])

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

    def submit_lead_data(self, text):
        if not text.isnumeric():
            self.lead_id = self.lead_id
            self.to_plot = self.data[self.sample_id][:, self.lead_id]

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        if int(text) < 0 or int(text) > self.quantity_samples - 1:
            self.lead_id = self.lead_id
            self.to_plot = self.data[self.sample_id][:, self.lead_id]

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        else:
            self.lead_id = int(text)
            self.to_plot = self.data[self.sample_id][:, self.lead_id]

            # Update scatter parameters to plot
            self.get_scatter_update(
                self.radio_labels.index(self.parameter_id)
            )

            # If scatters visibility is on -> set_visible(True)
            # else set_visible(False)
            self.scatters[
                self.radio_labels.index(self.parameter_id)
            ].set_visible(self.activated_checkbox[self.radio_labels.index(self.parameter_id)])

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

    def get_scatter_update(self, scatter_id):
        updated_data = np.c_[
            self.get_parameter_xdata(self.radio_labels[scatter_id]),
            self.get_parameter_ydata(self.radio_labels[scatter_id])
        ]
        self.scatters[scatter_id].set_offsets(updated_data)

    def radio_click(self, label):
        self.parameter_id = label
        index = self.radio_labels.index(label)

        for indx, value in enumerate(self.parameters):
            if indx == index:
                self.get_scatter_update(index)  # update scatter
                self.scatters[indx].set_visible(True)  # set it visible
                self.activated_checkbox[indx] = True  # set visibility parameter to True
            else:
                self.scatters[indx].set_visible(False)  # set current parameter to False
                self.activated_checkbox[indx] = False  # set visibility parameter to False

        plt.draw()

    def onclick(self, event):
        if event.inaxes == self.line.axes:
            self.parameters[self.parameter_id][self.sample_id][self.lead_id].append((event.xdata, event.ydata))
            self.get_scatter_update(self.radio_labels.index(self.parameter_id))

        plt.draw()

    def onpick(self, event):
        thisline = event.artist
        ind = event.ind[0]

        if event.artist == any(self.parameters[self.parameter_id][self.sample_id][self.lead_id]):
            x = event.xdata
            y = event.ydata

            self.parameters[self.parameter_id][self.sample_id][self.lead_id].remove(x, y)
            self.get_scatter_update(self.radio_labels.index(self.parameter_id))
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
            left=0.001, bottom=0.298, right=1, top=0.9, wspace=0.2, hspace=0.9
        )

        # Set xlabel
        self.ax.set_xlabel("0 / 21429\n0 / 11")

        self.ax.set_xlim(-5, self.data.shape[1] + 10)  # Set x limits
        self.ax.set_ylim(-0.5, 1)  # Set y limits

        self.line, = self.ax.plot(sample)

    def run_markup(self):
        # Call callback function class
        callback = Callback(self.data, 21430, 0, 0, self.ax, self.fig, self.line)

        # Init cursor
        # cursor = Cursor(self.ax, horizOn=False, vertOn=False)

        # Connect cursor to specific event
        self.fig.canvas.mpl_connect("button_press_event", callback.onclick)
        self.fig.canvas.mpl_connect("pick_event", callback.onpick)

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
        radio_button.on_clicked(callback.radio_click)

        plt.show()


mm = MarkUpper(file, "user_session.dat")
mm.run_markup()
