import os

import functions
import matplotlib.markers
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from matplotlib.widgets import RadioButtons
from matplotlib.backend_bases import MouseButton


class BaseStructure:
    def __init__(self, database, sampling_rate, recording_speed, seconds):
        self.sample_number = 0


        self.leads_names = []
