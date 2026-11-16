# Kiragam - 3D Mars Mapping Visualization

We help Mars mission planners and researchers choose safer surface routes by turning real NASA elevation data into a 3D, risk-scored map of the paths between locations.

Built for NASA Space Apps Challenge 2026 — Interplanetary Survival Guide: Martian Map.

**Demo video:** [link]
**Live demo (if deployed):** [link]

![Screenshot](docs/screenshot.png)

## What it does

- Shows an interactive 3D Mars globe using NASA imagery.
- Lets you pick a start and end point in the Gale Crater / Mount Sharp region.
- Computes a least-cost route that avoids steep slopes, using real elevation data.
- Reports route stats: distance, max slope, mean slope, estimated travel time.
- Shows a scenario-based risk assessment (terrain risk plus an adjustable
  dust storm severity setting) with a Go / Shorten / Wait advisory.
- [Optional: overlays Curiosity's real traverse for comparison.]
- [Optional: fly-through of the planned route.]

## How it works

1. **Display:** [CesiumJS / Plotly] shows the Mars globe or terrain with NASA Mars Trek
   imagery layers. Imagery is for display only.
2. **Routing:** a Python backend loads a cropped elevation grid (DEM), computes slope,
   builds a cost grid, and finds the least-cost path between the chosen points.
3. **Risk:** [describe how the score is built from slope, roughness, terrain type,
   and the storm setting].



## Run it locally
 
### Prerequisites
 
- [Miniforge or another conda distribution](https://github.com/conda-forge/miniforge)
- Python 3.12 (installed by the environment file below)
- A modern Chrome or Edge with **WebGL enabled** (needed for the globe)
### 1. Set up the environment (once)
 
```bash
conda env create -f environment.yml
conda activate gale
```
 
No conda? You can use pip instead, but `rasterio` needs GDAL and can fail to build on very new Python versions. We tested with Python 3.12.
 
```bash
python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
 
### 2. Start the backend
 
Run from the `backend` folder (the data paths are relative to it):
 
```bash
cd backend
uvicorn app:app --reload --port 8000
```
 
- Interactive API docs: http://localhost:8000/docs
- The first request after startup is the slowest, because it loads the grids and builds the cost array.
### 3. Start the frontend
 
In a second terminal:
 
```bash
cd frontend
python -m http.server 5173
```
 
Open **http://localhost:5173**. Use exactly this address, because the backend's CORS setting allows that origin.
 
In `frontend/config.js`, set `BACKEND_URL` to `http://localhost:8000` and `USE_MOCK` to `false`.
 
### Mock mode (no backend needed)
 
[Partner: explain how to switch `USE_MOCK` on and which file in `mock/` it loads.]
 
## API
 
`POST /api/route`
 
```json
{
  "region_id": "gale",
  "start": { "lon": 137.386, "lat": -4.562 },
  "end":   { "lon": 137.492, "lat": -4.5745 }
}
```
 
(Replace with any two points inside the routing area.)
 
Response:
 
```json
{
  "path": [ { "lon": 137.386, "lat": -4.562 }, "..." ],
  "stats": {
    "distance_m": 0,
    "max_slope_deg": 0,
    "mean_slope_deg": 0,
    "est_time_hours": 0
  },
  "meta": { "mock": false }
}
```
 
Errors return HTTP 400 with a `detail` message, for example when a point is outside the routing area, sits on blocked terrain, or no route exists.
 
`max_slope_deg` is accepted in the request body but is **not used yet**. The slope limit comes from `backend/config.py`.
 
See `docs/api-contract.md` for the full contract.
## Data

| Purpose | Source | Notes |
|---|---|---|
| Globe imagery | NASA Mars Trek WMTS — [layer names] | Display only |
| Elevation (routing) | USGS Astrogeology — [product name and resolution] | Cropped to [lat/lon box] |

See `data/README.md` for how to download and recreate the cropped file.

## Limitations (please read)

- Routing only works inside the [Gale Crater] region, where we have elevation data.
- The storm advisory is **scenario-based**, not a forecast. Storm levels are
  chosen by the user, and thresholds are our own assumptions.
- Travel time uses a simplified speed assumption of [value].
- [Add anything else honest: coarse data resolution, no wheel-terrain interaction, etc.]

## Team

- Avanthika Senthil Kumar — data and routing
- Amrita Sundaram — map and interface

## Credits and acknowledgments

- Imagery and layers: NASA / JPL-Caltech, NASA Mars Trek
- Elevation data: [NASA MOLA, ESA/DLR HRSC, USGS Astrogeology Science Center — confirm exact credit lines]
- [Curiosity images, if used: NASA/JPL-Caltech/MSSS]
- Libraries: [CesiumJS, FastAPI, rasterio, scikit-image, etc.]
