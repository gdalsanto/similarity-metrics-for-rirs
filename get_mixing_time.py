import numpy as np
import pandas as pd
import librosa
import scipy 
import matplotlib.pyplot as plt
from utils.utils import compute_echo

csv_path = "./metadata/arni_subset_metadata.csv"
df = pd.read_csv(csv_path)
fs = 44100
t_abels = []
echo_denss = []

for i, row in df.iterrows():
    rir1, _ = librosa.load(row['filename'], sr=fs)
    onset = row['onset']
    t_abel, echo_dens = compute_echo(rir1[onset:], fs, N=1024, preDelay=0)
    t_abels.append(t_abel)
    echo_denss.append(echo_dens)

df['t_abel'] = t_abels
df['echo_dens'] = echo_denss
df.to_csv('./metadata/arni_subset_tmix_metadata.csv', index=False)

df_short = df[['t_abel', 'num-closed']]
df_short.to_csv('./metadata/mixing_time.csv', index=False)
df_mixing_time = df.groupby('num-closed')['t_abel'].agg(['median', 'std']).reset_index()

plt.figure()
plt.scatter(df['num-closed'], df['t_abel'], marker='.', color='blue')
plt.errorbar(df_mixing_time['num-closed'], df_mixing_time['median'], yerr=df_mixing_time['std'], fmt='o', color='red')
plt.xlabel('Number of closed panels')
plt.ylabel('Mixing time (ms)')
plt.ylim([0, 50])
figure_path = "./figures/mixing_time.png"
plt.savefig(figure_path)

# save the mixing time in mat file
scipy.io.savemat('./data/mixing_time.mat', {'t_abel': df['t_abel'].values, 'num_closed': df['num-closed'].values})
