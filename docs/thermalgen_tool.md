# HybridThermalGen Tool

HybridThermalGen is the RGB-to-thermal inference tool used by the agent. It is not the whole product; it is the heat-evidence generator.

## Current Tool Contract

Input:

```text
RGB image file path
optional map/location metadata
optional output name
```

Output:

```text
thermal_image_path
thermal_image_url
thermal_preview_path
thermal_preview_url
thermal_data.hotspot_regions
thermal_data.min_temp_c
thermal_data.mean_temp_c
thermal_data.max_temp_c
metadata
model_input
```

The current fast inference path is RGB-only:

```text
uses_rgb: true
uses_alphaearth: false
uses_metadata: false
```

Location, prompt, bounds, and Google Maps context should still be passed as `metadata`; the agent uses that context after thermal generation.

## Runtime Preprocessing

No dataset preprocessing is required for the app workflow. Each inference request still performs the small image prep the checkpoint needs:

```text
input RGB image
-> open as RGB
-> center-crop / align one image
-> resize to 512x640
-> normalize tensor
-> run checkpoint
-> save grayscale thermal PNG
-> save autocontrasted orange preview PNG
```

Generated intermediate/output files are written under `backend/data/hybrid_thermal/` and ignored by Git. Teammates do not need to run manifest building, train/test splitting, AlphaEarth export, or batch prealignment for the app.

## Backend API

Start FastAPI from repo root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

Run inference against an existing repo-local image:

```powershell
$body = @{
  image_path = "backend/data/hybrid_thermal/uploads/map-capture.png"
  metadata = @{
    center = @{
      lat = 38.627
      lng = -90.1994
    }
    source = "agent_tool"
  }
  output_name = "demo_471"
  allow_fallback = $false
} | ConvertTo-Json -Depth 6

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/thermal/infer/path" `
  -ContentType "application/json" `
  -Body $body
```

For frontend map screenshots, upload image bytes directly:

```text
POST /thermal/infer/upload?lat=38.627&lng=-90.1994&radius_m=120&filename=map-capture.png
```

Do not send normal inference images as base64 JSON. Upload bytes once, let the backend store the image, then pass file paths through the agent/tool layer.

## Python Tool Call

```python
from backend.app.thermal.generator import generate_thermal

result = generate_thermal(
    "backend/data/hybrid_thermal/uploads/map-capture.png",
    {
        "center": {"lat": 38.627, "lng": -90.1994},
        "source": "agent_tool",
    },
    output_path="backend/data/hybrid_thermal/Predict_Thermal/demo_471.png",
    allow_fallback=False,
)
```

## Frontend Helper

```ts
await inferThermalFromMapBlob(blob, {
  lat: selectedRegion.center.lat,
  lng: selectedRegion.center.lng,
  radius_m,
  prompt: userPrompt,
  filename: 'map-capture.png',
});
```

## Required Local Assets

For the minimal current workflow:

```text
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
```

Generated and uploaded files are recreated at runtime:

```text
backend/data/hybrid_thermal/uploads/
backend/data/hybrid_thermal/Predict_Thermal/
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
```
