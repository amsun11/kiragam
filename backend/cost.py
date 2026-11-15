import config
import grid_utils as gu
import numpy as np
import math
class Cost:
    def __init__(self):
        print(True)
        self.slope = None
        self.get_slope()



    def get_slope(self):
        self.slope = config.SAFE_SLOPE_LIMIT
        


    def cost_mask(self, dem, slope):


        if not dem.check_same_values(slope):
            raise ValueError("Dem and Slope graphs are not aligned")
        
        valid_mask = slope.valid_mask()
        #arr = np.where(valid_mask, slope, False)

        mask = (slope.data<= self.slope) & valid_mask

        return mask
    
    def slope_function(self, dem, slope):
        mask = self.cost_mask(dem, slope)
        cost_array = np.full(slope.data.shape, np.inf, dtype=float)
        cost_array[mask] = config.BASE_COST + slope.data[mask] * config.SLOPE_PENALTY

        return cost_array
    

