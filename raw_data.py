from numpy import load


# Reading data from file
def get_raw_data(_path: str):
    return load(_path, allow_pickle=True)
