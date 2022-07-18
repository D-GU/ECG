from pandas import DataFrame
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

        self.df = DataFrame(
            {
                0: self.lead_1,
                1: self.lead_2,
                2: self.lead_3,
                3: self.a_vr,
                4: self.a_vl,
                5: self.a_vf,
                6: self.v1,
                7: self.v2,
                8: self.v3,
                9: self.v4,
                10: self.v5,
                11: self.v6
            }
        )

    @property
    def get_data(self):
        return self.df
