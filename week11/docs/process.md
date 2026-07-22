# Implementation Process

## Scope split

- Notebook: model training, transfer learning, GradCAM, detection, segmentation, VAE, CLIP, ONNX export
- Web: simple summary interface in HTML/CSS/JS
- Markdown: setup and process documentation

## Notebook changes

The notebook patcher fills the missing TODOs for:

- convolution output size calculations
- ResNet-50 preprocessing and transfer learning
- 3-epoch classifier training
- GradCAM hooks and heatmap generation
- IoU and NMS from scratch
- Faster R-CNN inference
- DeepLabV3 segmentation
- pixel accuracy and mean IoU
- VAE reparameterisation, ELBO loss, and interpolation
- ViT patch embedding
- CLIP zero-shot similarity scoring
- ONNX export and verification

## Deployment framing

The notebook is set up to compare:

- HSV baseline for the legacy rule-based system
- fine-tuned ResNet-50 for known products
- CLIP for zero-shot handling of unseen products

## Runtime status from this workspace

- Python 3.14 now imports `torch`, `torchvision`, `pandas`, and `matplotlib`
- the installed PyTorch build is CPU-only
- `conda` is still unavailable on PATH

That means the notebook logic is in place, but full training here would run on CPU rather than CUDA and would not match the requested GPU-backed workflow.
