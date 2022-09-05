import multiprocessing
import matplotlib.pyplot as plt
import numpy as np

from functions import *
from raw_data import get_raw_data

raw_data = get_raw_data("train.npy")

QUAN_SAMPLES = raw_data.shape[0]
SAMPLING_RATE = 100

parameters = np.array(
    [np.array(
        [np.array(
            [np.float64(0) for pars in range(15)]) for ch in range(12)]) for sample in range(QUAN_SAMPLES)])


def get_params(_st, _end, _leads, _queue):
    for sample in range(_st, _end):
        for leads in range(_leads):
            lead = raw_data[sample][:, leads]

            if np.max(lead) == 0:
                parameters[sample][leads][::] = 0
                continue

            # Get preprocessed data, such as cleaned signal, R-Peaks etc
            signals, info = preprocess(lead)

            # Cleaned ECG signal
            clean_signal = signals["ECG_Clean"]

            # Get R-Peaks
            r_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in info["ECG_R_Peaks"]])

            if r_peaks.size > 5:
                # Find Q-Peaks, S-Peaks, T-Peaks
                _, peaks = get_qst_peaks(clean_signal, r_peaks, SAMPLING_RATE)

                # Get Q, S, P, T peaks durations
                peaks_dur = get_durations(_signal=clean_signal, _peaks=peaks, _r_peaks=r_peaks)

                q_dur = peaks_dur["Q_Durations"]
                r_dur = peaks_dur["R_Durations"]
                s_dur = peaks_dur["S_Durations"]
                t_dur = peaks_dur["T_Durations"]
                p_dur = peaks_dur["P_Durations"]

                # Get Q, R, S, P, T amplitudes
                q_amp = np.array([lead[peak] if isinstance(peak, np.int64) else 0 for peak in peaks["ECG_Q_Peaks"]])
                r_amp = np.array([lead[peak] if isinstance(peak, np.int64) else 0 for peak in info["ECG_R_Peaks"]])
                s_amp = np.array([lead[peak] if isinstance(peak, np.int64) else 0 for peak in peaks["ECG_S_Peaks"]])
                p_amp = np.array(
                    [lead[peak] if isinstance(peak, int) and peak != 0 else 0 for peak in peaks["ECG_P_Peaks"]])
                t_amp = np.array(
                    [lead[peak] if isinstance(peak, int) and peak != 0 else 0 for peak in peaks["ECG_T_Peaks"]])

                # Get main intervals lengths (use median in future analysis)

                qt_interval = get_intervals(peaks_dur["Q_Onsets"], "qt", *peaks["ECG_T_Onsets"])
                pq_interval = get_intervals(peaks["ECG_P_Onsets"], "pq", *peaks_dur["Q_Onsets"])
                rr_interval = get_intervals(peaks["ECG_R_Onsets"], 'rr')
                pr_interval = get_intervals(peaks["ECG_P_Onsets"], "pr", *peaks["ECG_R_Onsets"])
                qrs_complex = get_intervals(peaks_dur["Q_Onsets"], "qrs", *peaks["ECG_S_Peaks"])

                # Assign values to the positions
                parameters[sample][leads][0] = np.array(np.median(q_dur), get_std_deviation(q_dur))
                parameters[sample][leads][1] = np.array(np.median(r_dur), get_std_deviation(r_dur))
                parameters[sample][leads][2] = np.array(np.median(s_dur), get_std_deviation(s_dur))
                parameters[sample][leads][3] = np.array(np.median(t_dur), get_std_deviation(t_dur))
                parameters[sample][leads][4] = np.array(np.median(p_dur), get_std_deviation(p_dur))
                parameters[sample][leads][5] = np.array(np.median(q_amp), get_std_deviation(q_amp))
                parameters[sample][leads][6] = np.array(np.median(r_amp), get_std_deviation(r_amp))
                parameters[sample][leads][7] = np.array(np.median(s_amp), get_std_deviation(s_amp))
                parameters[sample][leads][8] = np.array(np.median(t_amp), get_std_deviation(t_amp))
                parameters[sample][leads][9] = np.array(np.median(p_amp), get_std_deviation(p_amp))
                parameters[sample][leads][10] = np.array(np.median(qt_interval) / SAMPLING_RATE,
                                                         get_std_deviation(qt_interval))
                parameters[sample][leads][11] = np.array(np.median(pq_interval) / SAMPLING_RATE,
                                                         get_std_deviation(pq_interval))
                parameters[sample][leads][12] = np.array(np.median(rr_interval) / SAMPLING_RATE,
                                                         get_std_deviation(rr_interval))
                parameters[sample][leads][13] = np.array(np.median(pr_interval) / SAMPLING_RATE,
                                                         get_std_deviation(pr_interval))
                parameters[sample][leads][14] = np.array(np.median(qrs_complex) / SAMPLING_RATE,
                                                         get_std_deviation(qrs_complex))
            else:
                parameters[sample][leads][::] = 0

        print(sample)

        # Put sample parameters in queue
        _queue.put((sample, parameters[sample]))


def task(_tar):
    # Init manager and queue
    manager = multiprocessing.Manager()
    q = manager.Queue()

    # Init processes
    task1 = multiprocessing.Process(target=_tar, args=(0, 2444, 12, q), name="task1")
    task2 = multiprocessing.Process(target=_tar, args=(2444, 4888, 12, q), name="task2")
    task3 = multiprocessing.Process(target=_tar, args=(4888, 7332, 12, q), name="Task3")
    task4 = multiprocessing.Process(target=_tar, args=(7332, 9776, 12, q), name="Task4")
    task5 = multiprocessing.Process(target=_tar, args=(9776, 12220, 12, q), name="Task5")
    task6 = multiprocessing.Process(target=_tar, args=(12220, 14664, 12, q), name="Task6")
    task7 = multiprocessing.Process(target=_tar, args=(14664, 17108, 12, q), name="Task7")
    task8 = multiprocessing.Process(target=_tar, args=(17108, QUAN_SAMPLES, 12, q), name="Task8")

    # Start processes
    task1.start()
    task2.start()
    task3.start()
    task4.start()
    task5.start()
    task6.start()
    task7.start()
    task8.start()

    # Join processes
    task1.join()
    task2.join()
    task3.join()
    task4.join()
    task5.join()
    task6.join()
    task7.join()
    task8.join()

    # Taking objects off of the queue
    while q.empty() is False:
        key, sample = q.get()
        parameters[key] = sample

    np.save("train_par.npy", parameters)


if __name__ == "__main__":
    task(get_params)
