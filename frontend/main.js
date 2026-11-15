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
  moon: false,
  animation: false,
  timeline: false
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
// Connect to buttons
const cfg = window.APP_CONFIG;
const deg = Cesium.Math.toDegrees;
const START_VIEW = Cesium.Cartesian3.fromDegrees(137.40, -4.61, 100000, MARS);
const statusEl = document.getElementById("status");
const statsEl = document.getElementById("stats");
const findBtn = document.getElementById("findBtn");
const DEMO = { start: { lon: 137.44, lat: -4.59 }, end: { lon: 137.40, lat: -4.70 } };
const setStatus = (msg, isError = false) => {
  statusEl.textContent = msg;
  statusEl.classList.toggle("error", isError);
};

// turns number into text
const fmt = (v, digits = 1) => (Number.isFinite(v) ? v.toFixed(digits) : "n/a");

function clearRoute() {
  if (routeEntity) { viewer.entities.remove(routeEntity); routeEntity = null; }
  statsEl.innerText = "";
}

function validateRoute(data) {
  const ok = data && Array.isArray(data.path) && data.path.length >= 2 &&
    data.path.every((p) => Number.isFinite(p.lon) && Number.isFinite(p.lat));
  if (!ok) throw Object.assign(new Error("The route data was incomplete."), { code: "bad_response" });
}

// error handling messaging to the user
function friendlyError(err) {
  if (err.code === "no_route") return "No route found. Try different points or a higher slope limit.";
  if (err.code === "out_of_region") return "That point is outside the routing area. Pick points inside the white box.";
  if (err.code === "invalid_point") return "One of the points can't be used for routing. Try moving it a little.";
  if (err.code === "bad_response") return err.message;
  if (err.name === "TimeoutError") return "The route service took too long. Try again.";
  if (err.name === "SyntaxError") return "The route service sent an unreadable response.";
  if (err instanceof TypeError) return "Can't reach the route service. Check that the backend is running.";
  return "Something went wrong: " + err.message;
}

/* 
    start: starting coordinates, connects to backend
    end: destination coordinates, connects to backend
    startMarker: green pin drawn on globe
    endMarker: red pin drawn on globe
    routeEntity: route line drawn on globe
*/
let start = null, end = null, startMarker = null, endMarker = null, routeEntity = null;
// Region outline - clickable area
const r = startRegion;
viewer.entities.add({
  polyline: {
    positions: Cesium.Cartesian3.fromDegreesArray([
      deg(r.west), deg(r.south), deg(r.east), deg(r.south),
      deg(r.east), deg(r.north), deg(r.west), deg(r.north),
      deg(r.west), deg(r.south)
    ], MARS),
    width: 2,
    material: Cesium.Color.WHITE
  }
});

function inRegion(point) {   // point = { lon, lat } in degrees
  return Cesium.Rectangle.contains(
    startRegion,
    Cesium.Cartographic.fromDegrees(point.lon, point.lat)
  );
}

// Markers and clicks
function addMarker(pt, color) {
    return viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(pt.lon, pt.lat, 0, MARS),
        point: { pixelSize: 12, color, outlineColor: Cesium.Color.WHITE, outlineWidth: 2,
            disableDepthTestDistance: Number.POSITIVE_INFINITY 
        }
    });
}

function clearAll() {
  [startMarker, endMarker, routeEntity].forEach((e) => e && viewer.entities.remove(e));
  start = end = startMarker = endMarker = routeEntity = null;
  statsEl.innerText = "";
  findBtn.disabled = true;
  setStatus("Click inside the white box to set a start point.");
}

// Demo - uses pre-set points to show
function placePoints(a, b) {
  clearAll();
  if (!inRegion(a) || !inRegion(b)) { setStatus("Demo points are outside the region."); return; }
  start = a; startMarker = addMarker(a, Cesium.Color.LIME);
  end = b;   endMarker = addMarker(b, Cesium.Color.RED);
  findBtn.disabled = false;
  setStatus("Press Find route.");
}
document.getElementById("demoBtn").onclick = () => placePoints(DEMO.start, DEMO.end);

