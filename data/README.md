# Data - UPDATE THIS or remove/recreate as necessary

Large raw elevation files are NOT stored in this repo.

## Elevation (used for routing)
- Source: [USGS Astrogeology product name and link]
- Resolution: [e.g. 200 m per pixel]
- Region used: [lat/lon box around Gale Crater and Mount Sharp]

## How to recreate the cropped file
1. Download [file name] from [link] into `data/raw/` (this folder is git-ignored).
2. Crop it to the region above and save it as `data/crop/gale_dem.tif`.
3. [Add the exact command or script name once Person A decides.]

## Notes
- Longitude convention in this file: [0 to 360 or -180 to 180]
- Units: elevation in meters, coordinates in degrees