import numpy as np
import heapq
import math
import config

STRAIGHT_MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONAL_MOVES = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def neighbors(cost, row, col, settings):
    
    if not usable(cost, row, col):
        return []                      

    x, y = cost.shape                  
    cell_size = settings["cell_size"]
    valid_neighbors = []

    for i in STRAIGHT_MOVES:
        new_row = row + i[0]
        new_col = col + i[1]

        
        if new_row < 0 or new_row >= x:
            continue
        if new_col < 0 or new_col >= y:
            continue

        if usable(cost, new_row, new_col):
            valid_neighbors.append((new_row, new_col, cell_size))

    if settings["allow_diagonal"]:
        step_length = cell_size * math.sqrt(2)
        for i in DIAGONAL_MOVES:
            new_row = row + i[0]
            new_col = col + i[1]

            if new_row < 0 or new_row >= x:
                continue
            if new_col < 0 or new_col >= y:
                continue

            if not usable(cost, new_row, new_col):
                continue

            
            if settings["prevent_corner_cutting"]:
                if not usable(cost, new_row, col) or not usable(cost, row, new_col):  #Used Claude AI to come up with block to prevent cutting corners
                    continue

            valid_neighbors.append((new_row, new_col, step_length))

    return valid_neighbors


def usable(cost, row, col):
    return math.isfinite(cost[row, col])

#Claude AI came up with this method to help with metadata 
def build_settings(cell_size, cost):
    finite = np.isfinite(cost)
    if not finite.any():
        raise ValueError("Cost grid has no usable cells")

    min_cost = float(cost[finite].min())          
    if min_cost <= 0:
        raise ValueError(f"Costs must be positive, but the minimum is {min_cost}")

    return {
        "cell_size": abs(cell_size),
        "allow_diagonal": config.ALLOW_DIAGONAL,
        "prevent_corner_cutting": config.PREVENT_CORNER_CUTTING,
        "minimum_cost": min_cost,
    }

def step_cost(cost, from_cell, to_cell, length):
    row_one, col_one = from_cell
    row_two, col_two = to_cell
    return length*(cost[row_one, col_one] + cost[row_two, col_two]) / 2.0

def heuristic(curr_cell, goal_cell, settings):

    g_row, g_col = goal_cell
    c_row, c_col = curr_cell

    row_dist = abs(g_row-c_row)
    col_dist = abs(g_col-c_col)
    cell_size = settings["cell_size"]
    total_dist = 0
    if settings["allow_diagonal"]:
        diagonal = min(row_dist, col_dist)
        straight = max(row_dist, col_dist) - diagonal
        total_dist = diagonal * cell_size * math.sqrt(2) + straight*cell_size
        #Claude came up with a more time-sensitive way to get the total_dist then I had
    else:
        total_dist = (row_dist + col_dist) * cell_size
    
    return total_dist * settings["minimum_cost"]


def reconstruct(parent_row, parent_col, start, goal):

    start = tuple(start)                  
    row, col = goal
    path = [(row, col)]
    max_steps = parent_row.size           

    while (row, col) != start:
        if len(path) > max_steps:
            raise ValueError("Parent chain loops back on itself")

        p_row = int(parent_row[row, col])
        p_col = int(parent_col[row, col])

        if p_row == -1 or p_col == -1:
            raise ValueError(f"Broken parent chain at cell {(row, col)}") 

        row, col = p_row, p_col
        path.append((row, col))

    path.reverse()
    return path

def find_path(cost, start, goal, settings):
    start = (int(start[0]), int(start[1]))
    goal = (int(goal[0]), int(goal[1]))
    s_row, s_col = start
    g_row, g_col = goal
    n_rows, n_cols = cost.shape

    #Claude AI came up with these error checks
    if not (0 <= s_row < n_rows and 0 <= s_col < n_cols):
        raise ValueError(f"Starting point {start} is out of range for a grid of shape {cost.shape}")
    if not (0 <= g_row < n_rows and 0 <= g_col < n_cols):
        raise ValueError(f"Ending point {goal} is out of range for a grid of shape {cost.shape}")

    if not usable(cost, s_row, s_col):
        raise ValueError(f"Starting point {start} is blocked")
    if not usable(cost, g_row, g_col):
        raise ValueError(f"Ending point {goal} is blocked")

    if start == goal:
        return ([start], 0.0, 0, 0)

    best_cost = np.full(cost.shape, np.inf)         
    best_cost[s_row, s_col] = 0.0
    parent_row = np.full(cost.shape, -1, dtype=np.int32)
    parent_col = np.full(cost.shape, -1, dtype=np.int32)
    processed = np.zeros(cost.shape, dtype=bool)     

    tie_breaker = 0
    cells = []                                      
    heapq.heappush(cells, (heuristic(start, goal, settings), tie_breaker, s_row, s_col))

    cells_explored = 0
    found = False

    while cells:
        priority, tie, curr_row, curr_col = heapq.heappop(cells)

        if processed[curr_row, curr_col]:            
            continue
        processed[curr_row, curr_col] = True
        cells_explored += 1

        if (curr_row, curr_col) == goal:
            found = True
            break

        for r, c, step_length in neighbors(cost, curr_row, curr_col, settings):
            if processed[r, c]:
                continue

            new_cost = best_cost[curr_row, curr_col] + step_cost(
                cost, (curr_row, curr_col), (r, c), step_length)

            if new_cost < best_cost[r, c]:           
                best_cost[r, c] = new_cost
                parent_row[r, c] = curr_row
                parent_col[r, c] = curr_col
                tie_breaker += 1
                heapq.heappush(cells, (new_cost + heuristic((r, c), goal, settings),
                                       tie_breaker, r, c))

    if not found:
        raise ValueError(f"No route from {start} to {goal} (explored {cells_explored} cells)")

    path = reconstruct(parent_row, parent_col, start, goal)
    return (path, float(best_cost[g_row, g_col]), len(path) - 1, cells_explored)


def calculate_stats(path, slope, speed=config.ASTRONAUT_SPEED_MPS):
    if not path:
        raise ValueError("Cannot calculate stats for an empty path")

    total_distance = 0.0

    for i in range(len(path) - 1):
        row1, col1 = path[i]
        row2, col2 = path[i + 1]

        x1, y1 = slope.array_to_map(row1, col1)
        x2, y2 = slope.array_to_map(row2, col2)

        total_distance += math.hypot(x2 - x1, y2 - y1)

    slopes = [slope.get_slope(row, col) for row, col in path]

    max_slope = max(slopes)
    mean_slope = float(np.mean(slopes))

    time_hours = total_distance / speed / 3600

    return {
        "distance_m": total_distance,
        "max_slope_deg": max_slope,
        "mean_slope_deg": mean_slope,
        "est_time_hours": time_hours
    }
        

