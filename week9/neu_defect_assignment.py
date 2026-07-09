from __future__ import annotations

import argparse
import copy
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
from PIL import Image
from torch import nn
from torch.optim import Adam, SGD
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import datasets, transforms
from torchvision.transforms import InterpolationMode

try:
    import optuna
except ImportError:
    optuna = None


CLASS_SHORT_NAMES = {
    "rolled-in_scale": "RS",
    "patches": "Pa",
    "crazing": "Cr",
    "pitted_surface": "PS",
    "inclusion": "In",
    "scratches": "Sc",
}


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class DatasetBundle:
    train: Dataset
    val: Dataset
    test: Dataset
    class_names: List[str]
    train_counts: Dict[str, int]
    val_counts: Dict[str, int]
    test_counts: Dict[str, int]
    original_image_dimensions: Tuple[int, int]


class PathImageFolder(datasets.ImageFolder):
    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int, str]:
        image, target = super().__getitem__(index)
        path, _ = self.samples[index]
        return image, target, path


class TransformSubset(Dataset):
    def __init__(self, dataset: PathImageFolder, indices: Sequence[int], transform=None) -> None:
        self.dataset = dataset
        self.indices = list(indices)
        self.transform = transform
        self.classes = dataset.classes
        self.class_to_idx = dataset.class_to_idx
        self.samples = [dataset.samples[idx] for idx in self.indices]

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int, str]:
        dataset_index = self.indices[index]
        path, target = self.dataset.samples[dataset_index]
        image = self.dataset.loader(path)
        if self.transform is not None:
            image = self.transform(image)
        return image, target, path


def make_transforms(augment: bool = False) -> transforms.Compose:
    ops = [transforms.Grayscale(num_output_channels=1)]
    if augment:
        ops.extend(
            [
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(15, interpolation=InterpolationMode.BILINEAR),
                transforms.RandomCrop(180),
                transforms.Resize((200, 200), interpolation=InterpolationMode.BILINEAR),
            ]
        )
    else:
        ops.append(transforms.Resize((200, 200), interpolation=InterpolationMode.BILINEAR))
    ops.extend(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5,), std=(0.5,)),
        ]
    )
    return transforms.Compose(ops)


def class_counts_from_samples(samples: Sequence[Tuple[str, int]], class_names: Sequence[str]) -> Dict[str, int]:
    counts = Counter()
    for _, label in samples:
        counts[class_names[label]] += 1
    return dict(sorted(counts.items()))


def stratified_split_indices(
    samples: Sequence[Tuple[str, int]],
    val_fraction: float = 0.5,
    seed: int = 42,
) -> Tuple[List[int], List[int]]:
    grouped: Dict[int, List[int]] = defaultdict(list)
    for idx, (_, label) in enumerate(samples):
        grouped[label].append(idx)

    rng = random.Random(seed)
    val_indices: List[int] = []
    test_indices: List[int] = []
    for class_indices in grouped.values():
        shuffled = class_indices[:]
        rng.shuffle(shuffled)
        split_idx = int(len(shuffled) * val_fraction)
        val_indices.extend(shuffled[:split_idx])
        test_indices.extend(shuffled[split_idx:])
    return sorted(val_indices), sorted(test_indices)


def image_dimensions_from_folder(folder: Path) -> Tuple[int, int]:
    sample_path = next(folder.rglob("*.jpg"))
    with Image.open(sample_path) as image:
        return image.size


