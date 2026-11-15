// Set Cesium config to Mars
const MARS = Cesium.Ellipsoid.MARS ?? new Cesium.Ellipsoid(3396190, 3396190, 3396190);
Cesium.Ellipsoid.default = MARS;
console.log(MARS)

// Set viewer settings to not default to Earth
const viewer = new Cesium.Viewer("map", {
  baseLayer: false,        // skip the default Earth imagery
  sceneModePicker: false,
  baseLayerPicker: false,
  geocoder: false,          // both need Cesium's online service/token
  skyAtmosphere: false,
  moon: false
});
console.log("Cesium version:", Cesium.VERSION);

// Change default atmosphere and base color displays        // blue halo around the globe
viewer.scene.globe.showGroundAtmosphere = false;  // blue haze on the surface
viewer.scene.fog.enabled = false;                 // distance haze (optional)
viewer.scene.globe.baseColor = Cesium.Color.fromCssColorString("#8a4b2d"); // rusty color where there's no imagery yet

// Gale Crater bounding box (slightly padded around your region so mosaics don't clip), reassess when backend integrates
const galeBounds = Cesium.Rectangle.fromDegrees(136.5, -5.8, 138.5, -3.5);
const startRegion = Cesium.Rectangle.fromDegrees(137.124, -5.099, 137.681, -4.130);

// Set start view to Gale Crater
viewer.camera.setView({
  destination: Cesium.Cartesian3.fromDegrees(137.40, -4.61, 100000, MARS)
});

// Helper to keep a consistent rusty tint across all imagery layers
function applyRustTint(layer, brightness = 1.0, contrast = 1.0) {
  layer.saturation = 0;         // Strip any false-color elevation rainbow from MOLA
  layer.alpha = 1;          // Let #8a4b2d globe.baseColor show through
  layer.brightness = brightness;
  layer.contrast = contrast;
}

// TODO: Imagery layers (MarsTrek WMTS)
// Layer 1: Whole planet topographical layer
const marsProvider = new Cesium.WebMapTileServiceImageryProvider({
  url: "https://trek.nasa.gov/tiles/Mars/EQ/Mars_MOLA_blend200ppx_HRSC_ClrShade_clon0dd_200mpp_lzw/1.0.0/default/default028mm/{z}/{y}/{x}.jpg",
  layer: "Mars_MOLA_blend200ppx_HRSC_ClrShade_clon0dd_200mpp_lzw",
  style: "default",
  format: "image/jpeg",                   // match the Capabilities format
  tileMatrixSetID: "default028mm",
  tilingScheme: new Cesium.GeographicTilingScheme({ ellipsoid: MARS }),
  maximumLevel: 7                         // set from the Capabilities zoom range
});
const marsLayer = viewer.imageryLayers.addImageryProvider(marsProvider);
applyRustTint(marsLayer);


// Layer 2: Curiosity roving (closer to Gale crater) CTX layer
const ctxProvider = new Cesium.WebMapTileServiceImageryProvider({
  url: "https://trek.nasa.gov/tiles/Mars/EQ/curiosity_ctx_mosaic/1.0.0/default/default028mm/{z}/{y}/{x}.png",
  layer: "curiosity_ctx_mosaic",
  style: "default",
  format: "image/png",                   // match the Capabilities format
  tileMatrixSetID: "default028mm",
  tilingScheme: new Cesium.GeographicTilingScheme({ ellipsoid: MARS }),
  rectangle: galeBounds,
  maximumLevel: 14                         // set from the Capabilities zoom range
});
const ctxLayer = viewer.imageryLayers.addImageryProvider(ctxProvider);
applyRustTint(ctxLayer);

// Layer 3: Curiosity roving (closer to Gale crater) HIRISE layer
const hiriseProvider = new Cesium.WebMapTileServiceImageryProvider({
  url: "https://trek.nasa.gov/tiles/Mars/EQ/curiosity_hirise_mosaic/1.0.0/default/default028mm/{z}/{y}/{x}.png",
  layer: "curiosity_hirise_mosaic",
  style: "default",
  format: "image/png",                   // match the Capabilities format
  tileMatrixSetID: "default028mm",
  tilingScheme: new Cesium.GeographicTilingScheme({ ellipsoid: MARS }),
  rectangle: galeBounds,
  maximumLevel: 18                        // set from the Capabilities zoom range
});
const hiriseLayer = viewer.imageryLayers.addImageryProvider(hiriseProvider);
applyRustTint(hiriseLayer);

// Apply uniform rust tint to layers
function solidColorDataUrl(css) {
  const c = document.createElement("canvas");
  c.width = c.height = 4;
  const g = c.getContext("2d");
  g.fillStyle = css;
  g.fillRect(0, 0, 4, 4);
  return c.toDataURL("image/png");
}

const tintLayer = viewer.imageryLayers.addImageryProvider(
  new Cesium.UrlTemplateImageryProvider({
    url: solidColorDataUrl("#8a4b2d"),
    tilingScheme: new Cesium.GeographicTilingScheme({ ellipsoid: MARS }),
    maximumLevel: 0
  })
);
tintLayer.alpha = 0.55;

// TODO: Click handling, route drawing, panels, etc.