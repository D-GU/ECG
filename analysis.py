import xdrlib

import matplotlib.pyplot as plt
import numpy as np

from functions import *
from raw_data import get_raw_data

raw_data = get_raw_data("ecg_ptbxl.npy")
DATA = np.array([[[dict] for j in range(11)] for i in range(21430)])

for ex in range(2):
    for le in range(11):
        lead = raw_data[0][:, 1]
        # Get preprocessed data, such as cleaned signal, R-Peaks etc
        signals, info = preprocess(lead)

        # Cleaned ECG signal
        clean_signal = signals["ECG_Clean"]

        # Get R-Peaks
        r_peaks = info["ECG_R_Peaks"]

        # Get Q-Peaks, S-Peaks, T-Peaks
        _, all_peaks = get_qst_peaks(lead, r_peaks)

        df = DataFrame(
            {"ECG_Q_Peaks": all_peaks["ECG_Q_Peaks"],
             "ECG_T_Peaks": all_peaks["ECG_T_Peaks"],
             "ECG_S_Peaks": all_peaks["ECG_S_Peaks"],
             "ECG_P_Peaks": all_peaks["ECG_P_Peaks"]}
        )

        # Get heart rate and heart cycle
        heart_rate = signals["ECG_Rate"]
        heart_cycle = get_heart_cycle(heart_rate)

        # Get Q, R, S, P, T peaks
        q_peaks = np.array(all_peaks["ECG_Q_Peaks"])
        r_peaks = np.array(info["ECG_R_Peaks"])
        s_peaks = np.array(all_peaks["ECG_S_Peaks"])
        p_peaks = np.array(all_peaks["ECG_P_Peaks"])
        t_peaks = np.array(all_peaks["ECG_T_Peaks"])

        # Get Q, R, S, P, T amplitudes
        q_amp = np.array([lead[peak] if not isinstance(peak, int) else np.nan for peak in q_peaks])
        r_amp = np.array([lead[peak] if not isinstance(peak, int) else np.nan for peak in r_peaks])
        s_amp = np.array([lead[peak] if not isinstance(peak, int) else np.nan for peak in s_peaks])
        p_amp = np.array([lead[peak] if not isinstance(peak, int) else np.nan for peak in p_peaks])
        t_amp = np.array([lead[peak] if not isinstance(peak, int) else np.nan for peak in t_peaks])

        # Get main intervals lengths (use mean in future analysis)
        qt_interval = get_intervals(q_peaks, "qt", *t_peaks)
        pq_interval = get_intervals(p_peaks, "pq", *q_peaks)
        rr_interval = get_intervals(r_peaks, 'rr')

        # Get QRS complex length and mechanic systole coefficient
        qrs_complex = get_intervals(q_peaks, 'qrs', *s_peaks)

        data = {
            "Q": q_peaks,
            "R": r_peaks,
            "S": s_peaks,
            "T": t_peaks,
            "P": p_peaks,
            "Q_A": q_amp,
            "R_A": r_amp,
            "S_A": s_amp,
            "T_A": t_amp,
            "P_A": p_amp,
            "QT": qt_interval,
            "PQ": pq_interval,
            "RR": rr_interval
        }
        DATA[ex] = data

print(DataFrame(DATA[0][2][0]))
