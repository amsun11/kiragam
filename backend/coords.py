import math
import config

def longlat_to_xy(long_deg, lat_deg):
    # arc length = radius x angle (normalized)
    lon = ((long_deg + 180) % 360) - 180
    return config.MARS_RADIUS_M * math.radians(lon), config.MARS_RADIUS_M * math.radians(lat_deg)

def xy_to_longlat(x_m, y_m):
    # lon = x / k
    # lat = y / k
    return math.degrees(x_m / config.MARS_RADIUS_M), math.degrees(y_m / config.MARS_RADIUS_M)

def lonlat_to_rowcol(grid, lon_deg, lat_deg):
    x, y = longlat_to_xy(lon_deg, lat_deg)
    return grid.map_to_array(x, y)

def rowcol_to_lonlat(grid, row, col):
    x, y = grid.array_to_map(row, col)
    return xy_to_longlat(x, y)