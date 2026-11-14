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

The frontend and backend communicate through the API described in
`docs/api-contract.md`.

## Run it

### Prerequisites
- Python [version], [any other tools]
- A modern version of Chrome

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API docs appear at http://localhost:8000/docs

### Frontend
```bash
cd frontend
# [e.g. python -m http.server 5500]
```
Open http://localhost:5500

### Mock mode (no backend needed)
[Explain how to switch the frontend to the hardcoded response in `mock/route-response.json`.]

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
