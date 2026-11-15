window.APP_CONFIG = {
  BACKEND_URL: (
    location.hostname === "localhost" ||
    location.hostname === "127.0.0.1"
    )
    ? "http://localhost:8000"
    : "https://kiragam.onrender.com",
  USE_MOCK: false,
  MOCK_FILE: "",
  CREDITS: [
  { text: "Imagery: NASA Mars Trek APIs", url: "https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars" },
  { text: "NASA JPL Mars Trek", url: "https://trek.nasa.gov/mars/" },
  { text: "Elevation: USGS Astrogeology (MSL Gale DEM)", url: "https://astrogeology.usgs.gov/search/map/mars_msl_gale_merged_dem_1m" },
  { text: "NASA Space Apps Challenge 2026", url: "https://www.spaceappschallenge.org/" }
],
};