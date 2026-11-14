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

// Set start view to Gale Crater
viewer.camera.setView({
    //destination: Cesium.Cartesian3.fromDegrees(137.8, -5.4, 200000, MARS) gale crater
    destination: Cesium.Cartesian3.fromDegrees(137.8, -5.4, 12000000, MARS) // temporarily starting further out
});

// TODO: Imagery layers (MarsTrek WMTS)

// TODO: Click handling, route drawing, panels, etc.