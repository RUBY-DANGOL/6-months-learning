# NEU Surface Defect Assignment

This workspace contains a complete PyTorch solution for the NEU surface defect assignment in [neu_defect_assignment.py](/C:/Users/rubin/Desktop/AI%20fellow/week9/neu_defect_assignment.py), along with regenerated results in [results_summary.md](/C:/Users/rubin/Desktop/AI%20fellow/week9/results_summary.md).

## Dataset

- Classes: `crazing`, `inclusion`, `patches`, `pitted_surface`, `rolled-in_scale`, `scratches`
- Train split: `1440` images total, `240` per class
- Validation folder on disk: `360` images total, `60` per class
- Script behavior: stratified split of the provided validation folder into `180` validation + `180` test images, which gives `30` validation and `30` test images per class
- Original image size: `200 x 200`
- Model input size after transforms: `1 x 200 x 200`

## Environment

The project was run in the local Conda environment:

- Env path: `C:\Users\rubin\Desktop\AI fellow\week9\.conda-env`
- PyTorch build: CUDA-enabled
- Verified GPU: `NVIDIA GeForce RTX 3050 Laptop GPU`

## Install / Setup

If you need to recreate the environment manually, the required packages are listed in [requirements.txt](/C:/Users/rubin/Desktop/AI%20fellow/week9/requirements.txt).

## Run

Run everything:

```powershell
& 'C:\Users\rubin\anaconda3\Scripts\conda.exe' run -p 'C:\Users\rubin\Desktop\AI fellow\week9\.conda-env' python neu_defect_assignment.py --part all --output-dir outputs_cuda --optuna-trials 10
```

Run only one section:

```powershell
& 'C:\Users\rubin\anaconda3\Scripts\conda.exe' run -p 'C:\Users\rubin\Desktop\AI fellow\week9\.conda-env' python neu_defect_assignment.py --part part0 --output-dir outputs_cuda
& 'C:\Users\rubin\anaconda3\Scripts\conda.exe' run -p 'C:\Users\rubin\Desktop\AI fellow\week9\.conda-env' python neu_defect_assignment.py --part parta --output-dir outputs_cuda
& 'C:\Users\rubin\anaconda3\Scripts\conda.exe' run -p 'C:\Users\rubin\Desktop\AI fellow\week9\.conda-env' python neu_defect_assignment.py --part partb --output-dir outputs_cuda
& 'C:\Users\rubin\anaconda3\Scripts\conda.exe' run -p 'C:\Users\rubin\Desktop\AI fellow\week9\.conda-env' python neu_defect_assignment.py --part partc --output-dir outputs_cuda
& 'C:\Users\rubin\anaconda3\Scripts\conda.exe' run -p 'C:\Users\rubin\Desktop\AI fellow\week9\.conda-env' python neu_defect_assignment.py --part optuna --output-dir outputs_cuda --optuna-trials 10
```

## What The Code Covers

- `torchvision.datasets.ImageFolder` dataset loading
- `torchvision.transforms.Normalize` preprocessing
- Explicit `nn.Module` definitions for the 2-layer network and CNN
- ReLU vs Sigmoid comparison
- `CrossEntropyLoss` vs `MSELoss` discussion
- SGD vs SGD with momentum vs Adam comparison
- `BatchNorm1d` and `Dropout(0.3)` stability experiment
- CNN baseline training and evaluation
- Misclassified `crazing` vs `patches` export
- Augmentation, batch norm, and dropout hardening experiments
- Grid search over learning rate and batch size
- `StepLR` learning-rate scheduling
- Optuna Bayesian optimization

## Outputs

Fresh regenerated artifacts are in [outputs_cuda](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda):

- `part0_activation_loss.png`
- `part0_optimizer_loss.png`
- `part0_stability_val_loss.png`
- `part0_results.json`
- `part_a_accuracy.png`
- `part_a_loss.png`
- `part_a_crazing_patches_misclassified.png`
- `part_a_results.json`
- `part_b_val_accuracy.png`
- `part_b_val_loss.png`
- `part_b_results.json`
- `part_c_results.json`
- `part_c_optuna_results.json`
- `defect_cnn_best_steplr.pkl`

## Report Writing

Use [report_template.md](/C:/Users/rubin/Desktop/AI%20fellow/week9/report_template.md) as the cleaned-up report skeleton and [results_summary.md](/C:/Users/rubin/Desktop/AI%20fellow/week9/results_summary.md) as the filled results reference.
