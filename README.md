# Kiragam - 3D Mars Mapping Visualization
 
We help Mars mission planners and researchers choose safer surface routes by turning real NASA elevation data into an interactive 3D map of the paths between locations.
 
Built for NASA Space Apps Challenge 2026 - Interplanetary Survival Guide: Martian Map.
 
**Demo slides:** https://docs.google.com/presentation/d/1JV9T2ES3mUlwTVVHeVxYIgbjfse0SeeFbjDy3IfIjSQ/edit?usp=sharing
**Live demo:** https://kiragam-frontend.onrender.com/
 
> The backend is hosted on Render and may take a moment to wake up if it has been idle. If you see a connection error, wait a few seconds and try again.
 
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
python -m http.server 5173
```
 
Open **http://localhost:5173**. Use exactly this address, because the backend's CORS setting only allows that origin. (If you use a different port, add it to `allow_origins` in `backend/app.py`.)
 
In `frontend/config.js`, set `BACKEND_URL` to `http://localhost:8000` and `USE_MOCK` to `false`.
 
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
| Globe imagery | [NASA Mars Trek](https://trek.nasa.gov/mars/) WMTS: MGS MOLA and Mars Express HRSC Color Hillshade Blend (`Mars_MOLA_blend200ppx_HRSC_ClrShade_clon0dd_200mpp_lzw`); MRO CTX Curiosity Roving Site Mosaic (`curiosity_ctx_mosaic`); MRO HiRISE Curiosity Roving Site Mosaic (`curiosity_hirise_mosaic`) | Display only |
| Elevation (routing) | [USGS Astrogeology - MSL Gale Merged DEM 1m (v3)](https://astrogeology.usgs.gov/search/map/mars_msl_gale_merged_dem_1m) | 1 m, Float32, ESRI:103885. Built from HRSC, CTX and HiRISE DEMs tied to MOLA |
 
The backend reads two files from `data/`: `gale_crop_5m.tif` (the DEM cropped to the routing area, 5 m cells) and `gale_slope_5m.tif` (slope in degrees, derived from it). The 1 m crop and the full 3.6 GB USGS file are not in this repo.
 
See `data/DATA_SOURCES.md` for how to download and recreate the cropped files.
 
## Tools and libraries
 
**Backend and data**
- Python 3.12, managed with conda (conda-forge)
- [rasterio](https://rasterio.readthedocs.io/) (and GDAL) - reading the GeoTIFFs
- [NumPy](https://numpy.org/) - grid math and masks
- [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/) and [Uvicorn](https://www.uvicorn.org/) - the API
- [QGIS](https://qgis.org/) with GDAL tools - cropping, resampling and slope calculation
- Python standard library (`heapq` for the A* queue, `math`)
**Frontend**
- [CesiumJS](https://cesium.com/platform/cesiumjs/) 1.147, loaded from Cesium's CDN, with plain HTML, CSS and JavaScript
**Hosting and workflow**
- [Render](https://render.com/) - frontend and backend
- Git and GitHub
## Limitations (please read)
 
- **Routing area:** routing only works inside the Gale Crater region covered by our elevation crop (roughly 10 km by 16 km around Curiosity's landing site). Points outside it, or on blocked terrain, are rejected.
- **Travel time** uses a simplified constant walking speed of 0.417 meters/second and ignores slope, load and suit effects. Treat it as a rough estimate.
- **Longer routes take longer to calculate.** Greater distance between points means more terrain to search.
- **The slope limit is an assumption.** `SAFE_SLOPE_LIMIT` is 20 degrees, a placeholder we have not tied to a published spacesuit-mobility source. It is adjustable in `backend/config.py`, and changing it requires a backend restart.
- **Slope is only one factor.** The router cannot see rocks, loose sand, ripples or dust, and a gentle slope can still be hard to walk on.
- **5 m resolution.** The 1 m elevation data was averaged to 5 m for speed, which smooths out small obstacles and can understate steep spots.
- **Data quality:** parts of the DEM mosaic show noisy, grid-patterned slope values where different source DEMs were stitched together. Those cells are valid numbers, so they are not excluded from routing.
- **No weather, dust or radiation data** is used to compute routes.
- **Imagery is display only** and loads live from NASA Mars Trek, so the map depends on that service being available.
## Team
 
- Avanthika Senthil Kumar - data and routing
- Amrita Sundaram - map and interface
## Credits and acknowledgments
 
- Imagery and layers: NASA / JPL-Caltech, NASA Mars Trek
- Elevation data: USGS Astrogeology Science Center, MSL Gale Merged DEM, built from ESA/DLR HRSC, NASA MRO CTX and HiRISE terrain models tied to NASA MOLA elevations (see the USGS product page for the full credit line)
- Libraries: CesiumJS, FastAPI, Pydantic, Uvicorn, rasterio, NumPy
 
