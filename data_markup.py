import matplotlib.pyplot as plt
import numpy as np

class DataMarkup:
    def __init__(self, data_path: str, sampling_rate, recording_time,recording_speed):
        self.data = np.load(data_path, pickle=True)
        self.sampling_rate = sampling_rate
        self.recording_time = recording_speed
        self.recording_speed = recording_speed

