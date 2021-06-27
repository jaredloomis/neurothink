import numpy as np
import pandas as pd
import scipy.signal as ss
import seaborn as sns
import matplotlib.pyplot as plt
from config import DEFAULT_SAMPLE_RATE, muse2_sensors

def preprocess_eeg_channel(data, sample_rate=DEFAULT_SAMPLE_RATE):
    """
    Apply noise-reducing transformations to EEG data.
    - Remove 60 Hz noise
    - Detrend
    """
    # Remove 60 Hz noise
    b, a = ss.iirnotch(60.0, 200.0, sample_rate)
    data_ret = ss.filtfilt(b, a, data)
    # Detrend
    data_ret = ss.detrend(data_ret)
    return data_ret

def preprocess_eeg(data):
    """
    TODO: copy input df?
    Apply transformations in-place to clean multi-channel EEG data.
    - All single-chanel transformations (see preprocess_eeg_channel)
    - For each sensor X, create column Xz, containing `X-mean(x)/std(x)`
    """
    for sensor_key in muse2_sensors:
        data[sensor_key] = preprocess_eeg_channel(data[sensor_key])
        sensor_z = (data[sensor_key]-np.mean(data[sensor_key]))/np.std(data[sensor_key])
        data[sensor_key + "z"] = sensor_z
    
    return data

def preprocess_eeg_label_holes(data, labels):
    """
    Find any regions of invalid/noisy data, and assign the corresponding indices in "labels" to nan.
    """
    # TODO
    for sensor_key in muse2_sensors:
        data[sensor_key] = preprocess_eeg_channel(data[sensor_key])
        sensor_z = (data[sensor_key]-np.mean(data[sensor_key]))/np.std(data[sensor_key])
        data[sensor_key + "z"] = sensor_z