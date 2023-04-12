import streamlit as st
import numpy as np
import functions as fns
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
import json
import os
import plotly.express as px

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
                    # {"label": i, "value": i} for i in range(self.quantity_samples)
                    {"label": keys, "value": keys} for keys in self.ids.keys()
                ],
                value=self.current_parameter
            ),

            dcc.Graph(
                figure=self.fig,
                id="ecg_layout",
            ),

            html.Div(
                id="where"
            )
        ])

        @self.app.callback(
            Output(component_id="ecg_layout", component_property="figure"),
            [
                Input(component_id="drop", component_property="value"),
                Input(component_id="ecg_layout", component_property="hoverData"),
                Input(component_id="ecg_layout", component_property="clickData")
            ]
        )
        def visual_updater(value, hoverData, clickData):
            # print(value)
            self.current_parameter = value

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

                # if last marked figure's number is higher than 12 it means that parameter was triggered
                if self.last_marked_lead >= 12:
                    x, y = self.last_marked_lead_xy["x"], self.last_marked_lead_xy["y"]
                    for coordinates in self.parameters[self.ids[self.current_parameter]][self.sample_number][
                        self.last_marked_lead % 12]:
                        if int(coordinates[0]) == x:
                            self.parameters[self.ids[self.current_parameter]][self.sample_number][
                                self.last_marked_lead % 12].remove(coordinates)
                else:
                    print(f"Last marked figure was lead: {self.last_marked_lead}")
                    self.parameters[self.ids[self.current_parameter]][self.sample_number][self.last_marked_lead].append(
                        [self.last_marked_lead_xy["x"], self.last_marked_lead_xy["y"]]
                    )

            # update vertical line
            for trace in self.fig.data:
                trace.update(xaxis="x")
            # for rows in range(self.view[self.view_condition][0]):
            #     self.fig.update_traces(
            #         patch=go.Scatter(
            #             mode="markers",
            #             x=self.get_xy_data(rows)[0],
            #             y=self.get_xy_data(rows)[1],
            #             marker=dict(
            #                 color=self.parameters_color[self.current_parameter],
            #                 size=6,
            #             ),
            #             hoverinfo="name + x + y "
            #         ),
            #         selector=dict(name=f"({str((rows + 12))})"),
            #         row=rows + 1, col=1
            #     )

            # if not hoverData:
            #     ...
            # else:
            #     self.last_marked_lead = json.loads(
            #         json.dumps(
            #             {k: hoverData["points"][0][k] for k in ["curveNumber"]}
            #         )
            #     )["curveNumber"]
            #
            #     self.last_marked_lead_xy = json.loads(
            #         json.dumps(
            #             {k: hoverData["points"][0][k] for k in ["x", "y"]}
            #         )
            #     )

            # print(f"x: {self.last_marked_lead_xy['x']} y: {self.last_marked_lead_xy['y']}")
            # x = self.get_closest_point_index(self.last_marked_lead_xy["x"])

            return self.fig

        # def update_markers(clickData):
        #     if not clickData:
        #         ...
        #     else:
        #         self.last_marked_lead = json.loads(
        #             json.dumps(
        #                 {k: clickData["points"][0][k] for k in ["curveNumber"]}
        #             )
        #         )["curveNumber"]
        #
        #         self.last_marked_lead_xy = json.loads(
        #             json.dumps(
        #                 {k: clickData["points"][0][k] for k in ["x", "y"]}
        #             )
        #         )
        #
        #         print(f"Last marked lead: {self.last_marked_lead}")
        #         self.parameters[self.ids[self.current_parameter]][self.sample_number][self.last_marked_lead].append(
        #             [self.last_marked_lead_xy["x"], self.last_marked_lead_xy["y"]]
        #         )

    def get_closest_point_index(self, x):
        # get closets p param in 0 lead

        p_parameters = self.parameters[self.ids["P"]][self.sample_number][self.last_marked_lead]

        dists = [int(np.abs(x - param[0])) for param in p_parameters]
        min_dist = np.min(dists)

        return int(p_parameters[dists.index(min_dist)][0])

    def get_xy_data(self, lead):
        current = np.array(
            self.parameters[self.ids[self.current_parameter]][self.sample_number][lead]
        )

        x_d = np.array([int(data[0]) for data in current])
        x_y = np.array([data[1] for data in current])

        if x_d.size == 0:
            return np.array([np.nan]), np.array([np.nan])

        return x_d, x_y

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
                    name=self.lead_names[rows]
                ),
                row=rows + 1, col=1,
            )

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

        self.fig.update_layout({
            ax: {
                "showspikes": True,
                "spikemode": "across",
                "spikedash": "solid",
                "spikesnap": "cursor",
                "spikethickness": 2,
                "spikecolor": "blue"
            } for ax in self.fig.to_dict()["layout"] if ax[0:3] == "xax"})

        # self.fig.update_traces(xaxis="x")
        self.fig.update_layout(showlegend=False)
        self.fig.update_layout(height=950, width=1500)
        self.fig.layout.hovermode = 'closest'
        self.fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="LightSteelBlue",
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
