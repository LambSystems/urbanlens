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
from torch.utils.data import DataLoader

from config_utils import load_config
from dataset import HybridThermalDataset, get_transforms
from hybrid_model import HybridThermalModel
from losses import compute_loss
from metrics_utils import denorm_thermal, compute_psnr_torch, compute_ssim_simple


def setup_model(config):
    return HybridThermalModel(
        alphaearth_channels=config.get("alphaearth_encoder_channels", 64),
        alphaearth_latent_dim=config.get("alphaearth_latent_dim", 512),
        fusion_type=config.get("fusion_type", "gated"),
        use_metadata=config.get("use_metadata", False),
        metadata_features=config.get("metadata_features"),
        base_channels=config.get("base_channels", 64),
        out_size=tuple(config.get("hybrid_bottleneck_size", [16, 16])),
    )


def setup_optimizer(model, config):
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=float(config["learning_rate"]))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config["num_epochs"])
    return optimizer, scheduler


def train_epoch(model, dataloader, optimizer, device):
    model.train()
    total_loss = 0.0
    for batch in dataloader:
        rgb = batch["rgb"].to(device)
        thermal = batch["thermal"].to(device)
        alphaearth = batch.get("alphaearth")
        alphaearth = alphaearth.to(device) if alphaearth is not None else None
        metadata = batch.get("metadata")
        metadata = metadata.to(device) if metadata is not None else None
        style_id = batch["style_id"].to(device)
        optimizer.zero_grad()
        pred = model(rgb, alphaearth, metadata, style_id)
        loss = compute_loss(pred, thermal)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / max(len(dataloader), 1)


def validate(model, dataloader, device):
    model.eval()
    total_loss = 0.0
    val_psnr, val_ssim = [], []
    with torch.no_grad():
        for batch in dataloader:
            rgb = batch["rgb"].to(device)
            thermal = batch["thermal"].to(device)
            alphaearth = batch.get("alphaearth")
            alphaearth = alphaearth.to(device) if alphaearth is not None else None
            metadata = batch.get("metadata")
            metadata = metadata.to(device) if metadata is not None else None
            style_id = batch["style_id"].to(device)
            pred = model(rgb, alphaearth, metadata, style_id)
            loss = compute_loss(pred, thermal)
            total_loss += loss.item()
            pred_vis = denorm_thermal(pred)
            gt_vis = denorm_thermal(thermal)
            for i in range(pred.shape[0]):
                val_psnr.append(compute_psnr_torch(pred_vis[i], gt_vis[i]))
                val_ssim.append(compute_ssim_simple(pred_vis[i], gt_vis[i]))
    mean_loss = total_loss / max(len(dataloader), 1)
    mean_psnr = float(np.mean(val_psnr)) if val_psnr else float("nan")
    mean_ssim = float(np.mean(val_ssim)) if val_ssim else float("nan")
    return mean_loss, mean_psnr, mean_ssim


def main(config_path):
    config = load_config(config_path, PROJECT_ROOT)
    device_name = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    if device_name == "cuda" and not torch.cuda.is_available():
        device_name = "cpu"
    device = torch.device(device_name)

    alphaearth_transform = get_transforms(config)
    augmentations = config.get("augmentations", {})

    train_dataset = HybridThermalDataset(
        config["manifest_file"],
        split="train",
        alphaearth_transform=alphaearth_transform,
        use_metadata=config.get("use_metadata", False),
        root_dir=config["dataset_dir"],
        require_alphaearth=True,
        augmentations=augmentations,
    )

    val_dataset = HybridThermalDataset(
        config["manifest_file"],
        split="val",
        alphaearth_transform=alphaearth_transform,
        use_metadata=config.get("use_metadata", False),
        root_dir=config["dataset_dir"],
        require_alphaearth=True,
        augmentations=augmentations,
    )

    train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=config.get("eval_batch_size", config["batch_size"]), shuffle=False, num_workers=0)

    model = setup_model(config).to(device)
    optimizer, scheduler = setup_optimizer(model, config)

    checkpoint_dir = Path(config["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    best_loss = float("inf")
    best_psnr = -float("inf")

    for epoch in range(config["num_epochs"]):
        print(f"Epoch {epoch + 1}/{config['num_epochs']}")
        train_loss = train_epoch(model, train_loader, optimizer, device)
        val_loss, val_psnr, val_ssim = validate(model, val_loader, device)
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val PSNR: {val_psnr:.4f} | Val SSIM: {val_ssim:.4f}")
        scheduler.step()

        state = {
            "epoch": epoch + 1,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_psnr": val_psnr,
            "val_ssim": val_ssim,
            "config": config,
        }
        torch.save(state, checkpoint_dir / "latest.pth")
        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(state, checkpoint_dir / "best_loss.pth")
            print("Saved best_loss.pth")
        if val_psnr > best_psnr:
            best_psnr = val_psnr
            torch.save(state, checkpoint_dir / "best_psnr.pth")
            print("Saved best_psnr.pth")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()
    main(args.config)
