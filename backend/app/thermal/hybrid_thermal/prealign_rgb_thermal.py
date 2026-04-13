#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config_utils import load_config, resolve_path
from data_utils import process_rgb_for_alignment, process_thermal_for_alignment


def main(config_path: str):
    config = load_config(config_path, PROJECT_ROOT)
    dataset_dir = Path(config["dataset_dir"])

    manifest_in = Path(config["manifest_split"])
    manifest_out = Path(config["manifest_file"])
    out_rgb_dir = Path(config["aligned_rgb_dir"])
    out_thermal_dir = Path(config["aligned_thermal_dir"])

    out_rgb_dir.mkdir(parents=True, exist_ok=True)
    out_thermal_dir.mkdir(parents=True, exist_ok=True)
    manifest_out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    with open(manifest_in, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    processed = 0
    missing = 0
    failed = 0
    new_rows = []

    for row in rows:
        sample_id = str(row["sample_id"])
        rgb_path = dataset_dir / row["rgb_path"]
        thermal_path = dataset_dir / row["thermal_path"]

        if not rgb_path.exists() or not thermal_path.exists():
            missing += 1
            continue

        try:
            rgb_img = process_rgb_for_alignment(rgb_path, target_rgb_crop=(2700, 2160), target_size=(640, 512))
            thermal_img = process_thermal_for_alignment(thermal_path, target_size=(640, 512))
        except Exception as e:
            print(f"Failed processing sample {sample_id}: {e}", flush=True)
            failed += 1
            continue

        rgb_out = out_rgb_dir / f"{sample_id}.png"
        thermal_out = out_thermal_dir / f"{sample_id}.png"

        rgb_img.save(rgb_out)
        thermal_img.save(thermal_out)

        new_row = dict(row)
        new_row["rgb_path"] = str(rgb_out)
        new_row["thermal_path"] = str(thermal_out)
        new_row["preprocess"] = {
            "rgb_center_crop": [2700, 2160],
            "final_resize": [640, 512],
        }

        new_rows.append(new_row)
        processed += 1

    with open(manifest_out, "w") as f:
        for row in new_rows:
            f.write(json.dumps(row) + "\n")

    print("=== PREALIGN SUMMARY ===", flush=True)
    print("Input manifest :", manifest_in, flush=True)
    print("Output manifest:", manifest_out, flush=True)
    print("Processed      :", processed, flush=True)
    print("Missing        :", missing, flush=True)
    print("Failed         :", failed, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    main(args.config)