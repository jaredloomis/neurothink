import pylsl as lsl
import sys
import datetime
import numpy as np

class EEGRecorder():
  def __init__(self, source_name, sample_rate):
    self.source_name = source_name
    self.sample_rate = sample_rate

  def connect(self):
    """
    Connect to underlying datasource.
    """
    pass

  def record(self, duration):
    """
    A generator which yields raw EEG samples.

    Yields
    ------
    samples : ndarray
      an array of samples, size ()
    """
    pass

class Muse2EEGRecorder(EEGRecorder):
  def __init__(self):
    super().__init__("Muse 2 EEG Headset", 256)
    self.inlet = None

  def connect(self):
    if self.is_connected():
      return True

    # Find matching streams
    streams = lsl.resolve_byprop('type', 'EEG', timeout=2)

    # Connect to the first one
    if len(streams) == 0:
        print("ERROR: no Muse devices found. Make sure `muselsl stream` is running.", file=sys.stderr)
    else:
        print("Successfully connected to muse device")
        stream = streams[0]

    self.inlet = lsl.StreamInlet(stream, max_chunklen=11)

    # Print some info, update exact sample_rat
    info = self.inlet.info()
    description = info.desc()
    time_correction = self.inlet.time_correction()
    self.sample_rate = int(info.nominal_srate())
    print(description)
    print("Muse 2 Sample rate:", self.sample_rate)
    print("Muse 2 time correction:", time_correction)

    return True

  def stream(self, duration):
    if not self.is_connected():
      print("Muse stream inlet is not defined! Please `connect()` to Muse device.", file=sys.stderr)
      return
    
    start_time = datetime.datetime.now()
    end_time = datetime.datetime.now() + duration

    # Record and display 30s of EEG data
    while datetime.datetime.now() < end_time:
      # Get raw EEG data
      sample_matrix, timestamps = self.inlet.pull_chunk(timeout=1, max_samples=self.sample_rate)
      sample_matrix = np.array(sample_matrix)
      # Get time
      time_delta = (datetime.datetime.now() - start_time).total_seconds()

      # Add time to raw sample
      sample_matrix = np.append(sample_matrix, np.full((sample_matrix.shape[0], 1), time_delta), axis=1)
      # yield sample
      yield sample_matrix

  def is_connected(self):
    return "inlet" in self.__dict__ and self.inlet is not None
