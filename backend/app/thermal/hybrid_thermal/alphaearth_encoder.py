import torch
import torch.nn as nn


class AlphaEarthEncoder(nn.Module):
    def __init__(self, in_channels=64, latent_dim=512, out_size=(16, 16)):
        super().__init__()
        self.out_size = out_size
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, latent_dim, 3, padding=1),
            nn.ReLU(inplace=True),
        )
        self.adaptive_pool = nn.AdaptiveAvgPool2d(out_size)

    def forward(self, x):
        x = self.stem(x)
        return self.adaptive_pool(x)


class FusionLayer(nn.Module):
    def __init__(self, rgb_dim, alphaearth_dim, fusion_type="gated"):
        super().__init__()
        self.fusion_type = fusion_type
        if fusion_type == "concat":
            self.fusion = nn.Sequential(
                nn.Conv2d(rgb_dim + alphaearth_dim, rgb_dim, 1),
                nn.ReLU(inplace=True),
            )
        elif fusion_type == "gated":
            self.gate = nn.Sequential(
                nn.Conv2d(rgb_dim + alphaearth_dim, rgb_dim, 1),
                nn.Sigmoid(),
            )
            self.fusion = nn.Conv2d(rgb_dim, rgb_dim, 1)
        else:
            raise ValueError(f"Unknown fusion type: {fusion_type}")

    def forward(self, rgb_latent, alphaearth_latent):
        combined = torch.cat([rgb_latent, alphaearth_latent], dim=1)
        if self.fusion_type == "concat":
            return self.fusion(combined)
        gate = self.gate(combined)
        return self.fusion(rgb_latent * gate)


class MetadataEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, output_dim=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, output_dim),
            nn.ReLU(inplace=True),
        )

    def forward(self, metadata):
        if torch.is_tensor(metadata):
            x = metadata.float()
            if x.dim() == 1:
                x = x.unsqueeze(0)
            return self.encoder(x)
        x = torch.as_tensor(metadata, dtype=torch.float32, device=next(self.parameters()).device)
        if x.dim() == 1:
            x = x.unsqueeze(0)
        return self.encoder(x)