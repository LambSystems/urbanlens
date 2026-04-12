import torch


def denorm_rgb(x: torch.Tensor) -> torch.Tensor:
    return (x * 0.5 + 0.5).clamp(0, 1)


def denorm_thermal(x: torch.Tensor) -> torch.Tensor:
    return (x * 0.5 + 0.5).clamp(0, 1)


def compute_psnr_torch(pred: torch.Tensor, target: torch.Tensor, eps: float = 1e-8) -> float:
    mse = torch.mean((pred - target) ** 2)
    if mse < eps:
        return float("inf")
    return float(20 * torch.log10(torch.tensor(1.0, device=pred.device)) - 10 * torch.log10(mse))


def compute_ssim_simple(pred: torch.Tensor, target: torch.Tensor, c1: float = 0.01**2, c2: float = 0.03**2) -> float:
    pred = pred.float()
    target = target.float()
    mu_x = pred.mean()
    mu_y = target.mean()
    sigma_x = pred.var(unbiased=False)
    sigma_y = target.var(unbiased=False)
    sigma_xy = ((pred - mu_x) * (target - mu_y)).mean()
    ssim = ((2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)) / ((mu_x**2 + mu_y**2 + c1) * (sigma_x + sigma_y + c2))
    return float(ssim)