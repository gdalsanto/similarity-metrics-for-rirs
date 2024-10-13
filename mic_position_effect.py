import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import scipy.io
import json
import os 

csv_loss_path = "./arni_nclosed_losses.csv"
csv_arni_path = "./metadata/arni_subset_metadata.csv"

df_loss = pd.read_csv(csv_loss_path)
df_arni = pd.read_csv(csv_arni_path)


# get number of microphone positions 
n_mics = len(df_arni['mic'].unique())

# create a dictionary with the subsets by num-closed
div = [[i, i+4] for i in range(0, 51, 5)]
div[-1][1] = 55 # fix the last division
rir1_div = [7, 9]
rir2_div = [7, 9]
for val in range(0, div[rir1_div[0]][0]):
    df_loss = df_loss[~(df_loss['rir1'].str.contains(f'numClosed_{val}_')) ]
    continue
for val in range(div[rir1_div[-1]][1]+1, 55):
    df_loss = df_loss[~(df_loss['rir1'].str.contains(f'numClosed_{val}_')) ]
for val in range(0, div[rir2_div[0]][0]):
    df_loss = df_loss[~(df_loss['rir2'].str.contains(f'numClosed_{val}_')) ]
    continue
for val in range(div[rir2_div[-1]][1]+1, 55):
    df_loss = df_loss[~(df_loss['rir2'].str.contains(f'numClosed_{val}_')) ]


# create a dictionary of n_mic x n_mic dimension
dict_mrstft = {} 
dict_mrstft = {(i+1, j+1): [] for i in range(n_mics) for j in range(n_mics)}
dict_power = {(i+1, j+1): [] for i in range(n_mics) for j in range(n_mics)}
dict_edc = {(i+1, j+1): [] for i in range(n_mics) for j in range(n_mics)}
dict_esr = {(i+1, j+1): [] for i in range(n_mics) for j in range(n_mics)}

# loop over the rows in df_loss
for i, row in df_loss.iterrows():    
    if row['rir1'] == row['rir2']:
        # we don't want to compare the same RIR
        continue

#    if any((df_loss['rir1'] == row['rir2']) & (df_loss['rir2']== row['rir1']) & (df_loss.index < i)):
#        # we don't want to compare the same RIRs in different order - the loss will be the same
#        continue

    # get the row in df_arni
    rir1 = df_arni[df_arni['filename'].str.contains(row['rir1'])]
    rir2 = df_arni[df_arni['filename'].str.contains(row['rir2'])]

    # based on micfind the indexes to the subgroup where the two rirs belong to
    rir1_mic = rir1['mic'].values[0]
    rir2_mic = rir2['mic'].values[0]
    # add the loss to the corresponding group
    dict_mrstft[(rir1_mic, rir2_mic)].append(row['mrstft_loss'])
    dict_power[(rir1_mic, rir2_mic)].append(row['power_loss'])
    dict_edc[(rir1_mic, rir2_mic)].append(row['edc_loss'])
    dict_esr[(rir1_mic, rir2_mic)].append(row['esr_loss'])

max_length = max(len(lst) for lst in dict_mrstft.values())

# Convert dictionaries to NumPy arrays
# stupindous way to do this becuase idk it's so fucking hard to move data from python to matlab idk why and pissed about it 
dict_mrstft_array = 0.0*np.zeros((n_mics, n_mics,  max(len(lst) for lst in dict_mrstft.values())), dtype=object)
dict_power_array = 0.0*np.zeros((n_mics, n_mics,  max(len(lst) for lst in dict_power.values())), dtype=object)
dict_edc_array = 0.0*np.zeros((n_mics, n_mics,  max(len(lst) for lst in dict_edc.values())), dtype=object)
dict_esr_array = 0.0*np.zeros((n_mics, n_mics,  max(len(lst) for lst in dict_esr.values())), dtype=object)

for i in range(n_mics):
    for j in range(n_mics):
        dict_mrstft_array[i, j, :len(dict_mrstft[(i+1, j+1)])] = dict_mrstft[(i+1, j+1)]
        dict_power_array[i, j, :len(dict_power[(i+1, j+1)])] = dict_power[(i+1, j+1)]
        dict_edc_array[i, j, :len(dict_edc[(i+1, j+1)])] = dict_edc[(i+1, j+1)]
        dict_esr_array[i, j, :len(dict_esr[(i+1, j+1)])] = dict_esr[(i+1, j+1)]


# Save dicts to mat format
scipy.io.savemat('./data/dict_mic_power.mat', {'dict_power':dict_power_array})
scipy.io.savemat('./data/dict_mic_mrstft.mat', {'dict_mrstft':dict_mrstft_array})
scipy.io.savemat('./data/dict_mic_edc.mat', {'dict_edc':dict_edc_array})
scipy.io.savemat('./data/dict_mic_esr.mat', {'dict_esr':dict_esr_array})

# Convert keys of dictionaries to strings
dict_power = {str(key): value for key, value in dict_power.items()}
dict_mrstft = {str(key): value for key, value in dict_mrstft.items()}
dict_edc = {str(key): value for key, value in dict_edc.items()}
dict_esr = {str(key): value for key, value in dict_esr.items()}

json.dump(dict_power, open('./data/json/dict_mic_power.json', 'w+'))
json.dump(dict_mrstft, open('./data/json/dict_mic_mrstft.json', 'w+'))
json.dump(dict_edc, open('./data/json/dict_mic_edc.json', 'w+'))
json.dump(dict_esr, open('./data/json/dict_mic_esr.json', 'w+'))

