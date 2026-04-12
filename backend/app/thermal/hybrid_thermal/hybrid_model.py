import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from .alphaearth_encoder import AlphaEarthEncoder, FusionLayer, MetadataEncoder
    from .thermalgen_backbone import DiffusionPipelineBackbone
    from .unet_backbone import UNetBackbone
except ImportError:
    from alphaearth_encoder import AlphaEarthEncoder, FusionLayer, MetadataEncoder
    from thermalgen_backbone import DiffusionPipelineBackbone
    from unet_backbone import UNetBackbone


class HybridThermalModel(nn.Module):
    def __init__(
        self,
        alphaearth_channels=64,
        alphaearth_latent_dim=512,
        fusion_type="gated",
        use_metadata=False,
        metadata_features=None,
        base_channels=64,
        out_size=(16, 16),
    ):
        super().__init__()
        self.unet = UNetBackbone(base_channels=base_channels)
        self.gen_base = DiffusionPipelineBackbone()
        self.alphaearth_encoder = AlphaEarthEncoder(
            in_channels=alphaearth_channels,
            latent_dim=alphaearth_latent_dim,
            out_size=out_size,
        )
        self.unet_to_latent = nn.Sequential(
            nn.Conv2d(base_channels * 8, alphaearth_latent_dim, kernel_size=1),
            nn.ReLU(inplace=True),
        )
        self.fusion = FusionLayer(
            rgb_dim=alphaearth_latent_dim,
            alphaearth_dim=alphaearth_latent_dim,
            fusion_type=fusion_type,
        )
        self.use_metadata = use_metadata
        self.metadata_dim = len(metadata_features) if metadata_features else 5
        if use_metadata:
            self.metadata_encoder = MetadataEncoder(
                input_dim=self.metadata_dim,
                output_dim=alphaearth_latent_dim,
            )
        else:
            self.metadata_encoder = None
        self.residual_head = nn.Sequential(
            nn.Conv2d(alphaearth_latent_dim, alphaearth_latent_dim // 2, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(alphaearth_latent_dim // 2, alphaearth_latent_dim // 4, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(alphaearth_latent_dim // 4, 1, kernel_size=1),
            nn.Tanh(),
        )
        self.unet_scale = nn.Parameter(torch.tensor(1.0))
        self.base_scale = nn.Parameter(torch.tensor(0.3))
        self.residual_scale = nn.Parameter(torch.tensor(0.1))

    def forward(self, rgb, alphaearth=None, metadata=None, style_id=None):
        s0, s1, s2, s3, x = self.unet.encode(rgb)
        unet_pred = self.unet.decode(s0, s1, s2, s3, x)
        base_pred = self.gen_base(rgb, style_id=style_id).to(rgb.device)

        if alphaearth is None:
            return torch.clamp(self.unet_scale * unet_pred + self.base_scale * base_pred, -1.0, 1.0)

        rgb_latent = self.unet_to_latent(x)
        alphaearth_latent = self.alphaearth_encoder(alphaearth)
        if alphaearth_latent.shape[-2:] != rgb_latent.shape[-2:]:
            alphaearth_latent = F.interpolate(alphaearth_latent, size=rgb_latent.shape[-2:], mode="bilinear", align_corners=False)
        fused_latent = self.fusion(rgb_latent, alphaearth_latent)

        if self.use_metadata and metadata is not None:
            metadata_emb = self.metadata_encoder(metadata)
            fused_latent = fused_latent + metadata_emb.unsqueeze(-1).unsqueeze(-1)

        residual = self.residual_head(fused_latent)
        residual = F.interpolate(residual, size=unet_pred.shape[-2:], mode="bilinear", align_corners=False)

        out = self.unet_scale * unet_pred + self.base_scale * base_pred + self.residual_scale * residual
        return torch.clamp(out, -1.0, 1.0)
