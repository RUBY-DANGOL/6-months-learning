# NEU Surface Defect Assignment Results

These results were regenerated from the fixed code in [neu_defect_assignment.py](/C:/Users/rubin/Desktop/AI%20fellow/week9/neu_defect_assignment.py) using the project Conda environment with CUDA enabled on an `NVIDIA GeForce RTX 3050 Laptop GPU`.

## Dataset

- Loader API: `torchvision.datasets.ImageFolder`
- Normalization API: `torchvision.transforms.Normalize`
- Classes: `crazing (Cr)`, `inclusion (In)`, `patches (Pa)`, `pitted_surface (PS)`, `rolled-in_scale (RS)`, `scratches (Sc)`
- Train set: `1440` images total, `240` per class
- Validation split used by the script: `180` images total, `30` per class
- Test split used by the script: `180` images total, `30` per class
- Original image size: `200 x 200`
- Model input size after transforms: `1 x 200 x 200`

## Part 0

### 1. Two-layer network

Implemented explicitly in `TwoLayerNet` with handwritten `__init__` and `forward`, with no `nn.Sequential`.

### 2. ReLU vs Sigmoid over 20 epochs

- Final ReLU training loss: `0.5299`
- Final Sigmoid training loss: `1.1963`

Observation: ReLU converged faster and to a much lower loss. Sigmoid learned more slowly, which matches the usual saturation and smaller-gradient behavior in hidden layers.

### 3. Why `CrossEntropyLoss` over `MSELoss`?

`CrossEntropyLoss` is preferred because this is mutually exclusive 6-class classification. It works directly on logits, gives stronger corrective gradients for wrong confident predictions, and matches the task better than treating labels as regression targets with `MSELoss`.

### 4. Optimizer comparison

- Fastest practical convergence: `Adam`
- `SGD + momentum=0.9` was unstable in this run and diverged badly

Estimated optimizer-related model memory for the 2-layer network:

- `SGD`: `39.07 MB`
- `SGD + momentum`: `58.60 MB`
- `Adam`: `78.14 MB`

### 5. Training stability

Best validation loss over 20 epochs:

- Baseline: `2.2489`
- `BatchNorm1d`: `1.0395`
- `Dropout(0.3)`: `1.4586`

Observation: `BatchNorm1d` helped validation loss the most. It stabilizes hidden activation statistics and usually makes optimization smoother. `Dropout(0.3)` reduced co-adaptation, but in this run it did not help as much as batch normalization.

## Part A

### 1. Loading and dataset checks

- Images per class in train: `240`
- Images per class in validation split: `30`
- Images per class in test split: `30`
- Image dimensions: `200 x 200`

### 2. Why normalization matters

Normalization keeps pixel values on a consistent scale, which improves gradient behavior, reduces sensitivity to raw brightness scale, and usually makes CNN training more stable and faster.

### 3. CNN architecture

Implemented in `DefectCNN`:

- `Conv2d -> ReLU -> MaxPool2d`
- `Conv2d -> ReLU -> MaxPool2d`
- `Flatten -> Linear(6 classes)`

### 4. Training loop

Implemented explicitly with `zero_grad() -> forward() -> CrossEntropyLoss -> backward() -> optimizer.step()` in `run_epoch`.

### 5. Training vs validation curves

- Final training accuracy: `0.9708`
- Final validation accuracy: `0.8500`
- Final training loss: `0.1130`
- Final validation loss: `0.3601`
- Overfitting starts around epoch: `4`

Yes, the baseline CNN overfits. Training accuracy keeps rising while validation performance peaks earlier and becomes less stable after that point.

### 6. Per-class evaluation

Lowest test F1 class:

- `inclusion`, F1 = `0.7778`

Per-class F1:

- Crazing: `0.8966`
- Inclusion: `0.7778`
- Patches: `0.9180`
- Pitted surface: `0.9032`
- Rolled-in scale: `0.9677`
- Scratches: `0.8571`

Misclassified examples were exported to [part_a_crazing_patches_misclassified.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_a_crazing_patches_misclassified.png). The confusion between crazing and patches is plausible because both contain irregular textured grayscale regions with similar local contrast and streak-like surface patterns.

## Part B

### 7. Why augment only the training set?

Validation and test sets should stay unchanged so they measure real generalization on unseen data instead of performance on synthetic transforms.

### 8. Batch normalization after each `Conv2d`

Peak validation accuracy by configuration:

- Baseline: `0.8667`
- `+augmentation`: `0.6944`
- `+augmentation+BN`: `0.5167`
- `+augmentation+BN+dropout`: `0.5000`

Batch normalization normally reduces internal covariate shift and stabilizes feature statistics, but in this run the chosen augmentation recipe appears to have made the task much harder, so BN did not recover the lost performance.

### 9. Dropout before the final linear layer

Dropout randomly masks activations during training so the network cannot over-rely on a small set of features. During inference it is turned off and the full network is used. Here, adding dropout on top of augmentation and BN did not reduce overfitting enough to beat the baseline; it underperformed both the baseline and the augmentation-only model.

### 10. Best configuration on one validation-accuracy graph

Among the three requested plotted configurations:

- Baseline
- `+augmentation`
- `+augmentation+BN+dropout`

The best performer was `baseline`.

### 11. Reflection

If I could keep only one technique for a new manufacturing dataset, I would still choose `data augmentation`, because it directly targets deployment variation in angle, position, and lighting. This run suggests the augmentation policy needs gentler tuning, not that augmentation is useless.

## Part C

### 12. Grid search

| learning_rate | batch_size | best_val_accuracy | final_val_accuracy | test_accuracy |
| --- | --- | --- | --- | --- |
| 0.001 | 16 | 0.8833 | 0.8111 | 0.8556 |
| 0.001 | 32 | 0.9000 | 0.8944 | 0.8722 |
| 0.01 | 16 | 0.1667 | 0.1667 | 0.1667 |
| 0.01 | 32 | 0.1667 | 0.1667 | 0.1667 |

### 13. Best combination and hyperparameter impact

- Best overall combination: `learning_rate = 0.001`, `batch_size = 32`
- Hyperparameter with more impact: `learning rate`

`batch_size = 32` was clearly best in the rerun: it had the highest best validation accuracy, the highest final validation accuracy, and the strongest score among the viable settings. Changing the learning rate from `0.001` to `0.01` collapsed performance, while the batch-size effect was much smaller.

### 14. `StepLR`

- Best unscheduled test accuracy: `0.8444`
- Scheduled test accuracy: `0.8889`

Result: `StepLR` improved final test accuracy in this rerun.

Lowest scheduled-run F1 class:

- `inclusion`, F1 = `0.8148`

### 15. Optuna

Optuna was run successfully for 10 trials.

- Best Optuna params: `lr = 0.015702970884055395`, `batch_size = 42`
- Best Optuna validation accuracy: `0.6889`

Optuna did **not** beat the best grid-search run in this experiment. The grid search reached `0.8944` best validation accuracy, which is substantially higher than the best 10-trial Optuna result.

## Output files

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
