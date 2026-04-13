#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse
import json
import random

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config_utils import load_config, resolve_path


def split_manifest(manifest_path, output_path, train_ratio=0.7, val_ratio=0.15, seed=42):
    samples = []
    with open(manifest_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))

    if len(samples) == 0:
        raise ValueError(f"No samples found in {manifest_path}")

    random.seed(seed)
    random.shuffle(samples)

    n = len(samples)
    n_train = max(1, int(n * train_ratio))
    n_val = max(1, int(n * val_ratio))
    n_test = n - n_train - n_val

    if n >= 3 and n_test < 1:
        n_test = 1
        if n_train > n_val:
            n_train -= 1
        else:
            n_val -= 1

    for i, sample in enumerate(samples):
        if i < n_train:
            sample["split"] = "train"
        elif i < n_train + n_val:
            sample["split"] = "val"
        else:
            sample["split"] = "test"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")

    print(f"Saved split manifest to: {output_path}", flush=True)
    print(f"Total: {len(samples)}", flush=True)
    print(f"Train: {sum(1 for s in samples if s['split'] == 'train')}", flush=True)
    print(f"Val:   {sum(1 for s in samples if s['split'] == 'val')}", flush=True)
    print(f"Test:  {sum(1 for s in samples if s['split'] == 'test')}", flush=True)


def main(config_path: str):
    config = load_config(config_path, PROJECT_ROOT)
    dataset_dir = Path(config["dataset_dir"])
    manifest_in = Path(config["manifest_raw"])
    manifest_out = Path(config["manifest_split"])
    split_manifest(manifest_in, manifest_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    main(args.config)