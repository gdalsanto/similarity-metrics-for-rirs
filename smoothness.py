import torch 
import numpy as np 
import pandas as pd
import librosa 
from metrics import MultiResoSTFT, AveragePower, EDCLoss, ESRLoss
from utils.utils import rir_onset

test_id = "mic2"
mic_id = 2
sweep_id = 4
num_closed_id = 20

# load dataframe 
csv_path = "./metadata/arni_subset_metadata.csv"
out_csv_path = f"./metadata/smoothness_losses_{test_id}.csv"
# initialize the dataframe
df_full = pd.read_csv("./metadata/arni_metadata.csv")
df = pd.read_csv(csv_path)
df_out = pd.DataFrame()
ref_rir_path = f"/Users/dalsag1/Documents/datasets/arni/rir/IR_Arni_upload_numClosed_16-25/IR_numClosed_20_numComb_1950_mic_{mic_id}_sweep_{sweep_id}.wav"

fs = 44100  # sampling frequency
# Read the mixing times from the metadata and extract the maximum median mixing time
mixing_times_path = "./metadata/mixing_time.csv"
mixing_times_df = pd.read_csv(mixing_times_path)
max_median_mixing_time = mixing_times_df.groupby('num-closed')['t_abel'].median().max()
e_ref = np.ceil(max_median_mixing_time*0.001*fs).astype(int)  # time in samples of early reflections
max_len = np.ceil(1.6*fs).astype(int)

# read the reference RIR
rir1, _ = librosa.load(ref_rir_path, sr=fs)
rir1 = rir1[df[df['filename'] == ref_rir_path]['onset'].item()+e_ref:]
# remove the early reflection and truncate it to max_len
rir1 = rir1[:max_len]
# normalize total energy 
rir1 = rir1/np.sqrt(np.sum(rir1**2))

# initialie lists
rir1_path, rir2_path, num_closed = [], [], []
power_loss, mrstft_loss, edc_loss, esr_loss = [], [], [], [] 
edcLoss = EDCLoss(sr=fs, nfft = 35104)

panels = range(1, 55)
for i_panel in panels:
    # sample 10 RIRs with same mic_id, sweep_id and num_closed = i_panel
    if i_panel == 27 or i_panel == 35:
        dfs = df_full[(df_full['num-closed'] == i_panel) & (df_full['mic'] == mic_id) & (df_full['sweep'] == 5)].sample(n=50)
        # dfs = df_full[(df_full['num-closed'] == i_panel) & (df_full['sweep'] == 5)].sample(n=50)
        onsets = []
        for index, row in dfs.iterrows():
            rir2, _ = librosa.load(row['filename'], sr=fs)
            onset = rir_onset(rir2)
            while onset >= len(rir2)*0.1:
                # remove the row from the subset dataframes
                dfs = dfs.drop(index)
                df_full = df_full.drop(df_full[df_full['filename'] == row['filename']].index)
                # sample new row from full dataframe (because the short one doesn't have the fifth sweep)
                new_row = df_full[(df_full['num-closed'] == i_panel) & (df_full['mic'] == mic_id) & (df_full['sweep'] == 5)].sample(n=1)
                # new_row = df_full[(df_full['num-closed'] == i_panel) & (df_full['sweep'] == 5)].sample(n=1)
                # add row to the subset dataframe
                dfs = pd.concat([dfs, new_row])
                # analyze the onset time of the new rir
                rir2, _ = librosa.load(new_row['filename'].item(), sr=fs)
                onset = rir_onset(rir2)
            onsets.append(onset)
            onset = 0 
        dfs['onset'] = onsets
    else:
        dfs = df[(df['num-closed'] == i_panel) & (df['mic'] == mic_id)].sample(n=50)
        # dfs = df[(df['num-closed'] == i_panel)].sample(n=50)
    for i, row in dfs.iterrows():
        # read the "predicted RIR"
        rir2, _ =librosa.load(row['filename'], sr=fs)
        # remove the onset
        rir2 = rir2[row['onset']+e_ref:] 
        # truncate the RIR to the max_len
        rir2 = rir2[:max_len]
        # normalize total energy 
        rir2 = rir2/np.sqrt(np.sum(rir2**2))
        # compute the loss between the two RIRs
        mrstft_loss.append(MultiResoSTFT(rir2, rir1).item())
        power_loss.append(AveragePower(rir2, rir1).item())
        edc_loss.append(edcLoss(torch.tensor(rir2).unsqueeze(0), torch.tensor(rir1).unsqueeze(0)).item())
        esr_loss.append(ESRLoss(rir2, rir1).item())
        rir1_path.append(ref_rir_path)
        rir2_path.append(row['filename'])
        num_closed.append(row['num-closed'])
       
df_out['rir1'] = rir1_path
df_out['rir2'] = rir2_path
df_out['num-closed'] = num_closed
df_out['power_loss'] = power_loss
df_out['mrstft_loss'] = mrstft_loss
df_out['edc_loss'] = edc_loss
df_out['esr_loss'] = esr_loss

df_out.to_csv(out_csv_path, index=False)
import scipy.io as sio

# Save the lists as a MATLAB .mat file
mat_data = {
    'num_closed': num_closed,
    'power_loss': power_loss,
    'mrstft_loss': mrstft_loss,
    'edc_loss': edc_loss,
    'esr_loss': esr_loss
}

mat_file_path = f"./data/smoothness_{test_id}.mat"
sio.savemat(mat_file_path, mat_data)