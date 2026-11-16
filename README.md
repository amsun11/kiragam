# Kiragam - 3D Mars Mapping Visualization

We help Mars mission planners and researchers choose safer surface routes by turning real NASA elevation data into a multidimensional, interactive map of the paths between locations.

Built for NASA Space Apps Challenge 2026 — Interplanetary Survival Guide: Martian Map.

**Demo slides:** https://docs.google.com/presentation/d/1JV9T2ES3mUlwTVVHeVxYIgbjfse0SeeFbjDy3IfIjSQ/edit?usp=sharing 

**Live demo (if deployed):** https://kiragam-frontend.onrender.com/

## What it does

- Shows an interactive 3D Mars globe using NASA imagery layers.
- Lets you pick a start and end point in the Gale Crater / Mount Sharp region.
- Computes a least-cost route that avoids steep slopes, using real elevation data.
- Reports route stats: distance, max slope, mean slope, estimated travel time.

## How it works

1. **Display (frontend):** CesiumJS draws a Mars globe (Mars ellipsoid, radius 3,396,190 m) with NASA Mars Trek WMTS imagery. Imagery is for display only. Routing never reads it.
2. **Elevation prep (done once, offline):** the USGS Gale DEM is cropped, resampled to 5 m, and converted to a slope grid in degrees (see [Data](#data)).
3. **Cost grid (`backend/cost.py`):** each 5 m cell gets a cost of `BASE_COST + SLOPE_PENALTY * slope`. Cells are **blocked** if their slope is above `SAFE_SLOPE_LIMIT` or if the slope is unknown (this includes the one-cell border of the crop).
4. **Routing (`backend/route.py`):** A* search over the cost grid with 8-direction movement.
   - Step cost = step length (5 m straight, about 7.07 m diagonal) times the average cost of the two cells.
   - The heuristic is octile distance times the cheapest cost in the grid, so it never overestimates.
   - Diagonal moves are not allowed to cut between two blocked cells.
5. **Coordinates (`backend/coords.py`, `backend/grid_utils.py`):** the API takes longitude/latitude, converts to the DEM's projected meters (ESRI:103885, Mars 2000 Equidistant Cylindrical, sphere), then to grid cells, and converts the route back to longitude/latitude.
6. **API (`backend/app.py`):** FastAPI exposes `POST /api/route`. The grids and cost array are loaded once and reused for every request (`backend/pipeline.py`).

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
python -m http.server [your local host frontend server]
```
 
Open your local backend server **http://localhost:XXXX**. Use exactly this address, because the backend's CORS setting allows that origin.
 
In `frontend/config.js`, set `BACKEND_URL` to `http://localhost:XXXX` and `USE_MOCK` to `false`.
 
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
 
## Data

| Purpose | Source | Notes |
|---|---|---|
| Globe imagery | NASA Mars Trek WMTS — MGS MOLA and Mars Express HRSC, Color Hillshade Blend, MRO HiRISE, Curiosity Roving Site Mosaic, MRO CTX, Curiosity Roving Site Mosaic | Display only | Elevation (routing) | USGS Astrogeology — [product name and resolution] | Cropped to [lat/lon box] |

See `data/README.md` for how to download and recreate the cropped file.

## Limitations (please read)

- Routing only works inside the [Gale Crater] region, where we have elevation data.
- Travel time uses a simplified speed assumption of [0.417 meters/second].
- Increased distance between points may take longer time to calculate route.

## Team

- Avanthika Senthil Kumar — data and routing
- Amrita Sundaram — map and interface

## Credits and acknowledgments

- Imagery and layers: NASA / JPL, NASA Mars Trek
- Elevation data: [NASA MOLA, ESA/DLR HRSC, USGS Astrogeology Science Center — confirm exact credit lines]
- [Curiosity images, if used: NASA/JPL-Caltech/MSSS]
- Libraries: [CesiumJS, FastAPI, rasterio, scikit-image, etc.]
