# hybrid_thermal Asset Bundle

This zip contains the local data and checkpoints needed to run the `hybrid_thermal` inference notebook.

## Where To Unzip

Unzip this bundle at the root of the UrbanLens repository.

After unzipping, these paths should exist:

```text
backend/data/hybrid_thermal/RGB_to_thermal_dataset/
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
backend/models/hybrid_thermal/checkpoints/best_loss.pth
backend/models/hybrid_thermal/checkpoints/latest.pth
```

## Setup

From the UrbanLens repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name urbanlens --display-name "UrbanLens .venv"
```

Then open:

```text
notebooks/hybrid_thermal_inference.ipynb
```

Select the `UrbanLens .venv` kernel and run all cells.

## Quick CLI Test

```powershell
.\.venv\Scripts\python.exe backend\app\thermal\hybrid_thermal\prealign_test_rgb_thermal.py --limit 1
.\.venv\Scripts\python.exe backend\app\thermal\hybrid_thermal\inference.py --limit 1
```

Expected generated outputs:

```text
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/Predict_Thermal/
```

The backend returns:

- `thermal_image_path`: grayscale model output
- `thermal_preview_path`: autocontrasted orange preview for display

## Notes

These assets are intentionally not committed to Git. Keep dataset licensing and usage restrictions in mind before resharing.
