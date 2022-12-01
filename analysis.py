# task1 = multiprocessing.Process(target=_tar, args=(0, 308, 12, q), name="task1")
# task2 = multiprocessing.Process(target=_tar, args=(308, 616, 12, q), name="task2")
# task3 = multiprocessing.Process(target=_tar, args=(616, 924, 12, q), name="Task3")
# task4 = multiprocessing.Process(target=_tar, args=(924, 1232, 12, q), name="Task4")
# task5 = multiprocessing.Process(target=_tar, args=(1232, 1540, 12, q), name="Task5")
# task6 = multiprocessing.Process(target=_tar, args=(1540, 1848, 12, q), name="Task6")
# task7 = multiprocessing.Process(target=_tar, args=(1848, QUAN_SAMPLES, 12, q), name="Task7")


import multiprocessing
import processes

from time import time
from functions import *
from raw_data import get_raw_data

raw_data = get_raw_data("_.npy")

QUAN_SAMPLES = raw_data.shape[0]  # Quantity of samples
SAMPLING_RATE = 100

parameters = np.array(
    [np.array(
        [np.array(
            [np.array for pars in range(15)]) for ch in range(12)]) for sample in range(QUAN_SAMPLES)])


def get_params(_st, _end, _leads, _queue):
    for sample in range(_st, _end):
        for leads in range(_leads):
            lead = raw_data[sample][:, leads]

            # if signal is 0-ish than all parameters equals to 0,
            # and we move on to next signal
            if np.max(lead) == 0:
                for parameter in range(15):
                    parameters[sample][leads][parameter] = np.array([0, 0])
                continue

            # Get preprocessed data, such as cleaned signal, R-Peaks etc
            signals, info = preprocess(lead, SAMPLING_RATE)

            # Cleaned ECG signal
            clean_signal = signals["ECG_Clean"]

            # Get R-Peaks
            r_peaks = np.array([peak if isinstance(peak, np.int64) else 0 for peak in info["ECG_R_Peaks"]])

            # if there are less than 5 r peaks positions - analysis undoable
            if r_peaks.size > 5:
                # Find Q-Peaks, S-Peaks, T-Peaks
                _, peaks = get_qst_peaks(clean_signal, r_peaks, SAMPLING_RATE)

                # Get all peaks durations
                peaks_dur = get_durations(_signal=clean_signal, _peaks=peaks, _r_peaks=r_peaks)

                # Get Q, R, S, T, P peaks durations
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

                # Get main intervals lengths (using mean)
                qt_interval = get_intervals(peaks_dur["Q_Onsets"], "qt", *peaks["ECG_T_Onsets"])
                pq_interval = get_intervals(peaks["ECG_P_Onsets"], "pq", *peaks_dur["Q_Onsets"])
                rr_interval = get_intervals(peaks["ECG_R_Onsets"], 'rr')
                pr_interval = get_intervals(peaks["ECG_P_Onsets"], "pr", *peaks["ECG_R_Onsets"])
                qrs_complex = get_intervals(peaks_dur["Q_Onsets"], "qrs", *peaks["ECG_S_Peaks"])

                # Assign values to the positions
                parameters[sample][leads][0] = np.array([np.mean(q_dur) / SAMPLING_RATE, get_std_deviation(q_dur)])
                parameters[sample][leads][1] = np.array([np.mean(r_dur) / SAMPLING_RATE, get_std_deviation(r_dur)])
                parameters[sample][leads][2] = np.array([np.mean(s_dur) / SAMPLING_RATE, get_std_deviation(s_dur)])
                parameters[sample][leads][3] = np.array([np.mean(t_dur) / SAMPLING_RATE, get_std_deviation(t_dur)])
                parameters[sample][leads][4] = np.array([np.mean(p_dur) / SAMPLING_RATE, get_std_deviation(p_dur)])
                parameters[sample][leads][5] = np.array([np.mean(q_amp) / SAMPLING_RATE, get_std_deviation(q_amp)])
                parameters[sample][leads][6] = np.array([np.mean(r_amp) / SAMPLING_RATE, get_std_deviation(r_amp)])
                parameters[sample][leads][7] = np.array([np.mean(s_amp) / SAMPLING_RATE, get_std_deviation(s_amp)])
                parameters[sample][leads][8] = np.array([np.mean(t_amp) / SAMPLING_RATE, get_std_deviation(t_amp)])
                parameters[sample][leads][9] = np.array([np.mean(p_amp) / SAMPLING_RATE, get_std_deviation(p_amp)])
                parameters[sample][leads][10] = np.array(
                    [np.mean(qt_interval) / SAMPLING_RATE, get_std_deviation(qt_interval)])
                parameters[sample][leads][11] = np.array(
                    [np.mean(pq_interval) / SAMPLING_RATE, get_std_deviation(pq_interval)])
                parameters[sample][leads][12] = np.array(
                    [np.mean(rr_interval) / SAMPLING_RATE, get_std_deviation(rr_interval)])
                parameters[sample][leads][13] = np.array(
                    [np.mean(pr_interval) / SAMPLING_RATE, get_std_deviation(pr_interval)])
                parameters[sample][leads][14] = np.array(
                    [np.mean(qrs_complex) / SAMPLING_RATE, get_std_deviation(qrs_complex)])
            else:
                for parameter in range(15):
                    parameters[sample][leads][parameter] = np.array([0, 0])

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

    np.save("val_ecg_parameters.npy", parameters)


if __name__ == "__main__":
    start = time()
    # task(get_params)
    x = processes.ProcessCalculation(tasks=17111, target=get_params)

    x.get_args()
    print("%s seconds" % (time() - start))
