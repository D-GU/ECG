import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import wfdb

from visual_representation import Visualizer
from typing import Union, List, Tuple

FOLDER = "markedup_ecg_dataset/physionet.org/files/ludb/1.0.1/data"

LEADS = ['avf', 'avl', 'avr', 'i', 'ii', 'iii', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6']
DATA_FOLDER = "./lobachevsky-university-electrocardiography-database-1.0.1/data"
SEGMENT_TO_COLOR = {
    'p': 'red',
    'N': 'blue',
    't': 'green',
}
ECG_SIZE = 41 * 16

pd.set_option('display.max_columns', 12)
data_csv = pd.read_csv("markedup_ecg_dataset/physionet.org/files/ludb/1.0.1/ludb.csv")
signal = np.fromfile("markedup_ecg_dataset/physionet.org/files/ludb/1.0.1/data/1.dat")
dataframe = pd.DataFrame(data_csv)


def get_signal(index: int, as_p_signal: bool = True) -> Union[wfdb.Record, np.ndarray]:
    record = wfdb.rdrecord(FOLDER + "/" + str(index))
    assert type(record) is wfdb.Record

    if as_p_signal:
        assert type(record.p_signal) is np.ndarray
        return record.p_signal

    return record


def get_annotations(index: int, lead, as_sample=True) -> Union[wfdb.Annotation, np.ndarray]:
    annotations = wfdb.rdann(FOLDER + "/" + str(index), extension=lead)
    if as_sample:
        return np.array(annotations.sample)
    return annotations


# get a full EGC with 12 leads
def get_full_ecg(index: int):
    signal = get_signal(index)
    annotations = [
        get_annotations(index, lead) for lead in LEADS
    ]

    return signal, annotations


def get_single_lead_ecg(index, lead) -> Tuple[np.ndarray, np.ndarray]:
    """
    return and ecg signal and its annotations
    both as ndarray
    """
    signal = get_signal(index)
    assert type(signal) is np.ndarray
    signal = signal[:, LEADS.index(lead)]

    samples = get_annotations(index, lead)
    assert type(samples) is np.ndarray

    return signal, samples


def get_annotations_symbols(index, lead):
    ann = get_annotations(index, lead, as_sample=False)
    return ann.symbol


def paired_annotation_sample_and_symbol(index, lead):
    annotations_symbols = get_annotations_symbols(index, lead)
    annotations_sample = get_annotations(index, lead)
    return zip(annotations_sample, annotations_symbols)


def get_single_lead_ecg_with_symbols(index, lead):
    """
    return and ecg signal and its annotations
    both as ndarray
    """
    signal = get_signal(index)
    assert type(signal) is np.ndarray
    signal = signal[:, LEADS.index(lead)]

    data = paired_annotation_sample_and_symbol(index, lead)

    return signal, np.array(list(data))

# plot single lead ecg with annotations
def plot_single_lead_ecg(index, lead):
    signal, samples = get_single_lead_ecg(index, lead)

    fig, ax = plt.subplots(figsize=(28, 3))

    ax.plot(signal)
    ax.scatter(samples, signal[samples], c='r', marker='o')


# now plot every lead with annotations
def plot_signal_with_annotation(index):
    signal, samples = get_full_ecg(index)

    sample = signal[:, LEADS.index("ii")]

    # extract sample from annotations
    wfdb.plot_items(signal, samples)


signals, samples = get_full_ecg(200)
my_sample = signals[:, LEADS.index("ii")]

#sample = Visualizer(sampling_rate=500, seconds=10, recording_speed=25, signal=my_sample)
#sample.visualizer()

annotations = get_annotations(200, "ii")
annotations_symbols = get_annotations_symbols(200, "ii")

#plot_single_lead_ecg(200, "ii")
plt.show()
