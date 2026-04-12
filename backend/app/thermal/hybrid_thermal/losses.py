import torch
import torch.nn as nn


def denorm_thermal(x: torch.Tensor) -> torch.Tensor:
    return (x * 0.5 + 0.5).clamp(0, 1)


def compute_loss(pred_thermal: torch.Tensor, thermal: torch.Tensor) -> torch.Tensor:
    l1 = nn.L1Loss()(pred_thermal, thermal)
    mse = nn.MSELoss()(pred_thermal, thermal)
    return 0.8 * l1 + 0.2 * mse