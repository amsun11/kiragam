from grid_utils import Grid_Utils
import coords
from route import find_path, build_settings, calculate_stats
from cost import Cost


def get_route(start_lat, start_lon, end_lat, end_lon):


    dem = Grid_Utils("dem")
    slope = Grid_Utils("slope")

    dem.check_same_values(slope)        

    #Compute latitude/longitude into meters
    s_x,s_y = coords.longlat_to_xy(start_lon, start_lat)
    e_x, e_y = coords.longlat_to_xy(end_lon, end_lat)
    #Computer meters to array
    s_x, s_y = dem.map_to_array(s_x, s_y)
    e_x, e_y = dem.map_to_array(e_x, e_y)
    #get the files
    
    start = (s_x, s_y)
    end = (e_x, e_y)

    #Create array with all the valid value

    #Get cost array

    cost = Cost()
    cost_of_slopes = cost.slope_function(dem, slope)

    cell_width, cell_height = dem.get_cell_size()

    settings = build_settings(
        abs(cell_width),
        cost_of_slopes
    )

    path, best_cost, steps, cells_explored = find_path(cost_of_slopes, start, end, settings)
    #print("path: ", path)
    #convert array to meters
    stats = calculate_stats(path, slope)

    path_coordinates = []
    for row,col in path:
        lon, lat = coords.rowcol_to_lonlat(dem, row, col)

        path_coordinates.append({
           "longitude": lon,
            "latitude": lat 
        })
    return {
        "path": path_coordinates,
        "stats": stats,
        "total_cost": best_cost,
        "steps": steps,
        "cells_explored": cells_explored
    }




