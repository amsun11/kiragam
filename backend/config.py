#Files - slope map and elevation map of extent
FIVE_SLOPE_FILE = "../data/gale_slope_5m.tif"
FIVE_DEM_FILE = "../data/gale_crop_5m.tif"

#In degrees
SAFE_SLOPE_LIMIT = 20

BASE_COST = 1
SLOPE_PENALTY = .5

ALLOW_DIAGONAL = True
PREVENT_CORNER_CUTTING = True


#value marking cells with no data
DEM_NO_DATA_VAL = -32767
SLOPE_NO_DATA_VAL = -9999

#Radius measurement in meters
MARS_RADIUS_M = 3396190.0
