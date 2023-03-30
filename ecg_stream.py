import streamlit as st
import numpy as np
import functions as fns
import plotly
import plotly.graph_objects as go
import plotly.io
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import json

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
        self.view_condition = 0
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
            rows=6, cols=2,
            specs=[
                [{}, {}],
                [{}, {}],
                [{}, {}],
                [{}, {}],
                [{}, {}],
                [{}, {}]
            ],
            subplot_titles=(
                self.lead_names[0],
                self.lead_names[6],
                self.lead_names[1],
                self.lead_names[7],
                self.lead_names[2],
                self.lead_names[8],
                self.lead_names[3],
                self.lead_names[9],
                self.lead_names[4],
                self.lead_names[10],
                self.lead_names[5],
                self.lead_names[11]
            )
        )

        self.line_position = self.range[0]

        self.last_marked_lead = None
        self.last_marked_lead_xy = None

        self.make_plots()

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

            dcc.Slider(
                id="slider",
                min=self.range[0], max=self.range[1],
                value=self.range[0] + 1,
                step=0.1
            ),

            dcc.Graph(
                figure=self.fig,
                id="ecg_layout"
            ),

            dash.html.Div(
                id="where"
            )
        ])

        @self.app.callback(
            Output(component_id="ecg_layout", component_property="figure"),
            [
                Input(component_id="drop", component_property="value"),
                Input(component_id="slider", component_property="value"),
                Input(component_id="ecg_layout", component_property="clickData")
            ]
        )
        def visual_updater(value, pos_x, clickData):
            selected_value = value
            self.sample_number = selected_value

            self.ecg_matrix = self.update_matrix()

            for rows in range(self.view[self.view_condition][0]):
                for cols in range(self.view[self.view_condition][1]):
                    self.fig.update_traces(
                        patch=go.Scatter(
                            x=[i for i in range(1000)],
                            y=self.ecg_matrix[self.view_settings[self.view_condition][rows][cols]],
                            name=f"{self.view_settings[self.view_condition][rows][cols]}",
                        ),
                        row=rows + 1, col=cols + 1,
                    )

            if not clickData:
                raise dash.exceptions.PreventUpdate

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

            temp_row, temp_col = self.get_graph_component_coord()
            print(self.last_marked_lead, temp_row, temp_col)
            temp_row = self.lead_names.index(self.lead_names[self.last_marked_lead])

            self.fig.update_traces(
                go.Scatter(
                    mode='markers',
                    x=[self.last_marked_lead_xy["x"]],
                    y=[self.last_marked_lead_xy["y"]],
                    marker=dict(
                        color='LightSkyBlue',
                        size=20,
                        line=dict(
                            color='MediumPurple',
                            width=2
                        )
                    ),
                    showlegend=False
                ),
                row=temp_row + 1, col=temp_col + 1
            )

            return self.fig

    def get_graph_component_coord(self):
        for number, component in enumerate(self.view_settings[0]):
            if any(num == self.last_marked_lead for num in component):
                return number, component.index(self.last_marked_lead)

    def update_matrix(self):
        return fns.get_clean_matrix(
            np.array([self.data[self.sample_number][:, i] for i in range(12)]), self.sampling_rate
        )

    def make_plots(self):
        if not self.view_condition:
            for rows in range(self.view[self.view_condition][0]):
                for cols in range(self.view[self.view_condition][1]):
                    self.fig.add_trace(
                        go.Scatter(
                            x=[i for i in range(1000)],
                            y=self.ecg_matrix[self.view_settings[self.view_condition][rows][cols]],
                            name=f"{self.view_settings[self.view_condition][rows][cols]}",
                            fillcolor="gray"
                        ),
                        row=rows + 1, col=cols + 1
                    )

        self.fig.update_layout(xaxis1=dict(range=self.range))
        self.fig.update_layout(xaxis2=dict(range=self.range))
        self.fig.update_layout(xaxis3=dict(range=self.range))
        self.fig.update_layout(xaxis4=dict(range=self.range))
        self.fig.update_layout(xaxis5=dict(range=self.range))
        self.fig.update_layout(xaxis6=dict(range=self.range))
        self.fig.update_layout(xaxis7=dict(range=self.range))
        self.fig.update_layout(xaxis8=dict(range=self.range))
        self.fig.update_layout(xaxis9=dict(range=self.range))
        self.fig.update_layout(xaxis10=dict(range=self.range))
        self.fig.update_layout(xaxis11=dict(range=self.range))
        self.fig.update_layout(xaxis12=dict(range=self.range))

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

    ecg.app.run_server(debug=True, use_reloader=False)
