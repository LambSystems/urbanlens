#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config_utils import load_config, resolve_path


def index_alphaearth_files(alphaearth_dir: Path):
    tif_files = list(alphaearth_dir.rglob("*.tif")) + list(alphaearth_dir.rglob("*.TIF"))
    by_stem, by_name = {}, {}
    for tif in tif_files:
        by_name[tif.name] = tif
        by_stem[tif.stem] = tif
        by_stem[tif.stem.lower()] = tif
    return by_name, by_stem


def find_alphaearth_file(index_name: str, original_thermal_name: str, by_name, by_stem):
    indexed_stem = Path(index_name).stem
    thermal_stem = Path(original_thermal_name).stem
    candidates = [
        f"satellite_embedding_{thermal_stem}..tif",
        f"satellite_embedding_{thermal_stem}.tif",
        f"satellite_embedding_{thermal_stem}",
        f"{thermal_stem}.tif",
        thermal_stem,
        f"{indexed_stem}.tif",
        indexed_stem,
    ]
    for cand in candidates:
        if cand in by_name:
            return by_name[cand]
        if cand in by_stem:
            return by_stem[cand]
        low = str(cand).lower()
        if low in by_stem:
            return by_stem[low]
    return None


def main(config_path: str):
    config = load_config(config_path, PROJECT_ROOT)

    dataset_dir = Path(config["dataset_dir"])
    rgb_dir = Path(config["rgb_dir"])
    thermal_dir = Path(config["thermal_dir"])
    metadata_file = Path(config["metadata_file"])
    train_split_file = Path(config["train_split_file"])
    alphaearth_dir = Path(config["alphaearth_dir"])
    output_file = Path(config["manifest_raw"])

    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    with open(train_split_file, "r") as f:
        split_data = json.load(f)

    by_name, by_stem = index_alphaearth_files(alphaearth_dir)
    print(f"Indexed {len(by_name)} AlphaEarth tif files", flush=True)

    samples = []
    skipped_missing_rgb = 0
    skipped_missing_thermal = 0
    skipped_missing_metadata = 0
    skipped_missing_alphaearth = 0

    for indexed_name, original_pair in split_data.items():
        indexed_stem = Path(indexed_name).stem
        
        original_thermal_name = original_pair[0]
        original_rgb_name = original_pair[1]
        
        rgb_rel = rgb_dir / indexed_name
        thermal_rel = thermal_dir / indexed_name

        rgb_abs = dataset_dir / rgb_rel
        thermal_abs = dataset_dir / thermal_rel

        if not rgb_abs.exists():
            skipped_missing_rgb += 1
            continue
        if not thermal_abs.exists():
            skipped_missing_thermal += 1
            continue

        meta = metadata.get(original_thermal_name)
        if meta is None:
            skipped_missing_metadata += 1
            continue

        alphaearth_file = find_alphaearth_file(indexed_name, original_thermal_name, by_name, by_stem)
        if alphaearth_file is None:
            skipped_missing_alphaearth += 1
            continue

        sample = {
            "sample_id": indexed_stem,
            "rgb_path": str(rgb_rel),
            "thermal_path": str(thermal_rel),
            "alphaearth_path": str(alphaearth_file.relative_to(dataset_dir)),
            "original_thermal_name": original_thermal_name,
            "original_rgb_name": original_rgb_name,
            "lat": meta.get("lat", 0.0),
            "lon": meta.get("lng", 0.0),
            "timestamp": meta.get("timestamp", ""),
            "weather_timestamp": meta.get("weather_timestamp", ""),
            "split": "train",
            "dataset_name": "hackathon",
            "style_id": 0,
        }

        for key in [
            "temperature_2m",
            "relative_humidity_2m",
            "total_cloud_cover",
            "wind_speed_10m",
            "wind_direction_10m",
            "direct_radiation",
            "diffuse_radiation",
            "weather_code",
        ]:
            if key in meta:
                sample[key] = meta[key]

        samples.append(sample)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")

    print(f"Created manifest with {len(samples)} samples", flush=True)
    print(f"Skipped missing RGB: {skipped_missing_rgb}", flush=True)
    print(f"Skipped missing thermal: {skipped_missing_thermal}", flush=True)
    print(f"Skipped missing metadata: {skipped_missing_metadata}", flush=True)
    print(f"Skipped missing AlphaEarth: {skipped_missing_alphaearth}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    main(args.config)