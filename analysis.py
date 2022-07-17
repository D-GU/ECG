import matplotlib.pyplot as plt
import scipy.fftpack

from functions import *
from raw_data import DataECG
from biosppy.signals.tools import analytic_signal

lead_1 = DataECG(0).get_data["I"]
lead_2 = DataECG(0).get_data["II"]
lead_3 = DataECG(0).get_data["III"]

a_vr = DataECG(0).get_data["aVR"]
a_vl = DataECG(0).get_data["aVL"]
a_vf = DataECG(0).get_data["aVF"]

v1 = DataECG(0).get_data["V1"]
v2 = DataECG(0).get_data["V2"]
v3 = DataECG(0).get_data["V3"]
v4 = DataECG(0).get_data["V4"]
v5 = DataECG(0).get_data["V5"]
v6 = DataECG(0).get_data["V6"]

# Get preprocessed data, such as cleaned signal, R-Peaks etc
signals, info = preprocess(lead_1)

# Cleaned ECG signal
clean_signal = signals["ECG_Clean"]

# Get R-Peaks
r_peaks = info["ECG_R_Peaks"]

# Get Q-Peaks, S-Peaks, T-Peaks
_, all_peaks = get_qst_peaks(lead_1, r_peaks)

df = DataFrame({
    "ECG_Q_Peaks": all_peaks["ECG_Q_Peaks"],
    "ECG_T_Peaks": all_peaks["ECG_T_Peaks"],
    "ECG_S_Peaks": all_peaks["ECG_S_Peaks"],
    "ECG_P_Peaks": all_peaks["ECG_P_Peaks"]}
)

# Get heart rate and heart cycle
heart_rate = signals["ECG_Rate"]
heart_cycle = get_heart_cycle(heart_rate)

# Get Q, R, S, P peaks
q_peaks = np.array([peak / 100 for peak in all_peaks["ECG_Q_Peaks"]])
r_peaks = np.array([peak / 100 for peak in info["ECG_R_Peaks"]])
s_peaks = np.array([peak / 100 for peak in all_peaks["ECG_S_Peaks"]])
p_peaks = np.array([peak / 100 for peak in all_peaks["ECG_P_Peaks"]])

# Get T peaks + T period
t_peaks = np.array([peak / 100 for peak in all_peaks["ECG_T_Peaks"]])
t_peaks += signal_period(t_peaks, sampling_rate=100)

# Get main intervals lengths (use mean in future analysis)
qt_interval = get_intervals(q_peaks, "qt", *t_peaks)
pq_interval = get_intervals(p_peaks, "pq", *q_peaks)
rr_interval = get_intervals(r_peaks, 'rr')
rr_interval.resize(len(r_peaks))

# Get QRS complex length and mechanic systole coefficient
qrs_complex = get_intervals(q_peaks, 'qrs', *s_peaks)
mech_sys = get_mech_systole(qt_interval, heart_cycle, "women")

qt_amp = analytic_signal(qt_interval)['amplitude']

# Angle of QT
angle_qt = [np.arctan(i / j) for i, j in zip(qt_interval, qt_amp)]

delta_r_qt = np.array(
    ['+' if qt_interval[i] > qt_interval[i + 1] else '-' for i in range(len(qt_interval) - 1)]
)

delta_t_qt = np.array(
    ['+' if qt_amp[i] > qt_interval[i + 1] else '-' for i in range(len(qt_interval) - 1)]
)

delta_a_qt = np.array(
    ['+' if angle_qt[i] > angle_qt[i + 1] else '-' for i in range(len(angle_qt) - 1)]
)


def n_gram_sig(_interval: np.array, _amplitude: np.array, _angle: np.array):
    _gram_dict = {
        "+++": "A",
        "--+": "B",
        "+-+": "C",
        "---": "D",
        "++-": "F",
        "-+-": "E"
    }

    _n_string = ""

    for _inter, _ampl, _angl in zip(_interval, _amplitude, _angle):
        _n_string += _gram_dict[_inter + _ampl + _angl]

    return _n_string


p = n_gram_sig(delta_r_qt, delta_t_qt, delta_a_qt)

print(p)
# plt.show()
