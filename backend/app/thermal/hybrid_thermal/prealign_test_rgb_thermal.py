#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DEFAULT_CONFIG = PROJECT_ROOT / "backend" / "models" / "hybrid_thermal" / "config.yaml"

from config_utils import load_config
from data_utils import process_rgb_for_alignment, process_thermal_for_alignment


def list_jpeg_files(directory: Path) -> list[Path]:
    files: dict[Path, Path] = {}
    for pattern in ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG"):
        for path in directory.glob(pattern):
            files[path.resolve()] = path
    return sorted(files.values(), key=lambda path: path.name.lower())


def main(config_path: str, limit: int | None = None):
    config = load_config(config_path, PROJECT_ROOT)

    test_rgb_dir = Path(config["test_rgb_dir"])
    test_target_dir = Path(config["test_target_dir"])
    out_rgb_dir = Path(config["test_aligned_rgb_dir"])
    out_thermal_dir = Path(config["test_aligned_thermal_dir"])

    out_rgb_dir.mkdir(parents=True, exist_ok=True)
    out_thermal_dir.mkdir(parents=True, exist_ok=True)
    for output_dir in (out_rgb_dir, out_thermal_dir):
        for old_png in output_dir.glob("*.png"):
            old_png.unlink()

    rgb_files = list_jpeg_files(test_rgb_dir)
    thermal_files = list_jpeg_files(test_target_dir)
    if limit is not None:
        rgb_files = rgb_files[:limit]
        thermal_files = thermal_files[:limit]
    thermal_names = {path.name for path in thermal_files}

    assert len(rgb_files) > 0, f"No RGB files found in {test_rgb_dir}"
    if len(rgb_files) != len(thermal_files):
        print(
            f"Warning: found {len(rgb_files)} test RGB files and {len(thermal_files)} test thermal files. "
            "RGB will be aligned for inference; thermal targets will be aligned only when present.",
            flush=True,
        )

    processed = 0
    processed_thermal = 0

    for rgb_path in rgb_files:
        thermal_path = test_target_dir / rgb_path.name

        rgb_img = process_rgb_for_alignment(
            rgb_path,
            target_rgb_crop=(2700, 2160),
            target_size=(640, 512),
        )

        rgb_out = out_rgb_dir / f"{rgb_path.stem}.png"
        rgb_img.save(rgb_out)

        if rgb_path.name in thermal_names:
            thermal_img = process_thermal_for_alignment(
                thermal_path,
                target_size=(640, 512),
            )
            thermal_out = out_thermal_dir / f"{thermal_path.stem}.png"
            thermal_img.save(thermal_out)
            processed_thermal += 1

        processed += 1
        if processed % 25 == 0 or processed == len(rgb_files):
            print(f"Processed {processed}/{len(rgb_files)} test pairs", flush=True)

    print("=== TEST PREALIGN SUMMARY ===", flush=True)
    print("Input RGB dir   :", test_rgb_dir, flush=True)
    print("Input Thermal dir:", test_target_dir, flush=True)
    print("Output RGB dir  :", out_rgb_dir, flush=True)
    print("Output Thermal dir:", out_thermal_dir, flush=True)
    print("Processed RGB   :", processed, flush=True)
    print("Processed Thermal:", processed_thermal, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    main(args.config, limit=args.limit)