def load_datasets(
    root: str | Path = "dataset/NEU-DET",
    augment_train: bool = False,
    val_fraction_from_validation: float = 0.5,
    seed: int = 42,
) -> DatasetBundle:
    root = Path(root)
    train_dir = root / "train" / "images"
    validation_dir = root / "validation" / "images"

    original_dimensions = image_dimensions_from_folder(train_dir)

    train_full = PathImageFolder(train_dir, transform=make_transforms(augment_train))
    validation_full = PathImageFolder(validation_dir, transform=make_transforms(False))

    val_indices, test_indices = stratified_split_indices(
        validation_full.samples,
        val_fraction=val_fraction_from_validation,
        seed=seed,
    )

    train_ds = train_full
    val_ds = TransformSubset(validation_full, val_indices, transform=make_transforms(False))
    test_ds = TransformSubset(validation_full, test_indices, transform=make_transforms(False))

    return DatasetBundle(
        train=train_ds,
        val=val_ds,
        test=test_ds,
        class_names=train_full.classes,
        train_counts=class_counts_from_samples(train_full.samples, train_full.classes),
        val_counts=class_counts_from_samples(val_ds.samples, train_full.classes),
        test_counts=class_counts_from_samples(test_ds.samples, train_full.classes),
        original_image_dimensions=original_dimensions,
    )


def make_dataloaders(
    bundle: DatasetBundle,
    batch_size: int,
    num_workers: int = 0,
) -> Dict[str, DataLoader]:
    return {
        "train": DataLoader(bundle.train, batch_size=batch_size, shuffle=True, num_workers=num_workers),
        "val": DataLoader(bundle.val, batch_size=batch_size, shuffle=False, num_workers=num_workers),
        "test": DataLoader(bundle.test, batch_size=batch_size, shuffle=False, num_workers=num_workers),
    }


def unpack_batch(batch) -> Tuple[torch.Tensor, torch.Tensor, Optional[Sequence[str]]]:
    if len(batch) == 3:
        inputs, targets, paths = batch
        return inputs, targets, paths
    inputs, targets = batch
    return inputs, targets, None


class TwoLayerNet(nn.Module):
    def __init__(
        self,
        input_dim: int = 200 * 200,
        hidden_dim: int = 128,
        num_classes: int = 6,
        activation: str = "relu",
        stability: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.activation_name = activation
        self.bn = nn.BatchNorm1d(hidden_dim) if stability == "batchnorm" else None
        self.dropout = nn.Dropout(0.3) if stability == "dropout" else None
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        if self.activation_name == "relu":
            x = torch.relu(x)
        elif self.activation_name == "sigmoid":
            x = torch.sigmoid(x)
        else:
            raise ValueError(f"Unsupported activation: {self.activation_name}")
        if self.bn is not None:
            x = self.bn(x)
        if self.dropout is not None:
            x = self.dropout(x)
        return self.fc2(x)


class DefectCNN(nn.Module):
    def __init__(
        self,
        num_classes: int = 6,
        use_batchnorm: bool = False,
        dropout: float = 0.0,
        input_size: Tuple[int, int, int] = (1, 200, 200),
    ) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16) if use_batchnorm else None
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32) if use_batchnorm else None
        self.pool2 = nn.MaxPool2d(2)
        self.flatten = nn.Flatten()
        flat_dim = self._infer_flatten_dim(input_size)
        self.dropout = nn.Dropout(dropout) if dropout > 0 else None
        self.fc = nn.Linear(flat_dim, num_classes)

    def _infer_flatten_dim(self, input_size: Tuple[int, int, int]) -> int:
        with torch.no_grad():
            x = torch.zeros(1, *input_size)
            x = self.pool1(torch.relu(self.conv1(x)))
            x = self.pool2(torch.relu(self.conv2(x)))
            return int(np.prod(x.shape[1:]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        if self.bn1 is not None:
            x = self.bn1(x)
        x = torch.relu(x)
        x = self.pool1(x)
        x = self.conv2(x)
        if self.bn2 is not None:
            x = self.bn2(x)
        x = torch.relu(x)
        x = self.pool2(x)
        x = self.flatten(x)
        if self.dropout is not None:
            x = self.dropout(x)
        return self.fc(x)


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    device: torch.device,
) -> Dict[str, float]:
    training = optimizer is not None
    model.train(training)

    total_loss = 0.0
    total_correct = 0
    total_examples = 0

    for batch in loader:
        inputs, targets, _ = unpack_batch(batch)
        inputs = inputs.to(device)
        targets = targets.to(device)

        if training:
            optimizer.zero_grad()

        logits = model(inputs)
        loss = criterion(logits, targets)

        if training:
            loss.backward()
            optimizer.step()

        batch_size = targets.size(0)
        total_loss += loss.item() * batch_size
        total_correct += (logits.argmax(dim=1) == targets).sum().item()
        total_examples += batch_size

    return {
        "loss": total_loss / total_examples,
        "accuracy": total_correct / total_examples,
    }


def train_model(
    model: nn.Module,
    loaders: Dict[str, DataLoader],
    epochs: int,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    scheduler: Optional[StepLR] = None,
) -> Dict[str, List[float]]:
    criterion = nn.CrossEntropyLoss()
    model.to(device)

    history = {
        "train_loss": [],
        "train_accuracy": [],
        "val_loss": [],
        "val_accuracy": [],
        "learning_rate": [],
    }

    best_state = None
    best_val_loss = math.inf

    for _ in range(epochs):
        train_metrics = run_epoch(model, loaders["train"], criterion, optimizer, device)
        val_metrics = run_epoch(model, loaders["val"], criterion, None, device)

        history["train_loss"].append(train_metrics["loss"])
        history["train_accuracy"].append(train_metrics["accuracy"])
        history["val_loss"].append(val_metrics["loss"])
        history["val_accuracy"].append(val_metrics["accuracy"])
        history["learning_rate"].append(optimizer.param_groups[0]["lr"])

        if val_metrics["loss"] < best_val_loss:
            best_val_loss = val_metrics["loss"]
            best_state = copy.deepcopy(model.state_dict())

        if scheduler is not None:
            scheduler.step()

    if best_state is not None:
        model.load_state_dict(best_state)

    return history


@torch.no_grad()
def predict(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    model.eval()
    all_preds: List[int] = []
    all_targets: List[int] = []
    all_paths: List[str] = []
    for batch in loader:
        inputs, targets, paths = unpack_batch(batch)
        logits = model(inputs.to(device))
        preds = logits.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds.tolist())
        all_targets.extend(targets.numpy().tolist())
        if paths is not None:
            all_paths.extend(list(paths))
    return np.array(all_targets), np.array(all_preds), all_paths


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int) -> np.ndarray:
    matrix = np.zeros((num_classes, num_classes), dtype=np.int64)
    for true, pred in zip(y_true, y_pred):
        matrix[true, pred] += 1
    return matrix


