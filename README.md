# neurothink

neurothink is project exploring Muse 2 EEG data, with the goal being to classify wearer's thoughts/actions based on their EEG patterns.

![EEG 10-10 system](./data/EEG-10-10.png)

## Eyes open/closed detection

[notebook](./EEG/Muse-EEG-eyes-open.ipynb)

In this notebook, I train a CNN to determine whether the wearer's eyes are open or closed based on the raw EEG signals. The results were surprising, with up to **82% accuracy** on my dataset.

Possible improvements:

- Use FFT data as additional features (ie. feature per band per sample).
- Experiment with network architectures.

## Basic thought detection

[notebook](./EEG/Muse-EEG-eyes-open.ipynb)

Here, I train a similar CNN to determine whether the wearer is thinking of the concept of `left`, `right`, or neither. **In Progress.**

## Meditation coach

Next, I'll make an attempt at training a network