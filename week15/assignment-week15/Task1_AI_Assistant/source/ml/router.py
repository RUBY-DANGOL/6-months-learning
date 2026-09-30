import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from onnxruntime.quantization import QuantType, quantize_dynamic
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import onnxruntime as ort

SEED = 0
MAX_LEN = 64
DATASET = "bitext/Bitext-customer-support-llm-chatbot-training-dataset"
ROOT = Path(__file__).resolve().parent


def set_seed():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)


def load_bitext():
    from datasets import load_dataset

    rows = load_dataset(DATASET, split="train")
    texts = list(rows["instruction"])
    names = sorted(set(rows["category"]))
    index = {name: i for i, name in enumerate(names)}
    return texts, [index[c] for c in rows["category"]], names


def split(texts, labels):
    x_train, x_rest, y_train, y_rest = train_test_split(
        texts, labels, test_size=0.2, stratify=labels, random_state=SEED
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_rest, y_rest, test_size=0.5, stratify=y_rest, random_state=SEED
    )
    return (x_train, y_train), (x_val, y_val), (x_test, y_test)


def encode(tokenizer, texts):
    batch = tokenizer(
        texts, truncation=True, padding="max_length", max_length=MAX_LEN, return_tensors="pt"
    )
    return batch["input_ids"], batch["attention_mask"]


def finetune(model, tokenizer, train, device, epochs, lr, batch_size):
    ids, mask = encode(tokenizer, train[0])
    loader = DataLoader(
        TensorDataset(ids, mask, torch.tensor(train[1])), batch_size=batch_size, shuffle=True
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    schedule = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=lr, total_steps=epochs * len(loader), pct_start=0.1
    )
    scaler = torch.amp.GradScaler(device, enabled=device == "cuda")
    model.train()
    for epoch in range(1, epochs + 1):
        total = 0.0
        for input_ids, attention_mask, labels in loader:
            optimizer.zero_grad()
            with torch.autocast(device, enabled=device == "cuda"):
                out = model(
                    input_ids=input_ids.to(device),
                    attention_mask=attention_mask.to(device),
                    labels=labels.to(device),
                )
            scaler.scale(out.loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            schedule.step()
            total += out.loss.item()
        print(f"epoch {epoch}/{epochs}  loss {total / len(loader):.4f}")
    return model


def export_onnx(model, out_dir: Path):
    model.eval().cpu()
    dummy = (torch.ones(1, MAX_LEN, dtype=torch.long), torch.ones(1, MAX_LEN, dtype=torch.long))
    fp32 = out_dir / "model.onnx"
    torch.onnx.export(
        model,
        dummy,
        str(fp32),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "logits": {0: "batch"},
        },
        opset_version=14,
        do_constant_folding=True,
    )
    int8 = out_dir / "model.int8.onnx"
    quantize_dynamic(str(fp32), str(int8), weight_type=QuantType.QInt8)
    return fp32, int8


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.intra_op_num_threads = 2
    return ort.InferenceSession(str(path), options, providers=["CPUExecutionProvider"])


def infer(sess, tokenizer, texts, batch_size=64):
    chunks = []
    for start in range(0, len(texts), batch_size):
        batch = tokenizer(
            texts[start : start + batch_size],
            truncation=True,
            padding=True,
            max_length=MAX_LEN,
            return_tensors="np",
        )
        chunks.append(
            sess.run(
                None,
                {
                    "input_ids": batch["input_ids"].astype(np.int64),
                    "attention_mask": batch["attention_mask"].astype(np.int64),
                },
            )[0]
        )
    return np.concatenate(chunks)


def score(y_true, logits):
    predictions = logits.argmax(1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, predictions, average="macro", zero_division=0
    )
    return {
        "accuracy": float((predictions == np.array(y_true)).mean()),
        "precision": float(precision),
        "recall": float(recall),
        "macro_f1": float(f1),
    }


def latency(sess, tokenizer, runs=100):
    batch = tokenizer(
        "my card was charged twice, I want a refund", truncation=True, return_tensors="np"
    )
    feed = {
        "input_ids": batch["input_ids"].astype(np.int64),
        "attention_mask": batch["attention_mask"].astype(np.int64),
    }
    for _ in range(10):
        sess.run(None, feed)
    start = time.perf_counter()
    for _ in range(runs):
        sess.run(None, feed)
    return (time.perf_counter() - start) / runs * 1000


def energy(logits):
    top = logits.max(axis=1, keepdims=True)
    return (top + np.log(np.exp(logits - top).sum(axis=1, keepdims=True))).ravel()


