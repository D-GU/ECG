import multiprocessing

import numpy as np

from functions import *
from raw_data import get_raw_data

raw_data = get_raw_data("ecg_ptbxl.npy")

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
         "RR": []} for i in range(21430)
    ]
)


def get_params(_samples_st, _samples_end, _leads, _q):
    for samples in range(_samples_st, _samples_end):
        for leads in range(_leads):
            lead = raw_data[samples][:, leads]

            if np.max(lead) == 0:
                for parameter in parameters[samples].keys():
                    parameters[samples][parameter].append(0)

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

                parameters[samples]["Q"].append(get_period(q_peaks))
                parameters[samples]["R"].append(get_period(r_peaks))
                parameters[samples]["S"].append(get_period(s_peaks))
                parameters[samples]["T"].append(get_period(t_peaks))
                parameters[samples]["P"].append(get_period(p_peaks))
                parameters[samples]["Q_A"].append(np.mean(q_amp))
                parameters[samples]["R_A"].append(np.mean(r_amp))
                parameters[samples]["S_A"].append(np.mean(s_amp))
                parameters[samples]["T_A"].append(np.mean(t_amp))
                parameters[samples]["P_A"].append(np.mean(p_amp))
                parameters[samples]["QT"].append(np.mean(qt_interval))
                parameters[samples]["PQ"].append(np.mean(pq_interval))
                parameters[samples]["RR"].append(np.mean(rr_interval))

            else:
                for parameter in parameters[samples].keys():
                    parameters[samples][parameter].append(0)

        print(samples)
        _q.put_nowait(parameters[samples])

    return


x = np.array([])


def task(_tar):
    q = multiprocessing.Queue()
    task1 = multiprocessing.Process(target=_tar, args=(0, 10, 12, q), name="task1")
    task2 = multiprocessing.Process(target=_tar, args=(10, 20, 12, q), name="task2")
    # task3 = multiprocessing.Process(target=get_params, args=(12858, 17144, 12, q), name="Task3")
    # task4 = multiprocessing.Process(target=get_params, args=(17144, 21430, 12, q), name="Task4")

    task1.name = "task1"
    task2.name = "task2"
    # task3.name = "task3"
    # task4.name = "task4"

    task1.start()
    np.append(x, q.get())
    task1.join()

    task2.start()

    task2.join()

    # task3.start()
    # task4.start()

    # task3.join()
    # task4.join()

    while q.empty() is False:
        print(q.get())

    # np.save("parameters.npy", pars)


task(get_params)
