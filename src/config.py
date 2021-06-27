# Sample rate of Muse 2
DEFAULT_SAMPLE_RATE = 256

muse2_sensors = ["AF7", "AF8", "TP9", "TP10"]

# Define EEG bands
eeg_bands = {'Delta': (0, 4),
             'Theta': (4, 8),
             'Alpha': (8, 12),
             'Beta': (12, 30),
             'Gamma': (30, 50)}
# Colors to use when plotting
band_colors = {
    'Delta': 'tab:blue',
    'Theta': 'tab:orange',
    'Alpha': 'tab:gray',
    'Beta': 'tab:green',
    'Gamma': 'tab:brown'
}