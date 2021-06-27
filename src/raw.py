class RawEEG():
  def __init__(self, df, sample_rate, channels=None):
    """
    Parameters
    ----------
    df : DataFrame
      data with each column corresponding to an EEG signal.
    sample_rate : int
      sample rate of EEG data in Hz.
    columns : list(str)
      list of column names.
    """
    self.eeg = df
    self.sample_rate = sample_rate
    self.channels = channels if channels is not None else list(df.columns)