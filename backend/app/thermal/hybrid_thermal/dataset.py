from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import rasterio
import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import Dataset
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as TF


class AlphaEarthTransform:
    def __init__(self, size=(640, 512)):
        self.size = size

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        x = x.unsqueeze(0)
        x = F.interpolate(x, size=self.size, mode="bilinear", align_corners=False)
        return x.squeeze(0)


class HybridThermalDataset(Dataset):
    def __init__(
        self,
        manifest_path,
        split="train",
        alphaearth_transform=None,
        use_metadata=False,
        root_dir=None,
        require_alphaearth=True,
        augmentations=None,
    ):
        self.alphaearth_transform = alphaearth_transform
        self.use_metadata = use_metadata
        self.require_alphaearth = require_alphaearth
        self.augmentations = augmentations or {}
        self.root_dir = Path(root_dir) if root_dir is not None else Path(__file__).resolve().parents[1] / "resources"
        self.split = split
        self.size = tuple(self.augmentations.get("resize", [640, 512]))
        self.train_mode = split == "train"

        self.samples = []
        with open(manifest_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                sample = json.loads(line)
                if sample.get("split", "train") != split:
                    continue
                rgb_ok = "rgb_path" in sample
                thermal_ok = "thermal_path" in sample
                alpha_ok = ("alphaearth_path" in sample and sample["alphaearth_path"]) or not require_alphaearth
                if rgb_ok and thermal_ok and alpha_ok:
                    self.samples.append(sample)

        if not self.samples:
            raise ValueError(f"No samples found for split={split!r} in {manifest_path}")

    def __len__(self):
        return len(self.samples)

    def _resolve(self, relative_path: str) -> Path:
        path = Path(relative_path)
        if path.is_absolute():
            return path
        candidate = self.root_dir / path
        if candidate.exists():
            return candidate
        project_relative = self.root_dir.parent / path
        if path.parts and path.parts[0] == self.root_dir.name and project_relative.exists():
            return project_relative
        return candidate

    def load_alphaearth_tif(self, tif_path: Path) -> torch.Tensor:
        with rasterio.open(tif_path) as src:
            arr = src.read().astype(np.float32)
        arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
        if arr.size > 0:
            arr_min = arr.min(axis=(1, 2), keepdims=True)
            arr_max = arr.max(axis=(1, 2), keepdims=True)
            denom = np.where((arr_max - arr_min) < 1e-6, 1.0, arr_max - arr_min)
            arr = (arr - arr_min) / denom
        return torch.from_numpy(arr)

    def build_metadata_vector(self, sample: dict) -> torch.Tensor:
        values = [
            float(sample.get("lat", 0.0)),
            float(sample.get("lon", 0.0)),
            float(sample.get("month", 0.0)),
            float(sample.get("day_of_year", 0.0)),
            float(sample.get("hour", 0.0)),
        ]
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
            if key in sample:
                values.append(float(sample.get(key, 0.0)))
        return torch.tensor(values, dtype=torch.float32)

    def _paired_preprocess(self, rgb_pil: Image.Image, thermal_pil: Image.Image):
        rgb_pil = TF.resize(rgb_pil, self.size, interpolation=InterpolationMode.BILINEAR, antialias=True)
        thermal_pil = TF.resize(thermal_pil, self.size, interpolation=InterpolationMode.BILINEAR, antialias=True)

        if self.train_mode:
            if self.augmentations.get("horizontal_flip", False) and random.random() < 0.5:
                rgb_pil = TF.hflip(rgb_pil)
                thermal_pil = TF.hflip(thermal_pil)

            crop_scale = self.augmentations.get("paired_crop_scale", 0.92)
            if 0.0 < crop_scale < 1.0:
                h, w = self.size
                crop_h = max(1, int(h * crop_scale))
                crop_w = max(1, int(w * crop_scale))
                max_top = max(0, h - crop_h)
                max_left = max(0, w - crop_w)
                top = random.randint(0, max_top) if max_top > 0 else 0
                left = random.randint(0, max_left) if max_left > 0 else 0
                rgb_pil = TF.crop(rgb_pil, top, left, crop_h, crop_w)
                thermal_pil = TF.crop(thermal_pil, top, left, crop_h, crop_w)
                rgb_pil = TF.resize(rgb_pil, self.size, interpolation=InterpolationMode.BILINEAR, antialias=True)
                thermal_pil = TF.resize(thermal_pil, self.size, interpolation=InterpolationMode.BILINEAR, antialias=True)

        rgb = TF.to_tensor(rgb_pil)
        thermal = TF.to_tensor(thermal_pil)
        rgb = TF.normalize(rgb, mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        thermal = TF.normalize(thermal, mean=[0.5], std=[0.5])
        return rgb, thermal

    def __getitem__(self, idx):
        sample = self.samples[idx]
        rgb_path = self._resolve(sample["rgb_path"])
        thermal_path = self._resolve(sample["thermal_path"])
        rgb_pil = Image.open(rgb_path).convert("RGB")
        thermal_pil = Image.open(thermal_path).convert("L")
        rgb, thermal = self._paired_preprocess(rgb_pil, thermal_pil)

        out = {
            "rgb": rgb,
            "thermal": thermal,
            "sample_id": sample.get("sample_id", str(idx)),
            "style_id": torch.tensor(sample.get("style_id", 0), dtype=torch.long),
        }

        if "alphaearth_path" in sample and sample["alphaearth_path"]:
            alphaearth_path = self._resolve(sample["alphaearth_path"])
            alphaearth = self.load_alphaearth_tif(alphaearth_path)
            if self.alphaearth_transform:
                alphaearth = self.alphaearth_transform(alphaearth)
            out["alphaearth"] = alphaearth
        elif self.require_alphaearth:
            raise ValueError(f"Sample {out['sample_id']} missing alphaearth_path")

        if self.use_metadata:
            out["metadata"] = self.build_metadata_vector(sample)

        return out


def get_transforms(config):
    size = tuple(config.get("augmentations", {}).get("resize", [640, 512]))
    return AlphaEarthTransform(size=size)