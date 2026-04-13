from __future__ import annotations

from pathlib import Path
from PIL import Image


def center_crop(img: Image.Image, crop_w: int, crop_h: int) -> Image.Image:
    w, h = img.size
    if crop_w > w or crop_h > h:
        raise ValueError(f"Crop {crop_w}x{crop_h} larger than image size {w}x{h}")
    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    right = left + crop_w
    bottom = top + crop_h
    return img.crop((left, top, right, bottom))


def process_rgb_for_alignment(
    rgb_path: Path,
    target_rgb_crop: tuple[int, int] = (2700, 2160),
    target_size: tuple[int, int] = (640, 512),
) -> Image.Image:
    img = Image.open(rgb_path).convert("RGB")
    if img.size == (4000, 3000):
        img = center_crop(img, target_rgb_crop[0], target_rgb_crop[1])
    return img.resize(target_size, Image.BILINEAR)


def process_thermal_for_alignment(
    thermal_path: Path,
    target_size: tuple[int, int] = (640, 512),
) -> Image.Image:
    img = Image.open(thermal_path).convert("L")
    return img.resize(target_size, Image.BILINEAR)