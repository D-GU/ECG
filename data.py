import pandas as pd
from numpy import load


# Reading data from file
def get_raw_data(_path: str):
    return load(_path)


# Get raw data
ecg_raw_data = get_raw_data("ecg_ptbxl.npy")


class DataECG:
    def __init__(self, pack):
        self.pack = pack

        self.lead_1 = ecg_raw_data[pack][:, 0]
        self.lead_2 = ecg_raw_data[pack][:, 1]
        self.lead_3 = ecg_raw_data[pack][:, 2]

        self.a_vr = ecg_raw_data[pack][:, 3]
        self.a_vl = ecg_raw_data[pack][:, 4]
        self.a_vf = ecg_raw_data[pack][:, 5]

        self.v1 = ecg_raw_data[pack][:, 6]
        self.v2 = ecg_raw_data[pack][:, 7]
        self.v3 = ecg_raw_data[pack][:, 8]
        self.v4 = ecg_raw_data[pack][:, 9]
        self.v5 = ecg_raw_data[pack][:, 10]
        self.v6 = ecg_raw_data[pack][:, 11]

        self.df = pd.DataFrame(
            {
                "I": self.lead_1,
                "II": self.lead_2,
                "III": self.lead_3,
                "aVR": self.a_vr,
                "aVL": self.a_vl,
                "aVF": self.a_vf,
                "V1": self.v1,
                "V2": self.v2,
                "V3": self.v3,
                "V4": self.v4,
                "V5": self.v5,
                "V6": self.v6
            }
        )

    @property
    def get_data(self):
        return self.df
