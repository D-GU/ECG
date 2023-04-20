import numpy as np
import functions as fns
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import json
import os

from dash.dependencies import Input, Output
from dash import dcc
from dash import html
from plotly.subplots import make_subplots


class AppECG:
    def __init__(self, data, _sampling_rate, _recording_speed, _recording_time):
        self.data = data
        self.sampling_rate = sampling_rate
        self.recording_speed = recording_speed
        self.recording_time = recording_time
        self.view_condition = 1  # which lead interface is chosen
        self.sample_number = 0
        self.quantity_samples = data.shape[0]
        self.ecg_matrix = self.update_matrix()

        # interface: 6 rows x 2 columns or 12 rows x 1 column
        self.view = {
            0: (6, 2),
            1: (12, 1)
        }

        # a mask where each lead is representing specific position
        self.view_settings = {
            0: ((0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)),
            1: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        }

        self.lead_names = [
            "i", "ii", "iii", "aVF", "aVR", "aVL", "V1", "V2", "V3", "V4", "V5", "V6"
        ]

        self.grid_minor_bound = self.sampling_rate * self.recording_speed
        self.step_minor = (self.grid_minor_bound / self.recording_speed) / self.recording_speed

        self.fig = make_subplots(
            rows=12, cols=1,

            specs=[
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
                [{}],
            ],

            subplot_titles=(
                self.lead_names[0],
                self.lead_names[1],
                self.lead_names[2],
                self.lead_names[3],
                self.lead_names[4],
                self.lead_names[5],
                self.lead_names[6],
                self.lead_names[7],
                self.lead_names[8],
                self.lead_names[9],
                self.lead_names[10],
                self.lead_names[11],
                # "Ритмограмма"
            ),
            shared_xaxes=True,
            horizontal_spacing=0.035,
            vertical_spacing=0.001,
        )

        self.current_parameter = "P"
        self.p_parameter_median = 0
        self.filename = "test.npy"

        # If markup file exist take that file as a data else create a new one
        if os.path.exists(self.filename):
            self.parameters = np.load(self.filename, allow_pickle=True)
        else:
            self.parameters = [
                [[[] for _ in range(12)] for _ in range(self.quantity_samples)] for _ in range(8)
            ]

        self.parameters_color = {
            "P": "tomato",
            "Q": "LightSkyBlue",
            "R": "violet",
            "S": "olive",
            "T": "gold",
            "P_Int": "brown",
            "Q_Int": "orange",
            "R_Int": "pink",
        }

        # each parameter id in data
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

        self.last_marked_lead = None
        self.last_marked_lead_xy = None

        self.app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

        self.app.layout = html.Div([
            html.H3("ECG"),
            html.Div(
                [
                    dbc.RadioItems(
                        id="radios",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                        options=[parameter for parameter in self.ids.keys()],
                        value=self.current_parameter,
                    ),
                    html.Div(id="output"),
                ],
                className="radio-group",
            ),

            dcc.Graph(
                figure=self.fig,
                id="ecg_layout",
                config={
                    "scrollZoom": True,
                    "responsive": True
                },

            ),

            html.Div(
                id="where"
            )
        ])

        @self.app.callback(
            [Output("output", "children"),
             Output(component_id="ecg_layout", component_property="figure")],
            [
                Input("radios", "value"),
                Input(component_id="ecg_layout", component_property="clickData")
            ]
        )
        def visual_updater(value, clickData):
            if value == self.current_parameter:
                pass
            else:
                self.current_parameter = value
                self.update_markers()

            if clickData:
                self.last_marked_lead = json.loads(
                    json.dumps(
                        {k: clickData["points"][0][k] for k in ["curveNumber"]}
                    )
                )["curveNumber"]

                self.last_marked_lead_xy = json.loads(
                    json.dumps(
                        {k: clickData["points"][0][k] for k in ["x", "y"]}
                    )
                )

                # if last marked figure's number is higher than 12 it means that parameter was triggered
                if self.last_marked_lead >= 12:
                    x, y = self.last_marked_lead_xy["x"], self.last_marked_lead_xy["y"]
                    for coordinates in self.parameters[self.ids[self.current_parameter]][self.sample_number][
                        self.last_marked_lead % 12]:

                        if int(coordinates[0]) == x:
                            self.parameters[self.ids[self.current_parameter]][self.sample_number][
                                self.last_marked_lead % 12].remove(coordinates)
                    self.update_markers()
                else:
                    self.parameters[self.ids[self.current_parameter]][self.sample_number][self.last_marked_lead].append(
                        [self.last_marked_lead_xy["x"], self.last_marked_lead_xy["y"]]
                    )
                    self.update_markers()

            # update vertical line
            for trace in self.fig.data:
                trace.update(xaxis="x")

            return f"Selected value: {self.current_parameter}", self.fig

    def update_markers(self):
        for lead, trace in enumerate(self.fig.data[12::]):
            trace.update(
                x=self.get_xy_data(lead)[0],
                y=self.get_xy_data(lead)[1],
                marker=dict(
                    color=self.parameters_color[self.current_parameter],
                    size=6,
                ),
                mode="markers",
                name=f"{str(lead + 12)}"
            )

    def get_closest_point_index(self, x):
        p_parameters = self.parameters[self.ids["P"]][self.sample_number][self.last_marked_lead]

        dists = [int(np.abs(x - param[0])) for param in p_parameters]
        min_dist = np.min(dists)

        return int(p_parameters[dists.index(min_dist)][0])

    def get_xy_data(self, lead):
        parsed_word = self.current_parameter.split("_")

        if "Int" not in parsed_word:
            current = np.array(
                self.parameters[self.ids[self.current_parameter]][self.sample_number][lead]
            )

            x = np.array([int(data[0]) for data in current])
            y = np.array([data[1] for data in current])

            if x.size == 0:
                return np.array([np.nan]), np.array([np.nan])

            return x, y
        else:
            x = []
            y = []

            for current in self.parameters[self.ids[self.current_parameter]][self.sample_number][lead]:
                for x_cur, y_cur in current:
                    x.append(int(x_cur))
                    y.append(y_cur)

            x = np.array(x)
            y = np.array(y)

            if x.size == 0:
                return np.array([np.nan]), np.array([np.nan])

            return x, y

    def update_matrix(self):
        return fns.get_clean_matrix(
            np.array([self.data[self.sample_number][:, i] for i in range(12)]), self.sampling_rate
        )

    def make_plots(self):
        for rows in range(self.view[self.view_condition][0]):
            self.fig.add_trace(
                go.Line(
                    x=[i for i in range(1000)],
                    y=self.ecg_matrix[rows],
                    name=self.lead_names[rows],
                    line=dict(
                        color="black"
                    )
                ),
                row=rows + 1, col=1,
            )

        # Add the parameters markers on each subplot
        for rows in range(self.view[self.view_condition][0]):
            self.fig.add_trace(
                go.Scatter(
                    mode="markers",
                    x=self.get_xy_data(rows)[0],
                    y=self.get_xy_data(rows)[1],
                    name=f"{str((rows + 12))}",
                    marker=dict(
                        color=self.parameters_color[self.current_parameter],
                        size=6,
                    ),
                    hoverinfo="name + x + y"
                ),
                row=rows + 1, col=1,
            )

        # Update the layout by adding the vertical spike
        self.fig.update_layout({
            ax: {
                "showspikes": True,
                "spikemode": "across",
                "spikedash": "solid",
                "spikesnap": "cursor",
                "spikethickness": 2,
                "spikecolor": "blue"
            } for ax in self.fig.to_dict()["layout"] if ax[0:3] == "xax"}
        )

        # self.fig.update_traces(xaxis="x")
        self.fig.update_layout(showlegend=False)
        self.fig.update_layout(height=950, width=1500)

        self.fig.update_layout(yaxis_range=[-0.3, 0.5])
        self.fig.update_layout(xaxis_range=[0, self.sampling_rate * self.recording_time])
        # style the minor and major grids

        self.fig.update_xaxes(
            minor=dict(
                showgrid=True,
                tickmode="linear",
                tick0=0,
                dtick=self.step_minor,
                gridcolor="rgb(255,182,193)"
            ),

            tickmode="linear",
            tick0=0,
            dtick=self.sampling_rate,
            gridcolor="red"
        )

        # update the y-grid
        # self.fig.update_yaxes(
        #     minor=dict(
        #         showgrid=True,
        #         tick0=1,
        #         dtick=(self.step_minor / 100) * 2,
        #         gridcolor="rgb(255,182,193)"
        #     )
        # )

        # draw isoline
        self.fig.update_yaxes(
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=0.2,
        )


if __name__ == "__main__":
    ecg_file = np.load("ecg_ptbxl.npy", allow_pickle=True)
    ecg_sample = ecg_file[0][:, 0]
    sample_number = 0
    sampling_rate = 100
    recording_speed = 25
    recording_time = 10

    ecg = AppECG(
        ecg_file,
        *(sampling_rate,
          recording_time,
          recording_speed)
    )
    ecg.make_plots()
    ecg.app.run_server(debug=True, use_reloader=False)
    # np.save(ecg.filename, ecg.parameters)
