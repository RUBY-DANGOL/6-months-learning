# NEU Surface Defect Assignment Report

## Dataset

- Dataset: NEU Surface Defect Database
- Loader API: `torchvision.datasets.ImageFolder`
- Normalization API: `torchvision.transforms.Normalize`
- Classes: crazing, inclusion, patches, pitted surface, rolled-in scale, scratches
- Local train split: `240` images per class, `1440` total
- Validation split used in code: `30` images per class, `180` total
- Test split used in code: `30` images per class, `180` total
- Image size: `200 x 200`
- Model input size: `1 x 200 x 200`

## Part 0: NN Foundations

### 1. Two-layer neural network

The two-layer network is implemented explicitly in `TwoLayerNet` in [neu_defect_assignment.py](/C:/Users/rubin/Desktop/AI%20fellow/week9/neu_defect_assignment.py), with handwritten `__init__` and `forward`.

### 2. ReLU vs Sigmoid

Use:

- [part0_activation_loss.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part0_activation_loss.png)
- [part0_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part0_results.json)

Write-up:

- Final ReLU training loss:
- Final Sigmoid training loss:
- Observation after 20 epochs:

### 3. Why `CrossEntropyLoss` instead of `MSELoss`?

`CrossEntropyLoss` is preferred because:

### 4. Optimizer comparison

Use:

- [part0_optimizer_loss.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part0_optimizer_loss.png)
- [part0_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part0_results.json)

Write-up:

- Fastest converging optimizer:
- Estimated optimizer memory:

### 5. BatchNorm1d or Dropout(0.3)

Use:

- [part0_stability_val_loss.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part0_stability_val_loss.png)
- [part0_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part0_results.json)

Write-up:

- Effect on validation loss:
- Explanation:

## Part A: Defect Type Classifier

### 1. Loading with `ImageFolder` and `DataLoader`

Use [part_a_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_a_results.json).

- Images per class:
- Image dimensions:

### 2. Why normalization matters

Normalization is important because:

### 3. CNN architecture

The CNN is implemented in `DefectCNN` in [neu_defect_assignment.py](/C:/Users/rubin/Desktop/AI%20fellow/week9/neu_defect_assignment.py).

### 4. Full training loop

The training loop is implemented explicitly in:

- `run_epoch`
- `train_model`

### 5. Training vs validation accuracy and loss

Use:

- [part_a_loss.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_a_loss.png)
- [part_a_accuracy.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_a_accuracy.png)
- [part_a_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_a_results.json)

Write-up:

- Is the model overfitting?
- At what epoch?

### 6. Per-class evaluation

Use:

- [part_a_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_a_results.json)
- [part_a_crazing_patches_misclassified.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_a_crazing_patches_misclassified.png)

Write-up:

- Lowest F1 class:
- Why crazing and patches may be confused:

## Part B: Model Hardening

### 7. Data augmentation on training set only

Why only train:

### 8. Batch normalization after each `Conv2d`

Use:

- [part_b_val_loss.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_b_val_loss.png)
- [part_b_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_b_results.json)

Write-up:

- Effect on loss curves:
- Mechanism:

### 9. Dropout before final `Linear`

Write-up:

- Effect on overfitting:
- Training vs inference behavior:

### 10. Best configuration

Use:

- [part_b_val_accuracy.png](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_b_val_accuracy.png)
- [part_b_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_b_results.json)

Write-up:

- Best-performing configuration:

### 11. Reflection

If I could keep only one technique:

Reason:

## Part C: Hyperparameter Tuning

### 12. Grid search

Use [part_c_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_c_results.json).

### 13. Markdown table

Paste the `markdown_table` field from [part_c_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_c_results.json) here.

### 14. `StepLR`

Use [part_c_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_c_results.json).

Write-up:

- Did `StepLR` improve final test accuracy?

### 15. Optuna

Use [part_c_optuna_results.json](/C:/Users/rubin/Desktop/AI%20fellow/week9/outputs_cuda/part_c_optuna_results.json).

Write-up:

- Did Bayesian optimization find a better combination than grid search?
