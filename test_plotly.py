# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from time import sleep
# from matplotlib.backend_bases import MouseButton
#
# val1 = np.zeros(100)
# val2 = np.zeros(100)
#
# level1 = 0.2
# level2 = 0.5
#
# fig, ax = plt.subplots()
#
# ax1 = plt.subplot2grid((2, 1), (0, 0))
# lineVal1, = ax1.plot(np.zeros(100))
# ax1.set_ylim(-0.5, 1.5)
#
# ax2 = plt.subplot2grid((2, 1), (1, 0))
# lineVal2, = ax2.plot(np.zeros(100), color="r")
# ax2.set_ylim(-0.5, 1.5)
#
# axvline1 = ax1.axvline(x=0., color="k")
# axvline2 = ax2.axvline(x=0., color="k")
#
#
# def onMouseMove(event):
#     axvline1.set_data([event.xdata, event.xdata], [0, 1])
#     axvline2.set_data([event.xdata, event.xdata], [0, 1])
#
#
# def onMouseClick(event):
#     if event.inaxis == axvline1.axis and event.button is MouseButton.LEFT:
#         print(1)
#
#
# def updateData():
#     global level1, val1
#     global level2, val2
#
#     clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
#
#     level1 = clamp(level1 + (np.random.random() - .5) / 20.0, 0.0, 1.0)
#     level2 = clamp(level2 + (np.random.random() - .5) / 10.0, 0.0, 1.0)
#
#     # values are appended to the respective arrays which keep the last 100 readings
#     val1 = np.append(val1, level1)[-100:]
#     val2 = np.append(val2, level2)[-100:]
#
#     yield 1  # FuncAnimation expects an iterator
#
#
# def visualize(i):
#     lineVal1.set_ydata(val1)
#     lineVal2.set_ydata(val2)
#
#     return lineVal1, lineVal2
#
#
# fig.canvas.mpl_connect('motion_notify_event', onMouseMove)
# fig.canvas.mpl_connect("button_press_event", onMouseClick)
# ani = animation.FuncAnimation(fig, visualize, updateData, interval=50)
# plt.show()


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
import panel as pn

from dash.dependencies import Input, Output
from dash import dcc
from dash import html, ClientsideFunction
from plotly.subplots import make_subplots

# trace1 = go.Scatter(
#     x=[0, 1, 2],
#     y=[10, 11, 12]
# )
# trace2 = go.Scatter(
#     x=[2, 3, 4],
#     y=[100, 110, 120],
#     yaxis="y2"
# )
# trace3 = go.Scatter(
#     x=[3, 4, 5],
#     y=[1000, 1100, 1200],
#     yaxis="y3"
# )
# data = [trace1, trace2, trace3]
# layout = go.Layout(
#     yaxis=dict(
#         domain=[0, 0.33]
#     ),
#     legend=dict(
#         traceorder="reversed"
#     ),
#     yaxis2=dict(
#         domain=[0.33, 0.66]
#     ),
#     yaxis3=dict(
#         domain=[0.66, 1]
#     )
# )
#
# #fig = go.Figure(data=data, layout=layout)

view_condition = 0
sample_number = 0

view = {
    0: (6, 2),
    1: (12, 1)
}

view_settings = {
    0: ((0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)),
    1: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
}

trace = []
data = np.load("ecg_ptbxl.npy", allow_pickle=True)
ecg_matrix = fns.get_clean_matrix(np.array([data[0][:, i] for i in range(12)]), 100)

for rows in range(view[view_condition][0]):
    for cols in range(view[view_condition][1]):
        trace.append(
            go.Scatter(
                x=[i for i in range(1000)],
                y=ecg_matrix[view_settings[view_condition][rows][cols]],
                name=f"{view_settings[view_condition][rows][cols]}",
                fillcolor="gray",
                xaxis="x" + str(rows + 1),
                yaxis="y" + str(cols + 1)
            )
        )

layout = go.Layout(
    xaxis=dict(
        domain=[0, 0.45]
    ),
    yaxis=dict(
        domain=[0, 0.45]
    ),
    xaxis2=dict(
        domain=[0.45, 0.65]
    ),
    yaxis2=dict(
        domain=[0.65, 0.75],
        anchor="y4"
    ),
    xaxis3=dict(
        domain=[0.75, 0.85]
    ),
    yaxis3=dict(
        domain=[0.85, 1],
        anchor="x4"
    )
)

fig = go.Figure(data=trace, layout=layout)
fig.show()
