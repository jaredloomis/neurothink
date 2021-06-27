import numpy as np
import matplotlib.pyplot as plt

from config import DEFAULT_SAMPLE_RATE, band_colors
from power_spectrum import band_magnitude_samples

def plot_band_magnitude(data, frame_size=None, sample_rate=DEFAULT_SAMPLE_RATE, start_time=0, end_time=1):
    bands_over_time = band_magnitude_samples(data, frame_size, sample_rate)
    frame_count = len(bands_over_time["Delta"])

    # Plot each band
    for band_key in bands_over_time.keys():
        band = bands_over_time[band_key]
        plt.plot(np.linspace(start_time, end_time, frame_count), band, color=band_colors[band_key], label=band_key)

    plt.legend()
    plt.show()