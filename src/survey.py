from concurrent.futures import ThreadPoolExecutor
import os
import json # TODO: json survey index file?
import pathlib
import datetime
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import eeg_bands, band_colors
from eeg_preprocessing import preprocess_eeg_channel
from power_spectrum import get_band_magnitudes

DEFAULT_SURVEYS_DIR = "../data/muse2-recordings/surveys"

class Survey():
    def __init__(self, recorder, title, description, schedule, surveys_dir=DEFAULT_SURVEYS_DIR, next_step_audio=True):
        self.recorder = recorder
        self.title = title
        self.description = description
        self.schedule = schedule
        self.surveys_dir = surveys_dir
        self.next_step_audio = next_step_audio
        self.handler_thread = ThreadPoolExecutor(max_workers=1)
        if next_step_audio:
            self.audio_player_thread = ThreadPoolExecutor(max_workers=2)

    def record(self, subject):
        # Create survey dir
        timestamp = str(datetime.datetime.now())
        survey_name = self.title + " " + subject + " " + timestamp
        survey_dir = self.surveys_dir + "/" + survey_name
        pathlib.Path(survey_dir).mkdir(parents=True)
        
        # Iterate over each step in the schedule, record and save
        for step, step_i in zip(self.schedule, range(len(self.schedule))):
            if len(step) == 4:
                duration, tag, description, record = step
                handler = lambda: None
            elif len(step) == 5:
                duration, tag, description, record, handler = step
            else:
                raise Exception(f"Invalid schedule step: {step}")

            step_tag = str(step_i) + "_" + tag

            # Play audio to signal next step
            if self.next_step_audio:
                self._play_next_step_audio(description)

            # Execute custom handler function
            self.handler_thread.submit(handler)
                
            # Record stream or wait for specified duration
            if record:
                files = self._save_raw_recording(duration, survey_dir, tag=step_tag)
            else:
                time.sleep(duration.total_seconds())
        
        # Play audio to signal end of survey
        if self.next_step_audio:
            self._play_next_step_audio("Survey Completed. Thank you.")
        
        # Create README file
        readme_file = survey_dir + "/README.md"
        readme_text = "#" + survey_name + "\n\n" + self.description + "\n\n" +\
                      "Subject: " + subject + "\n\n" +\
                      "## Schedule\n\n" + str(self.schedule) + "\n\n"
        with open(readme_file, "w") as readme:
            readme.write(readme_text)
            
        return survey_dir

    ''' TODO historical support
    def list_all_surveys(self):
        """
        List all existing surveys in the survey dir.
        """
        pass

    def load_survey(self, name):
        """
        Load a previous survey by name.
        """
        pass
    '''

    def _save_raw_recording(self, duration, output_path, tag, plot=True):
        # Setup plot
        if plot:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            plt.ion()
            fig.show()
            fig.canvas.draw()

        # x8????? Seems to work...
        total_samples = int(self.recorder.sample_rate * duration.total_seconds() * 8)
        start_time = datetime.datetime.now()
        recorded_samples_ = np.full((total_samples, 6), np.nan)
        #recorded_samples = []
        ######### TODO USE, REMOVE OLD VARS
        recorded_bands_ = pd.DataFrame(columns=eeg_bands.keys())
        recorded_bands = {}

        # Connect recorder
        self.recorder.connect()

        sample_count = 0
        band_sample_count = 0
        for samples in self.recorder.stream(duration):
            new_sample_count = min(sample_count + samples.shape[0], total_samples)
            if new_sample_count != sample_count:
                recorded_samples_[sample_count:new_sample_count, :] = samples
            #recorded_samples.append(samples)
            sample_count = new_sample_count
            sensor_1_samples = samples[:, 0] ### TODO
            # Process into bands
            bands = get_band_magnitudes(preprocess_eeg_channel(sensor_1_samples))
            band_keys = bands.keys()
            # Add time to bands sample
            recorded_bands["time_since_start"] = samples[0, 5]
            # Add bands to band lists
            for band_key in band_keys:
                band = bands[band_key]
                recorded_bands_.loc[band_sample_count, band_key] = band
                if band_key in recorded_bands:
                    recorded_bands[band_key].append(band)
                else:
                    recorded_bands[band_key] = [band]
            
            band_sample_count = band_sample_count + 1

            # Update plot
            if plot:
                ax.clear()
                for band_key in band_keys:
                    band = recorded_bands[band_key]
                    plt.plot(band, color=band_colors[band_key], label=band_key)
                plt.legend()
                fig.canvas.draw()
        
        timestamp = str(start_time)
        # Save the EEG data
        # Remove nan rows
        recorded_samples_ = recorded_samples_[~np.isnan(recorded_samples_).any(axis=1)]
        # TODO use the actual signal names
        eeg = pd.DataFrame(recorded_samples_, columns=['eeg1','eeg2','eeg3','eeg4','aux','time_since_start'])
        eeg_file = output_path + "/" + tag + "-eeg_raw.csv"
        eeg.to_csv(eeg_file)

        """
        # Save the band magnitudes
        band_magnitudes = pd.DataFrame(recorded_bands)
        bands_file = output_path + "/" + tag + "-eeg_band_magnitudes.csv"
        # TODO columns
        band_magnitudes.to_csv(bands_file)
        """
        bands_file = output_path + "/" + tag + "-eeg_band_magnitudes.csv"
        recorded_bands_.to_csv(bands_file)

        return eeg_file, bands_file


    def _play_next_step_audio(self, description):
        def exec_cmd(cmd):
            self.audio_player_thread.submit(lambda: os.system(cmd))

        print("Next step -- " + description)
        exec_cmd("mpg123 ../data/Meditation-bell-sound.mp3")
        exec_cmd("bash -c 'mimic \"" + description + "\" -o EEG-Muse_tmp.wav && cvlc EEG-Muse_tmp.wav --play-and-exit && rm EEG-Muse_tmp.wav'")