const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction((click) => {
  const cart = viewer.camera.pickEllipsoid(click.position, MARS);
  if (!cart) return;  // clicked empty space
  const c = Cesium.Cartographic.fromCartesian(cart, MARS);
  if (!Cesium.Rectangle.contains(startRegion, c)) {
    setStatus("Routing only works inside the white box.");
    return;
  }
  const p = { lon: deg(c.longitude), lat: deg(c.latitude) };
  if (start && end) clearAll();   // third click starts over
  if (!start) {
    start = p; startMarker = addMarker(p, Cesium.Color.LIME);
    setStatus("Now click an end point.");
  } else {
    end = p; endMarker = addMarker(p, Cesium.Color.RED);
    findBtn.disabled = false;
    setStatus("Press Find route.");
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

// Route request - remove at backend integration or keep as mock backup
// Linear interpolation, draws a straight line between 2 clicked markers
function fakePath(a, b, n) {
  return Array.from({ length: n }, (_, i) => {
    const t = i / (n - 1);
    return { lon: a.lon + (b.lon - a.lon) * t, lat: a.lat + (b.lat - a.lat) * t, height_m: 0 };
  });
}

async function requestRoute() {
  const opts = { signal: AbortSignal.timeout(10000) };
  // if mock data
  const res = cfg.USE_MOCK
    ? await fetch("../mock/" + (cfg.MOCK_FILE || "route-response.json"), opts)
    // if backend
    : await fetch(cfg.BACKEND_URL + "/api/route", {
        ...opts,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ region_id: "gale", start, end, max_slope_deg: 20 })
      });

  const data = await res.json();                 // throws SyntaxError if not JSON
  if (data.error || !res.ok) {
    throw Object.assign(new Error(data.message || data.detail || "Route request failed"), { code: data.error });
  }
  if (cfg.USE_MOCK) {
    if (!cfg.MOCK_FILE) data.path = fakePath(start, end, 40);   // follow the clicked points
    data.meta = { ...(data.meta || {}), mock: true };
  }
  validateRoute(data);
  return data;
}

// Draw route and stats
function drawRoute(data) {
  if (routeEntity) viewer.entities.remove(routeEntity);
  // fixed 50 m height: the globe has no terrain yet, so real heights would sit underground
  const flat = data.path.flatMap((pt) => [pt.lon, pt.lat, 50]);
  routeEntity = viewer.entities.add({
    // draw cyan line as route
    polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights(flat, MARS),
                width: 4, material: Cesium.Color.CYAN }
  });
  // moves camera through route
  viewer.flyTo(routeEntity, { duration: 1.5 });
}

// read data from route given from backend and display stats
function showStats(data) {
  // doesn't crash sim if there is no stats sent from backend
  const s = data.stats || {};
  statsEl.innerText = [
    `Distance: ${fmt(s.distance_m / 1000)} km`,
    `Max slope: ${fmt(s.max_slope_deg)}°`,
    `Mean slope: ${fmt(s.mean_slope_deg)}°`,
    `Est. time: ${fmt(s.est_time_hours)} h`,
    data.meta && data.meta.mock ? "(demo data)" : ""
  ].join("\n");
}

// Create credits/attributions to be displayed
const creditsEl = document.getElementById("credits");

function renderCredits(items) {
 creditsEl.replaceChildren();
  if (!Array.isArray(items)) { creditsEl.textContent = items || ""; return; }   // old string format still works
  items.forEach((item, i) => {
    if (i > 0) creditsEl.append(" · ");
    if (item.url) {
      const a = document.createElement("a");
      a.href = item.url;
      a.textContent = item.text;
      a.target = "_blank";                  // open in a new tab
      a.rel = "noopener noreferrer";        // standard safety for links that open new tabs
      creditsEl.append(a);
    } else {
      creditsEl.append(item.text);
    }
  });
}
renderCredits(cfg.CREDITS);

// Buttons
findBtn.addEventListener("click", async () => {
  findBtn.disabled = true;
  clearRoute()
  setStatus("Finding route…");
  try {
    const data = await requestRoute();
    drawRoute(data);
    showStats(data);
    setStatus("Route found.");
  } catch (err) {
    setStatus(friendlyError(err), true);
  } finally {
    // enable/disable find route btn based on whether both points still exist
    findBtn.disabled = !(start && end);
  }
});
document.getElementById("clearBtn").onclick = clearAll;
document.getElementById("resetBtn").onclick = () => viewer.camera.flyTo({ destination: START_VIEW });
