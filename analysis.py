from data import DataECG
from functions import *

lead_1 = DataECG(0).get_data["I"]
lead_2 = None
lead_3 = None

a_vr = None
a_vl = None
a_vf = None

v1 = None
v2 = None
v3 = None
v4 = None
v5 = None
v6 = None

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

# Get QRS complex length and mechanic systole coefficient
qrs_complex = get_intervals(q_peaks, 'qrs', *s_peaks)
mech_sys = get_mech_systole(qt_interval, heart_cycle, "women")