def classification_report_from_confusion(
    cm: np.ndarray,
    class_names: Sequence[str],
) -> Dict[str, Dict[str, float]]:
    report: Dict[str, Dict[str, float]] = {}
    for i, class_name in enumerate(class_names):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        report[class_name] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return report


def save_json(data: Dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def save_pickle_checkpoint(payload: Dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, output_path)


def plot_curves(
    histories: Dict[str, Dict[str, List[float]]],
    metric_key: str,
    output_path: Path,
    title: str,
    ylabel: str,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for label, history in histories.items():
        plt.plot(history[metric_key], marker="o", label=label)
    plt.title(title)
    plt.xlabel("Epoch")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def export_misclassified_examples(
    example_records: Sequence[Dict[str, object]],
    output_path: Path,
    title: str,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not example_records:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cols = min(3, len(example_records))
    rows = math.ceil(len(example_records) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes_array = np.array(axes).reshape(-1)

    for ax, record in zip(axes_array, example_records):
        with Image.open(record["path"]) as image:
            ax.imshow(image, cmap="gray")
        ax.set_title(f"T: {record['true']}\nP: {record['pred']}")
        ax.axis("off")

    for ax in axes_array[len(example_records):]:
        ax.axis("off")

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def estimate_optimizer_memory_bytes(model: nn.Module, optimizer_name: str) -> int:
    param_count = sum(param.numel() for param in model.parameters())
    bytes_per_tensor = 4
    parameter_memory = param_count * bytes_per_tensor
    gradient_memory = param_count * bytes_per_tensor
    if optimizer_name == "sgd":
        state_memory = 0
    elif optimizer_name == "sgd_momentum":
        state_memory = param_count * bytes_per_tensor
    elif optimizer_name == "adam":
        state_memory = 2 * param_count * bytes_per_tensor
    else:
        raise ValueError(f"Unknown optimizer name: {optimizer_name}")
    return parameter_memory + gradient_memory + state_memory


def bytes_to_megabytes(num_bytes: int) -> float:
    return num_bytes / (1024 ** 2)


def summarize_dataset(bundle: DatasetBundle) -> Dict[str, object]:
    return {
        "train_counts": bundle.train_counts,
        "val_counts": bundle.val_counts,
        "test_counts": bundle.test_counts,
        "class_short_names": {name: CLASS_SHORT_NAMES[name] for name in bundle.class_names},
        "image_shape_after_transform": [1, 200, 200],
        "original_image_dimensions": list(bundle.original_image_dimensions),
        "loader_api": "torchvision.datasets.ImageFolder",
        "normalize_api": "torchvision.transforms.Normalize",
    }


def run_part0(output_dir: Path, batch_size: int, seed: int) -> Dict[str, object]:
    set_seed(seed)
    device = get_device()
    bundle = load_datasets(augment_train=False, seed=seed)
    loaders = make_dataloaders(bundle, batch_size=batch_size)

    relu_model = TwoLayerNet(activation="relu")
    sigmoid_model = TwoLayerNet(activation="sigmoid")

    relu_history = train_model(relu_model, loaders, epochs=20, optimizer=SGD(relu_model.parameters(), lr=0.01), device=device)
    sigmoid_history = train_model(sigmoid_model, loaders, epochs=20, optimizer=SGD(sigmoid_model.parameters(), lr=0.01), device=device)

    plot_curves(
        {"ReLU": relu_history, "Sigmoid": sigmoid_history},
        metric_key="train_loss",
        output_path=output_dir / "part0_activation_loss.png",
        title="Part 0: ReLU vs Sigmoid Training Loss",
        ylabel="Loss",
    )

    optimizer_histories = {}
    optimizer_builders = {
        "SGD": lambda m: SGD(m.parameters(), lr=0.01),
        "SGD+Momentum": lambda m: SGD(m.parameters(), lr=0.01, momentum=0.9),
        "Adam": lambda m: Adam(m.parameters(), lr=0.001),
    }
    optimizer_memory = {}
    for name, builder in optimizer_builders.items():
        model = TwoLayerNet(activation="relu")
        history = train_model(model, loaders, epochs=20, optimizer=builder(model), device=device)
        optimizer_histories[name] = history
        if name == "SGD":
            optimizer_memory[name] = bytes_to_megabytes(estimate_optimizer_memory_bytes(model, "sgd"))
        elif name == "SGD+Momentum":
            optimizer_memory[name] = bytes_to_megabytes(estimate_optimizer_memory_bytes(model, "sgd_momentum"))
        else:
            optimizer_memory[name] = bytes_to_megabytes(estimate_optimizer_memory_bytes(model, "adam"))

    plot_curves(
        optimizer_histories,
        metric_key="train_loss",
        output_path=output_dir / "part0_optimizer_loss.png",
        title="Part 0: Optimizer Comparison",
        ylabel="Loss",
    )

    baseline_model = TwoLayerNet(activation="relu")
    batchnorm_model = TwoLayerNet(activation="relu", stability="batchnorm")
    dropout_model = TwoLayerNet(activation="relu", stability="dropout")
    baseline_history = train_model(baseline_model, loaders, epochs=20, optimizer=Adam(baseline_model.parameters(), lr=0.001), device=device)
    batchnorm_history = train_model(batchnorm_model, loaders, epochs=20, optimizer=Adam(batchnorm_model.parameters(), lr=0.001), device=device)
    dropout_history = train_model(dropout_model, loaders, epochs=20, optimizer=Adam(dropout_model.parameters(), lr=0.001), device=device)

    plot_curves(
        {
            "Baseline": baseline_history,
            "BatchNorm1d": batchnorm_history,
            "Dropout(0.3)": dropout_history,
        },
        metric_key="val_loss",
        output_path=output_dir / "part0_stability_val_loss.png",
        title="Part 0: Stability Technique Comparison",
        ylabel="Validation Loss",
    )

    results = {
        "dataset_summary": summarize_dataset(bundle),
        "activation_histories": {"relu": relu_history, "sigmoid": sigmoid_history},
        "optimizer_histories": optimizer_histories,
        "optimizer_memory_mb": optimizer_memory,
        "stability_histories": {
            "baseline": baseline_history,
            "batchnorm": batchnorm_history,
            "dropout": dropout_history,
        },
        "theory_answers": {
            "cross_entropy_vs_mse": (
                "CrossEntropyLoss is preferred because it operates directly on logits for mutually exclusive classes, "
                "produces stronger gradients when the wrong class is predicted confidently, and matches categorical "
                "defect classification better than treating the labels as regression targets with MSELoss."
            ),
            "activation_observation": (
                "Sigmoid usually converges more slowly than ReLU because activations can saturate and shrink the "
                "gradient flowing through the hidden layer."
            ),
            "stability_observation": (
                "BatchNorm1d stabilizes hidden activation statistics and often improves optimization, while Dropout "
                "injects noise during training to reduce co-adaptation and overfitting."
            ),
        },
    }
    save_json(results, output_dir / "part0_results.json")
    return results


def make_cnn_model(use_batchnorm: bool = False, dropout: float = 0.0) -> DefectCNN:
    return DefectCNN(num_classes=6, use_batchnorm=use_batchnorm, dropout=dropout)


def evaluate_model(
    model: nn.Module,
    loaders: Dict[str, DataLoader],
    class_names: Sequence[str],
    device: torch.device,
) -> Dict[str, object]:
    y_true, y_pred, paths = predict(model, loaders["test"], device)
    cm = confusion_matrix(y_true, y_pred, len(class_names))
    report = classification_report_from_confusion(cm, class_names)
    lowest_f1_class = min(report.items(), key=lambda item: item[1]["f1"])[0]

    misclassified_examples = []
    crazing_patch_examples = []
    for true_idx, pred_idx, path in zip(y_true, y_pred, paths):
        if true_idx == pred_idx:
            continue
        record = {
            "path": path,
            "true": class_names[int(true_idx)],
            "pred": class_names[int(pred_idx)],
        }
        misclassified_examples.append(record)
        confusing_pair = {record["true"], record["pred"]}
        if confusing_pair == {"crazing", "patches"} and len(crazing_patch_examples) < 6:
            crazing_patch_examples.append(record)

    return {
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "lowest_f1_class": lowest_f1_class,
        "misclassified_examples": misclassified_examples[:20],
        "crazing_patches_examples": crazing_patch_examples,
    }


def find_overfitting_epoch(history: Dict[str, List[float]]) -> Optional[int]:
    best_val_loss = math.inf
    for epoch_idx, val_loss in enumerate(history["val_loss"]):
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            continue
        if history["train_loss"][epoch_idx] < history["val_loss"][epoch_idx]:
            return epoch_idx + 1
    return None


def run_part_a(output_dir: Path, batch_size: int, seed: int) -> Dict[str, object]:
    set_seed(seed)
    device = get_device()
    bundle = load_datasets(augment_train=False, seed=seed)
    loaders = make_dataloaders(bundle, batch_size=batch_size)

    model = make_cnn_model(use_batchnorm=False, dropout=0.0)
    optimizer = Adam(model.parameters(), lr=0.001)
    history = train_model(model, loaders, epochs=15, optimizer=optimizer, device=device)

    plot_curves(
        {"Train": {"metric": history["train_loss"]}, "Validation": {"metric": history["val_loss"]}},
        metric_key="metric",
        output_path=output_dir / "part_a_loss.png",
        title="Part A: Training vs Validation Loss",
        ylabel="Loss",
    )
    plot_curves(
        {"Train": {"metric": history["train_accuracy"]}, "Validation": {"metric": history["val_accuracy"]}},
        metric_key="metric",
        output_path=output_dir / "part_a_accuracy.png",
        title="Part A: Training vs Validation Accuracy",
        ylabel="Accuracy",
    )

    evaluation = evaluate_model(model, loaders, bundle.class_names, device)
    export_misclassified_examples(
        evaluation["crazing_patches_examples"],
        output_dir / "part_a_crazing_patches_misclassified.png",
        "Crazing vs Patches Misclassified Examples",
    )
    overfitting_epoch = find_overfitting_epoch(history)

    results = {
        "dataset_summary": summarize_dataset(bundle),
        "history": history,
        "evaluation": evaluation,
        "overfitting_epoch": overfitting_epoch,
        "notes": {
            "normalization": (
                "Normalization keeps pixel intensities on a consistent scale, which improves gradient behavior, "
                "reduces sensitivity to illumination scale, and usually makes CNN training faster and more stable."
            ),
            "crazing_vs_patches": (
                "Crazing and patches can be confused because both appear as irregular textured grayscale regions, "
                "and some examples share similar local contrast, streaking, and uneven lighting patterns."
            ),
        },
    }
    save_json(results, output_dir / "part_a_results.json")
    return results


def run_part_b(output_dir: Path, batch_size: int, seed: int) -> Dict[str, object]:
    set_seed(seed)
    device = get_device()

    configs = [
        ("baseline", False, False, 0.0),
        ("augmentation", True, False, 0.0),
        ("augmentation_bn", True, True, 0.0),
        ("augmentation_bn_dropout", True, True, 0.4),
    ]

    histories: Dict[str, Dict[str, List[float]]] = {}
    evaluations: Dict[str, Dict[str, object]] = {}

    for label, augment_train, use_batchnorm, dropout in configs:
        bundle = load_datasets(augment_train=augment_train, seed=seed)
        loaders = make_dataloaders(bundle, batch_size=batch_size)
        model = make_cnn_model(use_batchnorm=use_batchnorm, dropout=dropout)
        optimizer = Adam(model.parameters(), lr=0.001)
        history = train_model(model, loaders, epochs=15, optimizer=optimizer, device=device)
        histories[label] = history
        evaluations[label] = evaluate_model(model, loaders, bundle.class_names, device)

    plot_curves(
        {
            "Baseline": histories["baseline"],
            "+Augmentation": histories["augmentation"],
            "+Augmentation+BN+Dropout": histories["augmentation_bn_dropout"],
        },
        metric_key="val_accuracy",
        output_path=output_dir / "part_b_val_accuracy.png",
        title="Part B: Validation Accuracy Comparison",
        ylabel="Accuracy",
    )
    plot_curves(
        {
            "Baseline": histories["baseline"],
            "+Augmentation": histories["augmentation"],
            "+Augmentation+BN+Dropout": histories["augmentation_bn_dropout"],
        },
        metric_key="val_loss",
        output_path=output_dir / "part_b_val_loss.png",
        title="Part B: Validation Loss Comparison",
        ylabel="Loss",
    )

    best_config = max(histories.items(), key=lambda item: max(item[1]["val_accuracy"]))[0]

    results = {
        "histories": histories,
        "evaluations": evaluations,
        "best_config": best_config,
        "notes": {
            "augmentation_only_train": (
                "Augmentation should be applied only to the training set so validation and test metrics still measure "
                "generalization on unchanged unseen data instead of transformed copies."
            ),
            "batchnorm_mechanism": (
                "BatchNorm2d normalizes feature maps within each mini-batch, which reduces internal covariate shift, "
                "keeps activations in a healthier range, and often makes training steadier."
            ),
            "dropout_mechanism": (
                "During training, dropout randomly masks activations so the classifier cannot over-rely on a small set "
                "of features. During inference, dropout is disabled and the full network is used."
            ),
            "single_best_technique_reflection": (
                "If only one hardening technique could transfer to a new manufacturing dataset, augmentation is often "
                "the most broadly useful because it directly simulates viewpoint, position, and lighting variation."
            ),
        },
    }
    save_json(results, output_dir / "part_b_results.json")
    return results


def grid_search_part_c(
    output_dir: Path,
    seed: int,
    best_part_b_config: str = "augmentation_bn_dropout",
) -> Dict[str, object]:
    set_seed(seed)
    device = get_device()
    learning_rates = [0.001, 0.01]
    batch_sizes = [16, 32]

    config_settings = {
        "baseline": {"augment_train": False, "use_batchnorm": False, "dropout": 0.0},
        "augmentation": {"augment_train": True, "use_batchnorm": False, "dropout": 0.0},
        "augmentation_bn": {"augment_train": True, "use_batchnorm": True, "dropout": 0.0},
        "augmentation_bn_dropout": {"augment_train": True, "use_batchnorm": True, "dropout": 0.4},
    }
    settings = config_settings[best_part_b_config]

    rows = []
    run_histories = []
    best_row = None

    for lr in learning_rates:
        for batch_size in batch_sizes:
            bundle = load_datasets(augment_train=settings["augment_train"], seed=seed)
            loaders = make_dataloaders(bundle, batch_size=batch_size)
            model = make_cnn_model(use_batchnorm=settings["use_batchnorm"], dropout=settings["dropout"])
            optimizer = Adam(model.parameters(), lr=lr)
            history = train_model(model, loaders, epochs=15, optimizer=optimizer, device=device)
            evaluation = evaluate_model(model, loaders, bundle.class_names, device)
            row = {
                "learning_rate": lr,
                "batch_size": batch_size,
                "best_val_accuracy": max(history["val_accuracy"]),
                "final_val_accuracy": history["val_accuracy"][-1],
                "test_accuracy": sum(
                    evaluation["confusion_matrix"][i][i] for i in range(len(bundle.class_names))
                ) / sum(sum(row_vals) for row_vals in evaluation["confusion_matrix"]),
            }
            rows.append(row)
            run_histories.append({"config": row, "history": history})
            if best_row is None or (
                row["best_val_accuracy"],
                row["final_val_accuracy"],
                row["test_accuracy"],
                -row["batch_size"],
            ) > (
                best_row["best_val_accuracy"],
                best_row["final_val_accuracy"],
                best_row["test_accuracy"],
                -best_row["batch_size"],
            ):
                best_row = row

    table_lines = [
        "| learning_rate | batch_size | best_val_accuracy | final_val_accuracy | test_accuracy |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        table_lines.append(
            f"| {row['learning_rate']} | {row['batch_size']} | {row['best_val_accuracy']:.4f} | "
            f"{row['final_val_accuracy']:.4f} | {row['test_accuracy']:.4f} |"
        )

    bundle = load_datasets(augment_train=settings["augment_train"], seed=seed)
    loaders = make_dataloaders(bundle, batch_size=best_row["batch_size"])

    best_model = make_cnn_model(use_batchnorm=settings["use_batchnorm"], dropout=settings["dropout"])
    best_optimizer = Adam(best_model.parameters(), lr=best_row["learning_rate"])
    best_history = train_model(best_model, loaders, epochs=15, optimizer=best_optimizer, device=device)
    best_eval = evaluate_model(best_model, loaders, bundle.class_names, device)

    scheduled_model = make_cnn_model(use_batchnorm=settings["use_batchnorm"], dropout=settings["dropout"])
    scheduled_optimizer = Adam(scheduled_model.parameters(), lr=best_row["learning_rate"])
    scheduler = StepLR(scheduled_optimizer, step_size=5, gamma=0.5)
    scheduled_history = train_model(
        scheduled_model,
        loaders,
        epochs=15,
        optimizer=scheduled_optimizer,
        scheduler=scheduler,
        device=device,
    )
    scheduled_eval = evaluate_model(scheduled_model, loaders, bundle.class_names, device)

    best_test_accuracy = sum(best_eval["confusion_matrix"][i][i] for i in range(len(bundle.class_names))) / sum(
        sum(row_vals) for row_vals in best_eval["confusion_matrix"]
    )
    scheduled_test_accuracy = sum(
        scheduled_eval["confusion_matrix"][i][i] for i in range(len(bundle.class_names))
    ) / sum(sum(row_vals) for row_vals in scheduled_eval["confusion_matrix"])

    save_pickle_checkpoint(
        {
            "model_state_dict": scheduled_model.state_dict(),
            "config": {
                "learning_rate": best_row["learning_rate"],
                "batch_size": best_row["batch_size"],
                "use_batchnorm": settings["use_batchnorm"],
                "dropout": settings["dropout"],
                "augment_train": settings["augment_train"],
            },
        },
        output_dir / "defect_cnn_best_steplr.pkl",
    )

    results = {
        "selected_part_b_config": best_part_b_config,
        "grid_search_rows": rows,
        "grid_search_histories": run_histories,
        "markdown_table": "\n".join(table_lines),
        "best_combination": best_row,
        "best_unscheduled_history": best_history,
        "best_unscheduled_test_evaluation": best_eval,
        "best_unscheduled_test_accuracy": best_test_accuracy,
        "step_lr_history": scheduled_history,
        "step_lr_test_evaluation": scheduled_eval,
        "step_lr_test_accuracy": scheduled_test_accuracy,
    }
    save_json(results, output_dir / "part_c_results.json")
    return results


def run_optuna_search(output_dir: Path, seed: int, trials: int = 10) -> Dict[str, object]:
    if optuna is None:
        raise RuntimeError("Optuna is not installed. Install optuna to run Part C.15.")

    set_seed(seed)
    device = get_device()

    def objective(trial: optuna.Trial) -> float:
        lr = trial.suggest_float("lr", 1e-4, 1e-1, log=True)
        batch_size = trial.suggest_int("batch_size", 8, 64)
        bundle = load_datasets(augment_train=True, seed=seed)
        loaders = make_dataloaders(bundle, batch_size=batch_size)
        model = make_cnn_model(use_batchnorm=True, dropout=0.4)
        optimizer = Adam(model.parameters(), lr=lr)
        history = train_model(model, loaders, epochs=10, optimizer=optimizer, device=device)
        return max(history["val_accuracy"])

    sampler = optuna.samplers.TPESampler(seed=seed)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=trials)

    results = {
        "best_params": study.best_params,
        "best_value": study.best_value,
        "trials": [
            {
                "number": trial.number,
                "value": trial.value,
                "params": trial.params,
            }
            for trial in study.trials
        ],
    }
    save_json(results, output_dir / "part_c_optuna_results.json")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NEU surface defect assignment runner")
    parser.add_argument("--part", choices=["part0", "parta", "partb", "partc", "all", "optuna"], default="all")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--optuna-trials", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir

    if args.part in {"part0", "all"}:
        run_part0(output_dir, batch_size=args.batch_size, seed=args.seed)

    part_b_results = None
    if args.part in {"parta", "all"}:
        run_part_a(output_dir, batch_size=args.batch_size, seed=args.seed)

    if args.part in {"partb", "all"}:
        part_b_results = run_part_b(output_dir, batch_size=args.batch_size, seed=args.seed)

    if args.part in {"partc", "all"}:
        if part_b_results is None:
            part_b_path = output_dir / "part_b_results.json"
            if part_b_path.exists():
                with part_b_path.open("r", encoding="utf-8") as fh:
                    part_b_results = json.load(fh)
            else:
                part_b_results = {"best_config": "augmentation_bn_dropout"}
        grid_search_part_c(output_dir, seed=args.seed, best_part_b_config=part_b_results["best_config"])

    if args.part in {"optuna", "all"}:
        run_optuna_search(output_dir, seed=args.seed, trials=args.optuna_trials)


if __name__ == "__main__":
    main()
