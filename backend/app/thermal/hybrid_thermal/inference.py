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
from torchvision.transforms import InterpolationMode

from config_utils import load_config
from hybrid_model import HybridThermalModel
from metrics_utils import denorm_thermal


def choose_checkpoint(checkpoint_dir: Path) -> Path:
    all_ckpts = sorted(checkpoint_dir.glob("*.pth"))
    assert all_ckpts, f"No checkpoints found in {checkpoint_dir}"
    for name in ["best_psnr.pth", "best_loss.pth", "latest.pth"]:
        candidate = checkpoint_dir / name
        if candidate.exists():
            return candidate
    return all_ckpts[0]


def save_pred_tensor(pred_tensor: torch.Tensor, output_path: Path):
    pred_vis = denorm_thermal(pred_tensor).detach().cpu().squeeze().numpy()
    pred_uint8 = (pred_vis * 255).clip(0, 255).astype(np.uint8)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pred_uint8, mode="L").save(output_path)


def main(config_path, limit: int | None = None):
    config = load_config(config_path, PROJECT_ROOT)
    device_name = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    if device_name == "cuda" and not torch.cuda.is_available():
        device_name = "cpu"
    device = torch.device(device_name)

    checkpoint_dir = Path(config["checkpoint_dir"])
    checkpoint = torch.load(choose_checkpoint(checkpoint_dir), map_location=device)

    model = HybridThermalModel(
        alphaearth_channels=config.get("alphaearth_encoder_channels", 64),
        alphaearth_latent_dim=config.get("alphaearth_latent_dim", 512),
        fusion_type=config.get("fusion_type", "gated"),
        use_metadata=config.get("use_metadata", False),
        metadata_features=config.get("metadata_features"),
        base_channels=config.get("base_channels", 64),
        out_size=tuple(config.get("hybrid_bottleneck_size", [16, 16])),
    )
    model.load_state_dict(checkpoint["model_state_dict"], strict=False)
    model.to(device).eval()

    size_hw = tuple(config.get("augmentations", {}).get("resize", [640, 512]))
    size_wh = (size_hw[1], size_hw[0])
    rgb_transform = v2.Compose([
        v2.Resize(size_wh, interpolation=InterpolationMode.BILINEAR, antialias=True),
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])

    #test_rgb_dir = Path(config["test_rgb_dir"])
    test_rgb_dir = Path(config.get("test_aligned_rgb_dir", config["test_rgb_dir"]))
    
    test_predict_dir = Path(config["test_predict_dir"])
    test_predict_dir.mkdir(parents=True, exist_ok=True)

    #rgb_files = sorted(list(test_rgb_dir.glob("*.JPG")) + list(test_rgb_dir.glob("*.jpg")) + list(test_rgb_dir.glob("*.jpeg")))
    rgb_files = sorted(
        list(test_rgb_dir.glob("*.png")) +
        list(test_rgb_dir.glob("*.JPG")) +
        list(test_rgb_dir.glob("*.jpg")) +
        list(test_rgb_dir.glob("*.jpeg"))
    )
    if limit is not None:
        rgb_files = rgb_files[:limit]
    assert rgb_files, f"No RGB files found in {test_rgb_dir}"

    for p in test_predict_dir.glob("*"):
        if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            p.unlink()

    for i, rgb_path in enumerate(rgb_files, start=1):
        rgb_tensor = rgb_transform(Image.open(rgb_path).convert("RGB")).unsqueeze(0).to(device)
        with torch.no_grad():
            pred_thermal = model(rgb_tensor, None, None, None)
        #output_path = test_predict_dir / rgb_path.name
        output_path = test_predict_dir / f"{rgb_path.stem}.png"
        
        save_pred_tensor(pred_thermal[0], output_path)
        if i % 25 == 0 or i == len(rgb_files):
            print(f"Saved {i}/{len(rgb_files)} predictions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    main(args.config, limit=args.limit)
