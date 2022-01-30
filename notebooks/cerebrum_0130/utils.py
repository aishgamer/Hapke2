import numpy as np
import math

def calc_key(row):
    return hash(str(row.i)+'-'+str(row.e)+'-'+str(row.g))

def add_hash(df, colname):
    df[colname] = df.apply(lambda r: calc_key(r),axis=1)
    return df

def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx
