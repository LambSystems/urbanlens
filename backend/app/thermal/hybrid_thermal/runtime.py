from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torchvision.transforms.v2 as v2
from PIL import Image, ImageOps
from torchvision.transforms import InterpolationMode

from .data_utils import process_rgb_for_alignment
from .hybrid_model import HybridThermalModel
from .metrics_utils import denorm_thermal


BACKEND_ROOT = Path(__file__).resolve().parents[3]
MODEL_ROOT = BACKEND_ROOT / "models" / "hybrid_thermal"
CHECKPOINT_DIR = MODEL_ROOT / "checkpoints"
DATA_ROOT = BACKEND_ROOT / "data" / "hybrid_thermal"
PREDICT_DIR = DATA_ROOT / "Predict_Thermal"
ALIGNED_DIR = DATA_ROOT / "Test_RGB_centercrop_640x512"


def choose_checkpoint(checkpoint_dir: Path = CHECKPOINT_DIR) -> Path:
    for name in ("best_psnr.pth", "best_loss.pth", "latest.pth"):
        candidate = checkpoint_dir / name
        if candidate.exists():
            return candidate
    checkpoints = sorted(checkpoint_dir.glob("*.pth"))
    if not checkpoints:
        raise FileNotFoundError(f"No hybrid_thermal checkpoints found in {checkpoint_dir}")
    return checkpoints[0]


def _device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=1)
def load_model() -> tuple[HybridThermalModel, torch.device, Path]:
    device = _device()
    checkpoint_path = choose_checkpoint()
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = HybridThermalModel(
        alphaearth_channels=64,
        alphaearth_latent_dim=512,
        fusion_type="gated",
        use_metadata=False,
        metadata_features=["lat", "lon", "month", "day_of_year", "hour"],
        base_channels=64,
        out_size=(16, 16),
    )
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict, strict=False)
    model.to(device).eval()
    return model, device, checkpoint_path


def _transform() -> v2.Compose:
    return v2.Compose(
        [
            v2.Resize((512, 640), interpolation=InterpolationMode.BILINEAR, antialias=True),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ]
    )


def _save_pred_tensor(pred_tensor: torch.Tensor, output_path: Path) -> np.ndarray:
    pred_vis = denorm_thermal(pred_tensor).detach().cpu().squeeze().numpy()
    pred_uint8 = (pred_vis * 255).clip(0, 255).astype(np.uint8)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pred_uint8, mode="L").save(output_path)
    return pred_uint8


def _save_thermal_preview(gray_path: Path, output_path: Path) -> Path:
    gray = Image.open(gray_path).convert("L")
    stretched = ImageOps.autocontrast(gray, cutoff=1)
    preview = ImageOps.colorize(
        stretched,
        black="#130704",
        mid="#d85a00",
        white="#fff1a8",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    preview.save(output_path)
    return output_path


def _hotspot_regions(pred_uint8: np.ndarray, max_regions: int = 5) -> list[dict[str, Any]]:
    threshold = max(float(np.percentile(pred_uint8, 85)), 1.0)
    mask = pred_uint8 >= threshold
    visited = np.zeros(mask.shape, dtype=bool)
    height, width = mask.shape
    regions: list[dict[str, Any]] = []

    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue

            stack = [(x, y)]
            visited[y, x] = True
            pixels: list[tuple[int, int]] = []
            while stack:
                px, py = stack.pop()
                pixels.append((px, py))
                for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((nx, ny))

            if len(pixels) < 64:
                continue

            xs = np.array([p[0] for p in pixels])
            ys = np.array([p[1] for p in pixels])
            intensities = pred_uint8[ys, xs] / 255.0
            regions.append(
                {
                    "centroid_px": {"x": float(xs.mean()), "y": float(ys.mean())},
                    "bbox_px": {
                        "x": int(xs.min()),
                        "y": int(ys.min()),
                        "w": int(xs.max() - xs.min() + 1),
                        "h": int(ys.max() - ys.min() + 1),
                    },
                    "intensity": round(float(intensities.mean()), 4),
                    "area_px": int(len(pixels)),
                }
            )

    regions.sort(key=lambda item: (item["intensity"], item["area_px"]), reverse=True)
    return regions[:max_regions]


def predict_one(
    rgb_image_path: str | Path,
    output_dir: str | Path = PREDICT_DIR,
    aligned_dir: str | Path = ALIGNED_DIR,
) -> dict[str, Any]:
    rgb_image_path = Path(rgb_image_path)
    output_dir = Path(output_dir)
    aligned_dir = Path(aligned_dir)

    aligned_img = process_rgb_for_alignment(rgb_image_path)
    aligned_dir.mkdir(parents=True, exist_ok=True)
    aligned_path = aligned_dir / f"{rgb_image_path.stem}.png"
    aligned_img.save(aligned_path)

    model, device, checkpoint_path = load_model()
    tensor = _transform()(aligned_img.convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        pred_thermal = model(tensor, None, None, None)

    output_path = output_dir / f"{rgb_image_path.stem}.png"
    pred_uint8 = _save_pred_tensor(pred_thermal[0], output_path)
    preview_path = _save_thermal_preview(output_path, output_dir / f"{rgb_image_path.stem}_thermal_preview.png")
    pred_norm = pred_uint8.astype(np.float32) / 255.0

    return {
        "aligned_rgb_path": str(aligned_path),
        "thermal_image_path": str(output_path),
        "thermal_preview_path": str(preview_path),
        "checkpoint_path": str(checkpoint_path),
        "thermal_data": {
            "min_temp_c": round(28.0 + float(pred_norm.min()) * 20.0, 1),
            "max_temp_c": round(28.0 + float(pred_norm.max()) * 20.0, 1),
            "mean_temp_c": round(28.0 + float(pred_norm.mean()) * 20.0, 1),
            "hotspot_regions": _hotspot_regions(pred_uint8),
        },
    }
