import torch 
import torch.nn as nn
import numpy as np 
import pandas as pd
import librosa 
import os 
from metrics import *
import json
import scipy

# load dataframe 
csv_path = "./metadata/arni_subset_metadata.csv"
out_csv_path = "./arni_nclosed_losses.csv"

df = pd.read_csv(csv_path)
df_out = pd.DataFrame()

# create a dictionary with the subsets by num-closed 
dfs = {} 
div = [[i, i+4] for i in range(0, 51, 5)]
div[-1][1] = 55 # fix the last division

# option to analize RIRs from the same microphone position
same_mic = False
if same_mic:
    mic_id = 3
    out_csv_path = f"./metadata/arni_nclosed_mic{mic_id}_losses.csv"

# sample subset of RIRs
n_samples = 5 # for each mic
for i_div in div:
    if same_mic:
        dfs[i_div[0]] = df[df['num-closed'].between(i_div[0], i_div[1]) & (df['mic'] == mic_id)].sample(n=n_samples)
    else:
        dfs[i_div[0]] = df[df['num-closed'].between(i_div[0], i_div[1])].groupby('mic').apply(lambda x: x.sample(n=n_samples))
    
fs = 44100  # sampling frequency

# Read the mixing times from the metadata and extract the maximum median mixing time
mixing_times_path = "./metadata/mixing_time.csv"
mixing_times_df = pd.read_csv(mixing_times_path)
max_median_mixing_time = mixing_times_df.groupby('num-closed')['t_abel'].median().max()
e_ref = np.ceil(max_median_mixing_time*0.001*fs).astype(int)  # time in samples of early reflections
max_len = np.ceil(1.6*fs).astype(int)   # maximum rir length in samples

# initialie lists
rir1_name, rir2_name = [], []
power_loss, mrstft_loss, edc_loss, esr_loss = [], [], [], [] 
edcLoss = EDCLoss(sr=fs, nfft = 35104)

# compute losses 
dfs2 = dfs.copy()
for i_div, dir in enumerate(dfs.items()):
    for j_div, dir2 in enumerate(dfs.items()):
        loss = 0
        for i, row in dir[1].iterrows():
            rir1, _ = librosa.load(row['filename'], sr=fs)
            # remove the onset
            rir1 = rir1[row['onset']+e_ref:]
            # remove the early reflection and truncate it to max_len
            rir1 = rir1[:max_len]
            # normalize total energy 
            rir1 = rir1/np.sqrt(np.sum(rir1**2))
            
            for j, row2 in dir2[1].iterrows():

                rir2, _ = librosa.load(row2['filename'], sr=fs)
                
                # save basenames of the rirs files
                rir1_name.append(os.path.basename(row['filename']).split('.')[0])
                rir2_name.append(os.path.basename(row2['filename']).split('.')[0])
                
                # remove the onset
                rir2 = rir2[row2['onset']+e_ref:] 
                # truncate the RIR to the max_len
                rir2 = rir2[:max_len]
                # normalize total energy 
                rir2 = rir2/np.sqrt(np.sum(rir2**2))

                # compute the loss between the two RIRs
                mrstft_loss.append(MultiResoSTFT(rir1, rir2).item())
                power_loss.append(AveragePower(rir1, rir2).item())
                edc_loss.append(edcLoss(torch.tensor(rir1).unsqueeze(0), torch.tensor(rir2).unsqueeze(0)).item())
                esr_loss.append(ESRLoss(rir1, rir2).item())

# save losses in a dataframe     
df_out['rir1'] = rir1_name
df_out['rir2'] = rir2_name
df_out['power_loss'] = power_loss
df_out['mrstft_loss'] = mrstft_loss
df_out['edc_loss'] = edc_loss
df_out['esr_loss'] = esr_loss

df_out.to_csv(out_csv_path, index=False)

## Create dictionaries for plotting in matlab 

# create a dictionary of len(div) x len(div) dimension
dict_mrstft = {} 
dict_mrstft = {(i, j): [] for i in range(len(div)) for j in range(len(div))}
dict_power = {(i, j): [] for i in range(len(div)) for j in range(len(div))}
dict_edc = {(i, j): [] for i in range(len(div)) for j in range(len(div))}
dict_esr = {(i, j): [] for i in range(len(div)) for j in range(len(div))}

