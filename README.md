# Similarity Metrics for Late Reverberation

Companion repository for the paper 'Similarity Metrics for Late Reverberation' presented at ASILOMAR 2024.  
Pre-print available on [Arxiv](https://arxiv.org/abs/2408.14836) [1]

The objective results presented in this study have been computed on the dataset of impulse responses from variable acoustics room Arni at Aalto Acoustic Labs [2] available on [Zenodo](https://zenodo.org/records/6985104)

This repository contains the code used for 
- Data pre-processing
- Dataset sub-sampling
- Evaluating similarity between RIRs using
  - proposed similarity metrics $`\mathcal{L}_{\textrm{PC}}`$ and $`\mathcal{L}_{\textrm{EDC}}`$ 
  - baselines $`\mathcal{L}_{\textrm{MSS}}`$ [3] and $`\mathcal{L}_{\textrm{ESR}}`$ 
- Plotting
  
## Introduction
Accurate tuning of parametric artificial reverberators (ARs) relies heavily on the choice of cost function, yet common audio similarity metrics do not account for the unique statistical properties of late room reverberation. We introduce two novel similarity metrics specifically designed for this purpose, which outperform existing metrics on a dataset of measured room impulse responses (RIRs). 

## Proposed Similarity Metrics 

### **Averaged power convergence** 
Distance on the time-frequency representation:

$`\mathcal{L}_{\textrm{PC}} = \left\lVert \frac{| H(t, f)|^2 * W  - |\hat{H}(t, f) |^2 * W}{(| H(t, f) |^2 * W) (| \hat{H}(t, f) |^2 * W)} \right\rVert_{\textrm{F}}`$

The squared magnitude short-time Fourier transform of the RIR $`h(t)`$, $`\lvert H(t, f) \rvert^2`$, is smoothed by convolving it with a 2D Hann window $W$, to mitigate short-term fluctuations.
### **Energy decay convergence**
Convergence of the energy level over time and frequency:

$`\mathcal{L}_{\text{EDC}} = \frac{1}{|\mathcal{C}|}\sum_{f_{\textrm{c}} \in \mathcal{C}} \frac{\sum_{t=0}^L \left( \varepsilon_{\textrm{dB}}(t; f_\textrm{c}) - \hat{\varepsilon}_{\textrm{dB}}(t; f_\textrm{c}) \right)^2}{\sum_{t=0}^L \varepsilon_{\textrm{dB}}^2(t; f_\textrm{c})}
`$

The energy decay curve (EDC) at each frequency band $`\textrm{c} \in \mathcal{C}`$, $`\varepsilon_{\textrm{dB}}(t; f_\textrm{c})\,`$, is normalized to 0 dB to avoid emphasizing differences in noise level. 

## Dataset of measured RIRs  
We used a dataset of measured RIRs from a variable acoustics room [2], pre-processed to remove direct and early reflections, and segmented into 11 subsets based on the absorption configuration. For each partition, we randomly selected 25~RIRs, 5~RIRs for each of the 5 receiver positions.

### References

```[1] Dal Santo, G., Prawda, K., Schlecht, S. J., & Välimäki, V. (2024). Similarity Metrics For Late Reverberation. arXiv preprint arXiv:2408.14836.```  
```[2] K. Prawda, S. J. Schlecht, and V. Välimäki, “Calibrating the Sabine and Eyring formulas,” J. Acoust. Soc. Am., 2022```
```[3] R. Yamamoto, E. Song, and J.-M. Kim, “Parallel WaveGAN: A fast waveform generation model based on generative adversarial networks with multi-resolution spectrogram,” in Proc. IEEE ICASSP, 2020.```