def calibrate(test_logits, paraphrase_logits, ood_logits, margin=0.25):
    test_energy = energy(test_logits)
    free_energy = energy(paraphrase_logits)
    ood_energy = energy(ood_logits)

    threshold = round(float(free_energy.min()) - margin, 3)
    return {
        "energy_threshold": threshold,
        "calibrated_on": "free-form paraphrases, minimum minus margin",
        "margin": margin,
        "test_set_kept": round(float((test_energy >= threshold).mean()), 4),
        "paraphrases_kept": round(float((free_energy >= threshold).mean()), 4),
        "out_of_domain_rejected": round(float((ood_energy < threshold).mean()), 4),
        "test_energy_p1": round(float(np.quantile(test_energy, 0.01)), 3),
        "paraphrase_energy_min": round(float(free_energy.min()), 3),
        "paraphrase_energy_median": round(float(np.median(free_energy)), 3),
        "out_of_domain_energy_max": round(float(ood_energy.max()), 3),
        "out_of_domain_energy_median": round(float(np.median(ood_energy)), 3),
        "overlap": bool(free_energy.min() < ood_energy.max()),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Export the week 14 support router to ONNX, quantize it, and calibrate abstention."
    )
    parser.add_argument("--checkpoint", help="Fine-tuned checkpoint to export. Omit to fine-tune first.")
    parser.add_argument("--base", default="distilbert-base-uncased")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--out", default=str(ROOT / "models" / "router"))
    args = parser.parse_args()

    set_seed()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    texts, labels, names = load_bitext()
    train, _val, test = split(texts, labels)
    print(f"{len(texts)} messages, {len(names)} agents: {names}")
    print(f"train {len(train[0])}  test {len(test[0])}")

    if args.checkpoint:
        print(f"loading fine-tuned checkpoint {args.checkpoint}")
        tokenizer = AutoTokenizer.from_pretrained(args.checkpoint)
        model = AutoModelForSequenceClassification.from_pretrained(args.checkpoint)
        order = [model.config.id2label[i] for i in range(model.config.num_labels)]
        if order != names:
            raise SystemExit(f"checkpoint label order {order} does not match dataset order {names}")
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"fine-tuning {args.base} on {device}")
        tokenizer = AutoTokenizer.from_pretrained(args.base)
        model = AutoModelForSequenceClassification.from_pretrained(
            args.base,
            num_labels=len(names),
            id2label=dict(enumerate(names)),
            label2id={n: i for i, n in enumerate(names)},
        ).to(device)
        finetune(model, tokenizer, train, device, args.epochs, args.lr, args.batch_size)

    fp32, int8 = export_onnx(model, out_dir)
    tokenizer.backend_tokenizer.save(str(out_dir / "tokenizer.json"))
    (out_dir / "labels.json").write_text(json.dumps(names))

    sessions = {"onnx fp32": session(fp32), "onnx int8": session(int8)}
    results, logits_by_graph = {}, {}
    for name, sess in sessions.items():
        logits_by_graph[name] = infer(sess, tokenizer, test[0])
        results[name] = score(test[1], logits_by_graph[name])
        results[name]["latency_ms"] = round(latency(sess, tokenizer), 2)
        results[name]["size_mb"] = round((fp32 if "fp32" in name else int8).stat().st_size / 1e6, 1)

    print(f"\nheld-out test set, {len(test[0])} messages")
    print(f"{'graph':<12}{'accuracy':>10}{'precision':>11}{'recall':>9}{'macro-F1':>10}{'ms':>8}{'MB':>8}")
    for name, r in results.items():
        print(
            f"{name:<12}{r['accuracy']:>10.4f}{r['precision']:>11.4f}{r['recall']:>9.4f}"
            f"{r['macro_f1']:>10.4f}{r['latency_ms']:>8.2f}{r['size_mb']:>8.1f}"
        )
    agreement = float(
        (logits_by_graph["onnx fp32"].argmax(1) == logits_by_graph["onnx int8"].argmax(1)).mean()
    )
    print(f"fp32/int8 prediction agreement: {agreement:.4f}")

    print("\nper-agent, INT8")
    print(classification_report(test[1], logits_by_graph["onnx int8"].argmax(1), target_names=names, digits=3))

    def probe(name: str) -> list[str]:
        return [
            line.strip()
            for line in (ROOT / "data" / name).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    int8_session = sessions["onnx int8"]
    labelled = [line.split("	", 1) for line in probe("in_domain_paraphrases.txt")]
    paraphrases = [text for _agent, text in labelled]
    gold = [names.index(agent) for agent, _text in labelled]
    paraphrase_logits = infer(int8_session, tokenizer, paraphrases)
    free_form = score(gold, paraphrase_logits)
    print("\nfree-form paraphrases, written by hand, not from the dataset")
    print(f"  n={len(paraphrases)}  accuracy={free_form['accuracy']:.3f}  macro-F1={free_form['macro_f1']:.3f}")
    for text, predicted, actual in zip(paraphrases, paraphrase_logits.argmax(1), gold):
        if predicted != actual:
            print(f"    {names[actual]:12} -> {names[predicted]:12} {text}")

    ood_logits = infer(int8_session, tokenizer, probe("out_of_domain.txt"))
    abstain = calibrate(logits_by_graph["onnx int8"], paraphrase_logits, ood_logits)
    print("out-of-scope gate, energy score on INT8 logits")
    for key, value in abstain.items():
        print(f"  {key:28} {value}")
    if abstain["overlap"]:
        print(
            "  note: free-form in-domain and out-of-domain energies overlap, so this gate is a\n"
            "        coarse pre-filter only. Retrieval relevance is the real out-of-scope check."
        )

    (out_dir / "router.json").write_text(
        json.dumps(
            {
                "labels": names,
                "max_length": MAX_LEN,
                "test_size": len(test[0]),
                "metrics": results,
                "fp32_int8_agreement": agreement,
                "free_form": free_form,
                "abstain": abstain,
            },
            indent=2,
        )
    )
    print(f"\nartifacts written to {out_dir}")


if __name__ == "__main__":
    main()
