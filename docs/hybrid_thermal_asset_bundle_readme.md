# hybrid_thermal Checkpoint Bundle

This zip contains the local checkpoints needed to run the `hybrid_thermal` inference notebook and the ThermalGen API tool.

## Where To Unzip

Unzip this bundle at the root of the UrbanLens repository.

After unzipping, these paths should exist:

```text
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
backend/models/hybrid_thermal/checkpoints/best_loss.pth
backend/models/hybrid_thermal/checkpoints/latest.pth
```

## Setup

From the UrbanLens repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-full.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name urbanlens --display-name "UrbanLens .venv"
```

Then open:

```text
notebooks/hybrid_thermal_inference.ipynb
```

Select the `UrbanLens .venv` kernel and run all cells.

Set `INPUT_IMAGE` in the notebook to any local RGB image. Frontend/API uploads are stored under:

```text
backend/data/hybrid_thermal/uploads/
```

## Expected Outputs

Expected generated outputs:

```text
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/Predict_Thermal/
```

The backend returns:

- `thermal_image_path`: grayscale model output
- `thermal_preview_path`: autocontrasted orange preview for display
- `thermal_preview_url`: browser-loadable preview served by FastAPI from `/thermal-assets/...`

For app/API usage, see:

```text
docs/thermalgen_tool.md
```

## Notes

These checkpoint assets are intentionally not committed to Git.
