import os

import matplotlib.markers
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from matplotlib.widgets import RadioButtons
from matplotlib.backend_bases import MouseButton
from math import dist

import functions

ecg_file = np.load("ecg_ptbxl.npy", allow_pickle=True)  # file of ecg samples


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

        self.current_x = None  # Current x data of pressed event
        self.current_y = None  # Current y data of pressed event
        self.pressed = False  # State if button been pressed

        self.to_plot = functions.get_clean_signal(data[sample_id][:, lead_id], 100)  # current data to plot on the plot

        self.button_mouse_press = self.fig.canvas.mpl_connect("button_press_event", self.onclick)
        self.pick = self.fig.canvas.mpl_connect("pick_event", self.onpick)
        self.release = self.fig.canvas.mpl_connect("button_release_event", self.onrelease)
        self.key_press = self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

        self.filename = "test.npy"

        # If markup file exist take that file as a data else create a new one
        if os.path.exists(self.filename):
            self.parameters = np.load(self.filename, allow_pickle=True)
        else:
            self.parameters = [
                [[[] for _ in range(12)] for _ in range(self.quantity_samples)] for _ in range(8)
            ]

        self.ids = {
            "P": 0,
            "Q": 1,
            "R": 2,
            "S": 3,
            "T": 4,
            "P_Int": 5,
            "Q_Int": 6,
            "R_Int": 7,
        }

        self.radio_labels = ["P", "Q", "R", "S", "T", "P_Int", "Q_Int", "R_Int"]  # list of labels for checkbox
        self.activated_checkbox = [
            False, False, False, False, False, False, False, False
        ]  # list of activated parameters

        # Plot chosen parameter as point with specific marker
        # Scatter of P amplitude parameter
        scatter_p = plt.scatter(
            x=self.get_parameter_xdata("P"),
            y=self.get_parameter_ydata("P"),
            marker="X",
            c="red",
            picker=True,
            pickradius=5
        )

        # Scatter of Q amplitude parameter
        scatter_q = plt.scatter(
            x=self.get_parameter_xdata("Q"),
            y=self.get_parameter_ydata("Q"),
            marker="X",
            c="blue",
            picker=True,
            pickradius=5
        )

        # Scatter of Q amplitude parameter
        scatter_r = plt.scatter(
            x=self.get_parameter_xdata("R"),
            y=self.get_parameter_ydata("R"),
            marker="X",
            c="black",
            picker=True,
            pickradius=5
        )

        # Scatter of Q amplitude parameter
        scatter_s = plt.scatter(
            x=self.get_parameter_xdata("S"),
            y=self.get_parameter_ydata("S"),
            marker="X",
            c="green",
            picker=True,
            pickradius=5
        )

        # Scatter of T amplitude parameter
        scatter_t = plt.scatter(
            x=self.get_parameter_xdata("T"),
            y=self.get_parameter_ydata("T"),
            marker="X",
            c="purple",
            picker=True,
            pickradius=5
        )

        # Scatter of P interval
        scatter_p_intervals = plt.scatter(
            x=self.get_parameter_xdata("P_Int"),
            y=self.get_parameter_ydata("P_Int"),
            marker=matplotlib.markers.CARETDOWNBASE,
            c="black",
            picker=True,
            pickradius=5
        )

        # Scatter of Q interval
        scatter_q_intervals = plt.scatter(
            x=self.get_parameter_xdata("Q_Int"),
            y=self.get_parameter_ydata("Q_Int"),
            marker=matplotlib.markers.CARETDOWNBASE,
            c="blue",
            picker=True,
            pickradius=5
        )

        # Scatter of R parameter
        scatter_r_intervals = plt.scatter(
            x=self.get_parameter_xdata("R_Int"),
            y=self.get_parameter_ydata("R_Int"),
            marker=matplotlib.markers.CARETDOWNBASE,
            c="purple",
            picker=True,
            pickradius=5
        )

        # An array of all scatters
        self.scatters = np.array([
            scatter_p,
            scatter_q,
            scatter_r,
            scatter_s,
            scatter_t,
            scatter_p_intervals,
            scatter_q_intervals,
            scatter_r_intervals
        ])

        # Make every scatter and bound in array invisible
        for scatter in self.scatters:
            scatter.set_visible(False)

    def get_parameter_ydata(self, parameter_id):
        # Collect current x data of given parameter
        parsed_word = self.parameter_id.split("_")

        if "Int" not in parsed_word:
            current = np.array(
                self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][self.lead_id % 12]
            )
            return np.array([data[1] for data in current])
        else:
            current = np.array(
                self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][self.lead_id % 12]
            )

            return np.array([np.array(data[:, 1]) for data in current]).flatten()

    def get_parameter_xdata(self, parameter_id):
        # Collect current y data of given parameter
        parsed_word = self.parameter_id.split("_")

        if "Int" not in parsed_word:
            current = np.array(
                self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][self.lead_id % 12]
            )
            return np.array([data[0] for data in current])
        else:
            current = np.array(
                self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][self.lead_id % 12]
            )

            return np.array([np.array(data[:, 0]) for data in current]).flatten()

    def lead_next(self, event):
        self.lead_id += 1  # Increment lead id
        i = self.lead_id % 12  # Make sure that lead id stays within the ring
        self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, i], 100)  # Update data to plot

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
        self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, i], 100)  # Current data to plot

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
        self.to_plot = functions.get_clean_signal(self.data[i][:, 0], 100)

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
        self.to_plot = functions.get_clean_signal(self.data[i][:, 0], 100)

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
            self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, 0], 100)

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        if int(text) < 0 or int(text) > self.quantity_samples - 1:
            self.sample_id = self.sample_id
            self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, 0], 100)

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{0} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        else:
            self.sample_id = int(text)
            self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, 0], 100)

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
            self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, self.lead_id], 100)

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        if int(text) < 0 or int(text) > self.quantity_samples - 1:
            self.lead_id = self.lead_id
            self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, self.lead_id], 100)

            self.ax.set_xlabel(f"{self.sample_id % self.quantity_samples} / 21429\n{self.lead_id % 12} / 11")
            self.line.set_ydata(self.to_plot)

            plt.draw()

        else:
            self.lead_id = int(text)
            self.to_plot = functions.get_clean_signal(self.data[self.sample_id][:, self.lead_id], 100)

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

    def get_minimal_distance(self, x, y, line_x, line_y):
        distances = np.array([np.abs(x - x_) + np.abs((y * 100) - (y_ * 100)) for x_, y_ in zip(line_x, line_y)])
        return np.min(distances)

    def onclick(self, event):
        self.pressed = True  # Change current pressed state to True (button been pressed)
        toolbar_condition = self.ax.get_navigate_mode()  # Check if toolbar is active

        roi_points = 5

        x = event.xdata
        y = event.ydata

        line_x = self.line.get_xdata().astype(int)  # line x data
        line_y = self.line.get_ydata()  # line y data

        # if event is left mouse button press and the clicked point within the subplot
        if event.inaxes == self.line.axes and event.button is MouseButton.LEFT \
                and "Int" not in self.parameter_id.split("_") and toolbar_condition is None:
            eps_interval_x = np.array(line_x[int(x) - roi_points:int(x) + roi_points])
            eps_interval_y = np.array(line_y[eps_interval_x[0]:eps_interval_x[-1]])

            self.get_minimal_distance(x, y, eps_interval_x, eps_interval_y)
            self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][
                self.lead_id % 12].append((event.xdata, event.ydata))
            self.get_scatter_update(self.radio_labels.index(self.parameter_id))

        # If event middle mouse and selected parameter is any interval
        if event.inaxes == self.line.axes and event.button is MouseButton.MIDDLE \
                and "Int" in self.parameter_id.split("_"):
            self.current_x = event.xdata
            self.current_y = event.ydata

        plt.draw()

    def onrelease(self, event):
        self.pressed = False
        if event.button is MouseButton.MIDDLE and "Int" in self.parameter_id.split("_"):
            x = event.xdata
            y = event.ydata

            self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][
                self.lead_id % 12].append(
                ((self.current_x, self.current_y), (x, y))
            )

            self.get_scatter_update(self.radio_labels.index(self.parameter_id))

            plt.draw()

    def onpick(self, event):
        if event.mouseevent.button == 3 and "Int" in self.parameter_id.split("_"):
            ind = event.ind[0]
            interval_to_delete = int(np.ceil((ind + 1) * 0.5)) - 1
            self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][self.lead_id % 12].pop(
                interval_to_delete)
            self.get_scatter_update(self.radio_labels.index(self.parameter_id))
        else:
            ind = event.ind[0]
            self.parameters[self.ids[self.parameter_id]][self.sample_id % self.quantity_samples][self.lead_id % 12].pop(
                ind)
            self.get_scatter_update(self.radio_labels.index(self.parameter_id))

        plt.draw()

    def on_key_press(self, event):
        if event.key == 'q':
            np.save(self.filename, self.parameters)


class MarkUpper:
    def __init__(self, data_path):
        self.data = data_path

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

        # plot the first data

        self.line, = self.ax.plot(functions.get_clean_signal(data_path[0][:, 0], _sampling_rate=100))

    def run_markup(self):
        # Call callback function class
        callback = Callback(self.data, 21430, 0, 0, self.ax, self.fig, self.line)

        # Init axes of text buttons
        ax_sample_text_box = self.fig.add_axes([0.1, 0.2, 0.04, 0.025])
        ax_lead_text_box = self.fig.add_axes([0.1, 0.15, 0.04, 0.025])

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
        ax_radio = self.fig.add_axes([0.7, 0.05, 0.1, 0.095])

        labels = ["P", "Q", "R", "S", "T", "P_Int", "Q_Int", "R_Int"]
        activated = [False, False, False, False, False, False, False, False]

        # Init radio button
        radio_button = RadioButtons(ax_radio, labels, activated)

        # Connect radio button to callback function
        radio_button.on_clicked(callback.radio_click)

        plt.show()


mm = MarkUpper(ecg_file)
mm.run_markup()
