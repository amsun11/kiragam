import rasterio 
import numpy as np
import config 
import math

class Grid_Utils:

    def __init__(self, file):
        self.type = file.lower()
        self.shape = []
        self.transform = None
        self.crs = None
        self.data = None
        self.no_data = None
        self.parse_data(file)
        
    def parse_data(self, file):
        file = file.lower()
        print("file: ", file)
        data_to_use = None
        if file == "slope":
            data_to_use = config.FIVE_SLOPE_FILE
        elif file == "dem":
            data_to_use = config.FIVE_DEM_FILE
        else:
            raise ValueError(f"File chosen {file}, but options are either slope or DEM")
        print("data_to_use: ", data_to_use)
        with rasterio.open(data_to_use) as src:
            
        
            self.shape = [src.height, src.width,]
            self.transform = src.transform
            self.crs = src.crs
            self.no_data = src.nodata
            
            self.data = src.read(1)
    def get_cell_size(self):
        return [self.transform.a, self.transform.e]
    
    def check_same_values (self, other):
        if self.crs != other.crs or self.transform != other.transform:
            
            raise ValueError(f"CRS and/or Transform values don't match\ncrs\nself: {self.crs} other: {other.crs}\ntransform\nself: {self.transform} other: {other.transform}")
        
        shape_size = len(self.shape)
        if shape_size != len(other.shape) or shape_size != 2 or self.shape != other.shape:
            raise ValueError(f"Shapes don't match\nself: {self.shape} other: {other.shape}")
         
        return True
          
    def array_to_map(self, row, col):
        if not self.cell_in_bounds(row, col):
            raise ValueError("Row and Col index have to be in range")
        #Returns the center of the cel in map meters, as [x, y]

        cw = self.transform.a
        ch  = self.transform.e
        top_left_x = self.transform.c
        top_left_y = self.transform.f

        #TODO: Error check
        x_cord = top_left_x + float(cw*col) + float(cw/2)
        y_cord = top_left_y + float(ch*row) + float(ch/2)

        return [x_cord, y_cord]

    
    def map_to_array(self, x, y):
        if not self.map_in_bounds(x, y):
            raise ValueError("x and y coordinates have to be within range")
        #TODO: Error Handling
        #Returns the array cell for an x, y coordinate 
        cw = self.transform.a
        ch  = self.transform.e
        top_left_x = self.transform.c
        top_left_y = self.transform.f
        col = math.floor(float(x - top_left_x)/cw)
        row = math.floor(float(y-top_left_y)/ch)

        return [row, col]

    def cell_in_bounds(self, row, col):
        """True if (row, col) is a valid index into the array.
        Raises TypeError if row or col isn't an integer."""
        for name, v in (("row", row), ("col", col)):
            if isinstance(v, bool) or not isinstance(v, (int, np.integer)):
                raise TypeError(f"{name} must be an int, got {v!r} ({type(v).__name__})")

        n_rows, n_cols = self.shape  # shape is [height, width]
        return 0 <= row < n_rows and 0 <= col < n_cols


    def map_in_bounds(self, x, y):
        """True if the map point (x, y), in meters, falls inside the grid.
        Left and top edges count as inside, right and bottom edges don't
        (same convention as map_to_array's floor).
        Raises TypeError if x or y isn't a number."""
        for name, v in (("x", x), ("y", y)):
            if isinstance(v, bool) or not isinstance(v, (int, float, np.integer, np.floating)):
                raise TypeError(f"{name} must be a number, got {v!r} ({type(v).__name__})")

        if not (math.isfinite(x) and math.isfinite(y)):  # catches NaN and infinity
            return False

        col = math.floor((x - self.transform.c) / self.transform.a)
        row = math.floor((y - self.transform.f) / self.transform.e)
        return self.cell_in_bounds(row, col)

    def get_height(self, row, col):
        if self.type != "dem":
            raise ValueError("Object needs to be read from a DEM map not slopes")
        if not self.cell_in_bounds(row, col):
            raise ValueError("Row and Col out of range")
        
        height = float(self.data[row,col])
        if height == self.no_data:
            #returns the None if the elevation doesn't exist
            height = math.nan
        return height
    
    def get_slope(self, row, col):
        if self.type != "slope":
            raise ValueError("Object needs to be read from a slope map not DEM")
        if not self.cell_in_bounds(row, col):
            raise ValueError("Row and Col out of range")
        
        slope = float(self.data[row,col])
        if slope == self.no_data:
            #returns the None if the elevation doesn't exist
            slope = math.nan
        return slope

    def valid_mask(self):
        arr = np.isfinite(self.data)

        if self.no_data is not None and np.isfinite(self.no_data):
            arr &= (self.data != self.no_data)


        return arr
     

