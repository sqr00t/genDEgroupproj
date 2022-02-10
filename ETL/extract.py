import pandas as pd


### Load csv. csv does not have header in first row, set header=None
def data_set():
    df = pd.read_csv('data/chesterfield_25-08-2021_09-00-00.csv', header=None)
    return df 