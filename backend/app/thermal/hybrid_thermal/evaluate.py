#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DEFAULT_CONFIG = PROJECT_ROOT / "backend" / "models" / "hybrid_thermal" / "config.yaml"

import numpy as np
import torch
from PIL import Image
import torchvision.transforms.v2 as v2
import lpips

from config_utils import load_config
from metrics_utils import compute_psnr_torch, compute_ssim_simple


def main(config_path):
    config = load_config(config_path, PROJECT_ROOT)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    '''
    eval_transform = v2.Compose([
        v2.ToImage(),
        v2.Resize((256, 256), interpolation=v2.InterpolationMode.BILINEAR, antialias=True),
        v2.ToDtype(torch.float32, scale=True),
    ])
    '''
    eval_transform = v2.Compose([
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
    ])
    pred_dir = Path(config["test_predict_dir"])
    #target_dir = Path(config["test_target_dir"])
    target_dir = Path(config.get("test_aligned_thermal_dir", config["test_target_dir"]))

    pred_fns = sorted([p for p in pred_dir.glob("*") if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg"]])
    target_fns = sorted([p for p in target_dir.glob("*") if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg"]])

    assert pred_fns, f"No predictions found in {pred_dir}"
    assert target_fns, f"No evaluation targets found in {target_dir}"
    assert len(pred_fns) == len(target_fns), (
        f"Prediction and target counts do not match: {len(pred_fns)} predictions, "
        f"{len(target_fns)} targets"
    )

    lpips_model = lpips.LPIPS(net="alex").to(device)

    def _load_gray_tensor(path):
        img = Image.open(path).convert("L")
        return eval_transform(img).unsqueeze(0).to(device)

    def calculate_lpips_real(pred, target):
        pred3 = pred.repeat(1, 3, 1, 1) * 2 - 1
        target3 = target.repeat(1, 3, 1, 1) * 2 - 1
        with torch.no_grad():
            val = lpips_model(pred3, target3)
        return float(val.item())

    psnr_vals, ssim_vals, lpips_vals = [], [], []
    for pred_fn, target_fn in zip(pred_fns, target_fns):
        pred = _load_gray_tensor(pred_fn)
        target = _load_gray_tensor(target_fn)
        psnr_vals.append(compute_psnr_torch(pred, target))
        ssim_vals.append(compute_ssim_simple(pred, target))
        lpips_vals.append(calculate_lpips_real(pred, target))

    print("=== FINAL RESULTS ===")
    print(f"PSNR : {float(np.mean(psnr_vals)):.6f}")
    print(f"SSIM : {float(np.mean(ssim_vals)):.6f}")
    print(f"LPIPS: {float(np.mean(lpips_vals)):.6f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()
    main(args.config)
