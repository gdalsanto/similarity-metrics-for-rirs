import torch 
import torch.nn.functional as F
import torch.nn as nn
import scipy.signal as signal
import numpy as np 
import auraloss
from utils.utils import window2d
from utils.filterbank import FilterBank


def MAE_stft(rir1, rir2, n_fft=1024, hop_size=0.25, fs=44100):
        '''compute the mean absolute error between the STFT of two RIRs'''
        f, t, Zxx1 = signal.stft(rir1, fs=fs, nperseg=n_fft, noverlap=int(n_fft*hop_size))
        f, t, Zxx2 = signal.stft(rir2, fs=fs, nperseg=n_fft, noverlap=int(n_fft*hop_size))

        return np.abs(np.abs(Zxx1) - np.abs(Zxx2))/Zxx1.shape[1]

@torch.no_grad()
def MultiResoSTFT(rir1, rir2):
    '''compute the mean absolute error between the Multi Scale Spectra Loss (from auraloss) of two RIRs'''
    rir1 = torch.tensor(rir1).unsqueeze(0).unsqueeze(0) # chanels and batch
    rir2 = torch.tensor(rir2).unsqueeze(0).unsqueeze(0)
    MRstft = auraloss.freq.MultiResolutionSTFTLoss()
    return MRstft(rir1, rir2)

@torch.no_grad()
def ESRLoss(rir1, rir2):
    '''compute the Error to Signal Ration of two RIRs using auraloss'''
    rir1 = torch.tensor(rir1).unsqueeze(0).unsqueeze(0) # chanels and batch
    rir2 = torch.tensor(rir2).unsqueeze(0).unsqueeze(0)
    ESR = auraloss.time.ESRLoss(reduction='mean')
    return ESR(rir1, rir2)

@torch.no_grad()
def AveragePower(rir1,rir2): # x , y // pred, target
    '''compute the Average Power convergence of two RIRs'''
    rir1 = torch.tensor(rir1)
    rir2 = torch.tensor(rir2)      
    # compute the magnitude spectrogram 
    S1 = torch.abs(torch.stft(rir1, n_fft=1024, hop_length=256, return_complex=True))
    S2 = torch.abs(torch.stft(rir2, n_fft=1024, hop_length=256, return_complex=True))
    
    # create 2d window
    win = window2d(torch.hann_window(64, dtype=S1.dtype))
    # convove spectrograms with the window
    S1_win = F.conv2d(S1.unsqueeze(0).unsqueeze(0), win.unsqueeze(0).unsqueeze(0), stride=(4, 4)).squeeze()
    S2_win = F.conv2d(S2.unsqueeze(0).unsqueeze(0), win.unsqueeze(0).unsqueeze(0), stride=(4, 4)).squeeze()
    # compute the normalized difference between the two windowed spectrograms 
    return torch.norm(S2_win - S1_win, p="fro") / torch.norm(S2_win, p="fro") / torch.norm(S1_win, p="fro") 

@torch.no_grad()
class EDCLoss(nn.Module):
    '''compute the Energy Decay Convergence of two RIRs'''
    def __init__(self, backend = 'torch',sr = 48000,nfft=None):
        super().__init__()   
        self.sr = sr 
        self.filterbank = FilterBank(fraction=3, 
                                order = 5, 
                                fmin = 60, 
                                fmax = 15000, 
                                sample_rate= self.sr, 
                                backend=backend,
                                nfft=nfft)
        self.mse = nn.MSELoss(reduction='mean')

    def discard_last_n_percent(self, edc, n_percent):
        # Discard last n%
        last_id = int(np.round((1 - n_percent / 100) * edc.shape[-1]))
        out = edc[..., 0:last_id]

        return out
    
    def backward_int(self, x):
        # Backwards integral on last dimension
        x = torch.flip(x, [-1])
        x = (1 / x.shape[-1]) * torch.cumsum(x ** 2, -1)
        return torch.flip(x, [-1])


    def forward(self, y_pred, y_true):
        # Remove filtering artefacts (last 5 permille)
        y_pred = self.discard_last_n_percent(y_pred, 0.5)
        y_true = self.discard_last_n_percent(y_true, 0.5)
        # compute EDCs
        y_pred_edr = self.backward_int(self.filterbank(y_pred))
        y_true_edr = self.backward_int(self.filterbank(y_true))
        y_pred_edr = 10*torch.log10(y_pred_edr + 1e-32)
        y_true_edr = 10*torch.log10(y_true_edr + 1e-32)
        level_pred = y_pred_edr[:,:,0]
        level_true = y_true_edr[:,:,0]
        # compute normalized mean squared error on the EDCs 
        num = self.mse(y_pred_edr - level_pred.unsqueeze(-1), y_true_edr - level_true.unsqueeze(-1))
        den = torch.mean(torch.pow(y_true_edr - level_true.unsqueeze(-1), 2))
        return  num / den
        