# loop over the rows in df_out
bad_rir = 'IR_numClosed_54_numComb_69_mic_5_sweep_5.wav'
for i, row in df_out.iterrows():
    if row['rir1'] == bad_rir or row['rir2'] == bad_rir:
        continue 
    
    if row['rir1'] == row['rir2']:
        # we don't want to compare the same RIR
        continue

    # get the row in df_arni
    rir1 = df[df['filename'].str.contains(row['rir1'])]
    rir2 = df[df['filename'].str.contains(row['rir2'])]

    # based on num-closed find the indexes to the subgroup in div where the two rirs belong to
    rir1_num_closed = rir1['num-closed'].values[0]
    rir2_num_closed = rir2['num-closed'].values[0]
    rir1_group_index = next((i for i, group in enumerate(div) if rir1_num_closed >= group[0] and rir1_num_closed <= group[1]), None)
    rir2_group_index = next((i for i, group in enumerate(div) if rir2_num_closed >= group[0] and rir2_num_closed <= group[1]), None)
    # add the loss to the corresponding group
    dict_mrstft[(rir1_group_index, rir2_group_index)].append(row['mrstft_loss'])
    dict_power[(rir1_group_index, rir2_group_index)].append(row['power_loss'])
    dict_edc[(rir1_group_index, rir2_group_index)].append(row['edc_loss'])
    dict_esr[(rir1_group_index, rir2_group_index)].append(row['esr_loss'])
   # indx.append((rir1_group_index, rir2_group_index))

max_length = max(len(lst) for lst in dict_mrstft.values())

# Convert dictionaries to NumPy arrays
# suboptimal way to do this 
dict_mrstft_array = 0.0*np.zeros((len(div), len(div),  max(len(lst) for lst in dict_mrstft.values())), dtype=object)
dict_power_array = 0.0*np.zeros((len(div), len(div),  max(len(lst) for lst in dict_power.values())), dtype=object)
dict_edc_array = 0.0*np.zeros((len(div), len(div),  max(len(lst) for lst in dict_edc.values())), dtype=object)
dict_esr_array = 0.0*np.zeros((len(div), len(div),  max(len(lst) for lst in dict_esr.values())), dtype=object)

for i in range(len(div)):
    for j in range(len(div)):
        dict_mrstft_array[i, j, :len(dict_mrstft[(i, j)])] = dict_mrstft[(i, j)]
        dict_power_array[i, j, :len(dict_power[(i, j)])] = dict_power[(i, j)]
        dict_edc_array[i, j, :len(dict_edc[(i, j)])] = dict_edc[(i, j)]
        dict_esr_array[i, j, :len(dict_esr[(i, j)])] = dict_esr[(i, j)]

# Save dicts to mat format
scipy.io.savemat('./data/dict_nclosed_power.mat', {'dict_power':dict_power_array})
scipy.io.savemat('./data/dict_nclosed_mrstft.mat', {'dict_mrstft':dict_mrstft_array})
scipy.io.savemat('./data/dict_nclosed_edc.mat', {'dict_edc':dict_edc_array})
scipy.io.savemat('./data/dict_nclosed_esr.mat', {'dict_esr':dict_esr_array})

# Convert keys of dictionaries to strings
dict_power = {str(key): value for key, value in dict_power.items()}
dict_mrstft = {str(key): value for key, value in dict_mrstft.items()}
dict_edc = {str(key): value for key, value in dict_edc.items()}
dict_esr = {str(key): value for key, value in dict_esr.items()}

json.dump(dict_power, open('./data/json/dict_nclosed_power.json', 'w+'))
json.dump(dict_mrstft, open('./data/json/dict_nclosed_mrstft.json', 'w+'))
json.dump(dict_edc, open('./data/json/dict_nclosed_edc.json', 'w+'))
json.dump(dict_esr, open('./data/json/dict_nclosed_esr.json', 'w+'))

