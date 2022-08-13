import multiprocessing

from functions import *
from raw_data import get_raw_data

raw_data = get_raw_data("ecg_ptbxl.npy")

QUAN_SAMPLES = raw_data.shape[0]
SAMPLING_RATE = 100

parameters = np.array(
    [np.array(
        [np.array(
            [np.float64(0) for pars in range(14)]) for ch in range(12)]) for sample in range(QUAN_SAMPLES)])


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
                _, peaks = get_qst_peaks(lead, r_peaks, SAMPLING_RATE)

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

                # Get main intervals lengths (use median in future analysis)
                qt_interval = get_intervals(q_peaks, "qt", *t_peaks)
                pq_interval = get_intervals(p_peaks, "pq", *q_peaks)
                rr_interval = get_intervals(r_peaks, 'rr')
                qrs_interval = get_intervals(q_peaks, s_peaks)

                # Assign values to the positions
                parameters[sample][leads][0] = get_period(q_peaks)
                parameters[sample][leads][1] = get_period(r_peaks)
                parameters[sample][leads][2] = get_period(s_peaks)
                parameters[sample][leads][3] = get_period(t_peaks)
                parameters[sample][leads][4] = get_period(p_peaks)
                parameters[sample][leads][5] = np.median(q_amp)
                parameters[sample][leads][6] = np.median(r_amp)
                parameters[sample][leads][7] = np.median(s_amp)
                parameters[sample][leads][8] = np.median(t_amp)
                parameters[sample][leads][9] = np.median(p_amp)
                parameters[sample][leads][10] = np.median(qt_interval)
                parameters[sample][leads][11] = np.median(pq_interval)
                parameters[sample][leads][12] = np.median(rr_interval)
                parameters[sample][leads][13] = np.median(qrs_interval)

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
    task1 = multiprocessing.Process(target=_tar, args=(0, 308, 12, q), name="task1")
    task2 = multiprocessing.Process(target=_tar, args=(308, 616, 12, q), name="task2")
    task3 = multiprocessing.Process(target=_tar, args=(616, 924, 12, q), name="Task3")
    task4 = multiprocessing.Process(target=_tar, args=(924, 1232, 12, q), name="Task4")
    task5 = multiprocessing.Process(target=_tar, args=(1232, 1540, 12, q), name="Task5")
    task6 = multiprocessing.Process(target=_tar, args=(1540, 1848, 12, q), name="Task6")
    task7 = multiprocessing.Process(target=_tar, args=(1848, QUAN_SAMPLES, 12, q), name="Task7")

    # Start processes
    task1.start()
    task2.start()
    task3.start()
    task4.start()
    task5.start()
    task6.start()
    task7.start()

    # Join processes
    task1.join()
    task2.join()
    task3.join()
    task4.join()
    task5.join()
    task6.join()
    task7.join()

    # Taking objects off of the queue
    while q.empty() is False:
        key, sample = q.get()
        parameters[key] = sample

    np.save("val_par.npy", parameters)


if __name__ == "__main__":
    task(get_params)
