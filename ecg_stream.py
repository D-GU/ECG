import streamlit as st
import numpy as np
import functions as fns
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
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
        self.view_condition = 1
        self.sample_number = 0
        self.quantity_samples = data.shape[0]
        self.ecg_matrix = self.update_matrix()

        self.view = {
            0: (6, 2),
            1: (12, 1)
        }

        self.view_settings = {
            0: ((0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)),
            1: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        }

        self.lead_names = [
            "i", "ii", "iii", "aVF", "aVR", "aVL", "V1", "V2", "V3", "V4", "V5", "V6"
        ]

        self.range = [350, 700]

        self.fig = make_subplots(
            rows=13, cols=1,

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
            horizontal_spacing=0.045,
            vertical_spacing=0.01,
        )

        self.current_parameter = "P"

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

        self.last_marked_lead = None
        self.last_marked_lead_xy = None

        self.app = dash.Dash()

        self.app.layout = html.Div([
            html.H3("ECG"),

            dcc.Dropdown(
                id="drop",
                options=[
                    {"label": i, "value": i} for i in range(self.quantity_samples)
                ],
                value=self.sample_number
            ),

            dcc.Graph(
                figure=self.fig,
                id="ecg_layout",
                config={
                    'modeBarButtonsToAdd': [
                        'drawline',
                        'drawopenpath',
                        'drawclosedpath',
                        'eraseshape'
                    ],
                    "scrollZoom": True,
                }
            ),

            html.Div(
                id="where"
            )
        ])

        @self.app.callback(
            Output(component_id="ecg_layout", component_property="figure"),
            [
                Input(component_id="drop", component_property="value"),
                Input(component_id="ecg_layout", component_property="clickData")
            ]
        )
        def visual_updater(value, clickData):
            selected_value = value

            self.sample_number = selected_value

            self.ecg_matrix = self.update_matrix()

            for rows in range(self.view[self.view_condition][0]):
                self.fig.update_traces(
                    patch=go.Scatter(
                        x=[i for i in range(1000)],
                        y=self.ecg_matrix[rows],
                        name=self.lead_names[rows]
                    ),
                    row=rows + 1, col=1
                )

            for rows in range(self.view[self.view_condition][0]):
                for peaks in self.get_xy_data(rows)[0]:
                    self.fig.update_shapes(
                        selector=dict(
                            line={'color': 'tomato', 'width': 5},
                            x0=peaks,
                            x1=peaks,
                            y0=0.02,
                            y1=-0.02,
                            visible=True,
                            layer="below",
                        ),
                        row=rows + 1, col=1
                    )

            if not clickData:
                ...
            else:
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

                self.parameters[self.ids[self.current_parameter]][self.sample_number][self.last_marked_lead].append(
                    (self.last_marked_lead_xy["x"], self.last_marked_lead_xy["y"])
                )

            return self.fig

    def get_closest_point_index(self, vline_x):
        p_parameters = self.parameters[self.ids["P"]][self.sample_number][0]
        min_dist = np.minimum(np.array([abs(vline_x - param) for param in p_parameters]))
        return p_parameters.index(min_dist)

    def get_xy_data(self, lead):
        current = np.array(
            self.parameters[self.ids[self.current_parameter]][self.sample_number][
                lead]
        )
        return np.array([int(data[0]) for data in current]), np.array([data[1] for data in current])

    def update_matrix(self):
        return fns.get_clean_matrix(
            np.array([self.data[self.sample_number][:, i] for i in range(12)]), self.sampling_rate
        )

    def make_plots(self):
        for rows in range(self.view[self.view_condition][0]):
            self.fig.add_trace(
                go.Scatter(
                    x=[i for i in range(1000)],
                    y=self.ecg_matrix[rows],
                    name=self.lead_names[rows]
                ),
                row=rows + 1, col=1
            )

        for rows in range(self.view[self.view_condition][0]):
            for peaks in self.get_xy_data(rows)[0]:
                self.fig.add_shape(
                    line={"color": "tomato", "width": 3},
                    x0=peaks,
                    x1=peaks,
                    y0=0.03,
                    y1=-0.03,
                    layer="above"
                )

        self.fig.update_layout({
            ax: {
                "showspikes": True,
                "spikemode": "across",
                "spikedash": "solid",
                "spikesnap": "cursor",
                "spikethickness": 1,
                "spikecolor": "tomato"
            } for ax in self.fig.to_dict()["layout"] if ax[0:3] == "xax"})

        self.fig.update_traces(xaxis="x")
        self.fig.update_layout(showlegend=True)
        self.fig.update_layout(height=950, width=1500)


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
