import numpy as np
import scipy

from config import DEFAULT_SAMPLE_RATE, eeg_bands

def get_band_magnitudes(data, sample_rate=DEFAULT_SAMPLE_RATE, bands=eeg_bands):
    """
    Given an EEG timeseries, compute the magnitude of each band of EEG frequencies.
    """
    """
    eeg_band_fft = {}
    for band in bands.keys():
        eeg_band_fft[band] = bandpower(data, bands[band])
    return eeg_band_fft
    """
    # Get real amplitudes of FFT (only in postive frequencies)
    fft_vals = np.abs(np.fft.rfft(data))

    # Get frequencies for amplitudes in Hz
    fft_freq = np.fft.rfftfreq(len(data), 1.0/sample_rate)

    # Take the mean of the fft amplitude for each EEG band
    eeg_band_fft = dict()
    for band in bands.keys():
        freq_ix = np.where((fft_freq >= bands[band][0]) &
                           (fft_freq <= bands[band][1]))[0]
        eeg_band_fft[band] = np.mean(fft_vals[freq_ix])
    
    return eeg_band_fft
    """
    C = np.fft.fft(data)
    C = abs(C)
    Power = np.zeros(len(bands.keys()))
    print(Power.shape)
    for Band_key, i in zip(bands.keys(), range(len(bands.keys()))):
        Freq = float(bands[Band_key][0])
        Next_Freq = float(bands[Band_key][1])
        Power[i] = sum(
            C[int(np.floor(Freq / sample_rate * len(data))): 
                int(np.floor(Next_Freq / sample_rate * len(data)))]
        )
    Power_Ratio = Power / sum(Power)
    return Power, Power_Ratio
    """

def bandpower(x, band_range, sample_rate=DEFAULT_SAMPLE_RATE):
    f, Pxx = scipy.signal.periodogram(x, fs=sample_rate, detrend=False)
    print(x.shape, f, Pxx)
    ind_min = scipy.argmax(f > band_range[0]) - 1
    ind_max = scipy.argmax(f > band_range[1]) - 1
    print(ind_min, ind_max)
    return scipy.trapz(Pxx[ind_min: ind_max], f[ind_min: ind_max])
    
#### Plot magnitude of each band over time

def band_magnitude_samples(data, frame_size=None, sample_rate=DEFAULT_SAMPLE_RATE):
    """
    Get the magnitude of each frequency band over time, using frames of a given size.
    """
    
    # Default to 2s per frame
    if frame_size == None:
        frame_size = int(sample_rate * 2)
    max_frame = len(data)
    frame_count = int(np.ceil(max_frame / frame_size))

    bands_over_time = {
        'Delta': [],
        'Theta': [],
        'Alpha': [],
        'Beta': [],
        'Gamma': []
    }
    band_keys = list(bands_over_time.keys())

    for frame_i in range(0, frame_count):
        start_frame = frame_i * frame_size
        bands = get_band_magnitudes(data[start_frame:start_frame+frame_size], sample_rate=sample_rate)
        for band_key in band_keys:
            bands_over_time[band_key].append(bands[band_key])

    # Process into numpy arrays
    for band_key in band_keys:
        bands_over_time[band_key] = np.array(bands_over_time[band_key])
        
    return bands_over_time

# Test our band magnitude function
def test_get_band_magnitudes():
    import matplotlib.pyplot as plt
    from scipy.io import wavfile
    samplerate, data = wavfile.read('../data/piano-C5.wav')
    print(data[:, 0].shape, get_band_magnitudes(data, sample_rate=samplerate, bands={'C5': (210, 230), 'A4': (430, 450)}))
    plt.psd(data[:, 0], Fs=samplerate, NFFT=256)
    plt.show()
