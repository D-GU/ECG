import multiprocessing

import numpy as np

from functions import *
from raw_data import get_raw_data

raw_data = get_raw_data("ecg_ptbxl.npy")

QUAN_SAMPLES = 21430

parameters = np.array(
    [
        {"Q": [],
         "R": [],
         "S": [],
         "T": [],
         "P": [],
         "Q_A": [],
         "R_A": [],
         "P_A": [],
         "S_A": [],
         "T_A": [],
         "QT": [],
         "PQ": [],
         "RR": []} for i in range(QUAN_SAMPLES)
    ]
)


def get_params(_st, _end, _leads, _queue):
    for sample in range(_st, _end):
        for leads in range(_leads):
            lead = raw_data[sample][:, leads]

            if np.max(lead) == 0:
                for parameter in parameters[sample].keys():
                    parameters[sample][parameter].append(0)
                continue

            # Get preprocessed data, such as cleaned signal, R-Peaks etc
            signals, info = preprocess(lead)

            # Cleaned ECG signal
            clean_signal = signals["ECG_Clean"]

            # Get R-Peaks
            r_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in info["ECG_R_Peaks"]])

            if r_peaks.size > 5:
                # Find Q-Peaks, S-Peaks, T-Peaks
                _, peaks = get_qst_peaks(lead, r_peaks)

                # Get Q, S, P, T peaks
                q_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in peaks["ECG_Q_Peaks"]])
                s_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in peaks["ECG_S_Peaks"]])
                p_peaks = np.array([peak if isinstance(peak, int) else 0 for peak in peaks["ECG_P_Peaks"]])
                t_peaks = np.array([peak if isinstance(peak, int) else 0 for peak in peaks["ECG_T_Peaks"]])

                # Get Q, R, S, P, T amplitudes
                q_amp = np.array([lead[peak] if isinstance(peak, np.int64) else 0 for peak in q_peaks])
                r_amp = np.array([lead[peak] if isinstance(peak, np.int64) else 0 for peak in r_peaks])
                s_amp = np.array([lead[peak] if isinstance(peak, np.int64) else 0 for peak in s_peaks])
                p_amp = np.array(
                    [lead[peak] if isinstance(peak, np.int64) and peak != 0 else 0 for peak in p_peaks])
                t_amp = np.array(
                    [lead[peak] if isinstance(peak, np.int64) and peak != 0 else 0 for peak in t_peaks])

                # Get main intervals lengths (use mean in future analysis)
                qt_interval = get_intervals(q_peaks, "qt", *t_peaks)
                pq_interval = get_intervals(p_peaks, "pq", *q_peaks)
                rr_interval = get_intervals(r_peaks, 'rr')

                parameters[sample]["Q"].append(get_period(q_peaks))
                parameters[sample]["R"].append(get_period(r_peaks))
                parameters[sample]["S"].append(get_period(s_peaks))
                parameters[sample]["T"].append(get_period(t_peaks))
                parameters[sample]["P"].append(get_period(p_peaks))
                parameters[sample]["Q_A"].append(np.mean(q_amp))
                parameters[sample]["R_A"].append(np.mean(r_amp))
                parameters[sample]["S_A"].append(np.mean(s_amp))
                parameters[sample]["T_A"].append(np.mean(t_amp))
                parameters[sample]["P_A"].append(np.mean(p_amp))
                parameters[sample]["QT"].append(np.mean(qt_interval))
                parameters[sample]["PQ"].append(np.mean(pq_interval))
                parameters[sample]["RR"].append(np.mean(rr_interval))

            else:
                for parameter in parameters[sample].keys():
                    parameters[sample][parameter].append(0)
        print(sample)
        _queue.put(parameters[sample])
    _queue.cancel_join_thread()


def task(_tar):
    q = multiprocessing.JoinableQueue()

    task1 = multiprocessing.Process(target=_tar, args=(0, 4286, 12, q), name="task1")
    task2 = multiprocessing.Process(target=_tar, args=(4286, 8572, 12, q), name="task2")
    task3 = multiprocessing.Process(target=_tar, args=(8572, 12858, 12, q), name="Task3")
    task4 = multiprocessing.Process(target=_tar, args=(12858, 17144, 12, q), name="Task4")
    task5 = multiprocessing.Process(target=_tar, args=(17144, QUAN_SAMPLES, 12, q), name="Task5")

    task1.start()
    task2.start()
    task3.start()
    task4.start()
    task5.start()

    task1.join()
    task2.join()
    task3.join()
    task4.join()
    task5.join()

    while q.empty() is False:
        print(f"Result №{q.get()[0]}")

    # np.save("parameters.npy", parameters)

if __name__ == "__main__":
    task(get_params)
