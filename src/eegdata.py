import os
import torch
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from eeg_preprocessing import preprocess_eeg_channel

class EEGSurveyDataset(Dataset):
    """
    Given a survey path, load each eeg_raw.csv file as a datum.
    Labels are represented as numeric values. First encountered label = 0, second = 1, etc.
    """
    def __init__(self, survey_path, max_size, ilabelmap=None, transform=None, target_transform=None):
        self.data_files = [survey_path + "/" + f for f in os.listdir(survey_path) if f.endswith("eeg_raw.csv")]
        self.label_map = {f:self._parse_filename(f)[1] for f in self.data_files}
        self.ilabel_map = ilabelmap if ilabelmap is not None else self._create_ilabel_map()
        self.max_size = max_size
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.data_files)

    def __getitem__(self, idx):
        data_file = self.data_files[idx]
        data = pd.read_csv(data_file)[["eeg1", "eeg2", "eeg3", "eeg4"]].to_numpy()
        data = data[:self.max_size]
        label = self.ilabel_map[self.label_map[data_file]]
        if self.transform:
            data = self.transform(data)
        if self.target_transform:
            label = self.target_transform(label)
        return torch.from_numpy(data.T), label
    
    def _create_ilabel_map(self):
        ilabel_map = {}
        i = 0
        for key in self.label_map.keys():
            if self.label_map[key] not in ilabel_map:
                ilabel_map[self.label_map[key]] = i
                i += 1
        return ilabel_map
    
    def _parse_filename(self, filename):
        filename = filename.split("/")[-1]
        name, extension = filename.split(".", 1)
        num_tag, typ = name.split("-", 1)
        num, tag = num_tag.split("_", 1)
        return num, tag
    
class ChunkedDataset(Dataset):
    """
    Given a dataset that returns ndarrays, split each element into chunks not more than size `chunk_size`.
    """
    def __init__(self, dataset, chunk_size, axis=-1):
        self.axis = axis
        self.dataset = [sample for sample in self._gen(dataset, chunk_size)]
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]
    
    def _gen(self, dataset, chunk_size):
        for data, label in dataset:
            length = data.shape[self.axis]
            if length > chunk_size:
                chunks = np.split(data, chunk_size, axis=self.axis)
                for chunk in chunks:
                    yield chunk, label
            else:
                yield data, label
    
class MultiDataset(Dataset):
    """
    Given a collection of datasets, create a single dataset.
    """
    def __init__(self, datasets):
        self.datasets = datasets

    def __len__(self):
        l = 0
        for ds in self.datasets:
            l += len(ds)
        return l

    def __getitem__(self, idx):
        ds_i, ii = self._index_to_dataset_index(idx)
        return self.datasets[ds_i][ii]
    
    def _index_to_dataset_index(self, idx):
        """
        Given a raw index into this dataset, return (1) the dataset responsible for this sample,
        and (2) the index of the requested datum, within that dataset.
        
        Returns: (dataset_idx, sample_idx)
        """
        ds_start_i = 0
        for ds_i, ds in enumerate(self.datasets, 0):
            ds_end_i = ds_start_i + len(ds)
            if ds_start_i <= idx and idx < ds_end_i:
                return ds_i, idx - ds_start_i
            else:
                ds_start_i += len(ds)
        
        raise Exception("Can't find index in datasets: " + str(idx))
