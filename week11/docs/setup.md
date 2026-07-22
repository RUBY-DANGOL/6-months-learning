# Setup Notes

## Goal

Provide a reproducible local setup for the Week 11 computer vision assignment with GPU support when CUDA is available.

## Conda Environment

The workspace includes `environment.yml` with:

- `pytorch`
- `torchvision`
- `pytorch-cuda=12.1`
- notebook tooling
- plotting and tabular libraries
- `onnxruntime`
- `timm`
- CLIP installed from GitHub via `pip`

## Create and activate

```powershell
conda env create -f environment.yml
conda activate week11-cv-cuda
jupyter notebook
```

## CUDA verification

Inside Python or the notebook:

```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
```

## Current machine note

At the time of implementation in this workspace:

- `conda` was not installed on PATH
- the accessible PyTorch runtime resolved to CPU-only (`torch.cuda.is_available() == False`)

Because of that, I prepared the Conda environment definition and notebook automation, but could not create a real CUDA-backed local Conda environment from this terminal session.
