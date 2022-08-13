import numpy as np

from functions import *
from raw_data import *
import matplotlib.pyplot as plt

data = get_raw_data("ecg_ptbxl.npy")
raw = data[2][:, 11]
print(len(raw))
signals, info = preprocess(raw)

# Cleaned ECG signal
clean_signal = signals["ECG_Clean"]

# Get R-Peaks
r_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in info["ECG_R_Peaks"]])

_, peaks = get_qst_peaks(data, r_peaks, 100)

plt.show()