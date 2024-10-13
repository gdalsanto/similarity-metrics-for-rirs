import pandas as pd
import librosa
from utils import rir_onset
import os

"""
Read the metadata file of the Arni variable acoustics room dataset of measured rirs
and create a new metadata file with only one rir per set of (num-closed, combination, mic)
"""
csv_path = "./metadata/arni_metadata.csv"
csv2_path = "./metadata/arni_subset_metadata.csv"

df = pd.read_csv(csv_path)
fs = 44100
onset = 0
corrupted_rirs = []
onsets = []

df2 = pd.DataFrame()
# get one rir per set of num-closed, combination, mic; thus discard sweeps
for i, filepath in enumerate(pd.unique(df['filename'].str[:-6])):
    # onset detection
    while onset == 0:
        try: 
            # sample one rir from the same set of (num-closed, combination, mic) but discard those that have sweep number == 5
            rir_filepath = df[(df['filename'].str[:-6] == filepath) & (df['sweep'] != 5)].sample(n=1)['filename'].item()
        except ValueError:
            print('exception made for file:', filepath)
            # accept the rir even if it has sweep number == 5
            rir_filepath = df[(df['filename'].str[:-6] == filepath)].sample(n=1)['filename'].item()
        # load the rir and detect the onset
        rir1, _ = librosa.load(rir_filepath, sr=fs)
        onset = rir_onset(rir1)
        if onset >= len(rir1)*0.1:
            # onset is too long, discard the rir as it might be corrupted by noise
            onset = 0
            df = df.drop(df[df['filename'].eq(rir_filepath)].index)
            corrupted_rirs.append(rir_filepath)

    df2 = pd.concat([df2, df[df['filename'].eq(rir_filepath)]])
    onsets.append(onset)
    onset = 0

# save detected onset times in the new metadata file
df2['onset'] = onsets
df2.to_csv(csv2_path, index=False)

# save the corrupted rirs in a separate metadata file
df_bad_rirss = pd.DataFrame()
df_bad_rirss['filename'] = corrupted_rirs
df_bad_rirss.to_csv('./metadata/corrupted_rirs.csv', index=False)
