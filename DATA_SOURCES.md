# Data Sources and Processing

**Visual Mars Trek Imagery Layer Data**
**Source:** https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars#description **from** https://trek.nasa.gov/mars/
- **Layer 1:** MGS MOLA and Mars Express HRSC, Color Hillshade Blend
- **Layer 2:** MRO HiRISE, Curiosity Roving Site Mosaic
- **Layer 3:** MRO CTX, Curiosity Roving Site Mosaic
  
**Usage:** This data is used to layer the visual texture and terrain of whole planet of Mars (layer 1) and the region around Gale Crater (Layers 2 and 3).

## Original Dataset

The terrain data used in this project comes from the **Mars MSL Gale Merged Digital Elevation Model (DEM), Version 3**

- **Dataset:** `MSL_Gale_DEM_Mosaic_1m_v3.tif`
- **Source:** [USGS Astrogeology](https://astrogeology.usgs.gov/search/map/mars_msl_gale_merged_dem_1m)
- **Original resolution:** 1 meter per pixel
- **Format:** GeoTIFF (.tif)
- **Geographic region:** Gale Crater, Mars

A Digital Elevation Model (DEM) represents the elevation of terrain using a raster grid, where each cell contains an elevation value. This dataset provides topographic information about Gale Crater, allowing the project to analyze changes in elevation and identify potentially hazardous terrain.

## Data Preprocessing

The original DEM was processed using **QGIS**, an open-source Geographic Information System (GIS) application.

### 1. Resampling Elevation Data

The original dataset had a spatial resolution of 1 × 1 meters. Using QGIS, the raster was resampled to a resolution of **5 × 5 meters per cell**.

This was done to reduce the computational complexity of pathfinding. Since the routing algorithm evaluates terrain cells to determine optimal paths, using a lower-resolution grid reduces the number of nodes that must be processed while preserving useful terrain information.

### 2. Slope Calculation

Using the processed elevation data, an additional slope raster was generated in QGIS.

The slope raster represents the steepness of the terrain at each cell. 
## Use in Pathfinding

The project uses two processed raster datasets:

| Dataset | Description | Purpose |
|---|---|---|
| Elevation DEM (5 m) | Elevation values across the terrain | Calculate elevation changes and terrain-related movement costs |
| Slope raster (5 m) | Terrain steepness in degrees | Identify unsafe terrain and restrict traversal based on slope limits |

Together, these datasets allow the routing algorithm to evaluate both terrain elevation and steepness when calculating paths across Gale Crater.

Using 5-meter cells provides a practical balance between computational efficiency and terrain detail for grid-based pathfinding.
