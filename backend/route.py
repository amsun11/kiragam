import numpy as np
import heapq
import math
import config

STRAIGHT_MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONAL_MOVES = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def neighbors(cost, row, col, settings):
    # settings is a dict: {"cell_size": 5.0, "allow_diagonal": True, "prevent_corner_cutting": True}
    if not usable(cost, row, col):
        return []                      # a blocked start cell has no neighbors

    x, y = cost.shape                  # x = number of rows, y = number of columns
    cell_size = settings["cell_size"]
    valid_neighbors = []

    for i in STRAIGHT_MOVES:
        new_row = row + i[0]
        new_col = col + i[1]

        # Off the grid: skip this move (don't raise)
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

            # Corner cutting: the two cells the diagonal squeezes between
            if settings["prevent_corner_cutting"]:
                if not usable(cost, new_row, col) or not usable(cost, row, new_col):
                    continue

            valid_neighbors.append((new_row, new_col, step_length))

    return valid_neighbors


def usable(cost, row, col):
    return math.isfinite(cost[row, col])


def build_settings(cell_size, cost):
    finite = np.isfinite(cost)
    if not finite.any():
        raise ValueError("Cost grid has no usable cells")

    min_cost = float(cost[finite].min())          # cheapest cost per meter anywhere in the grid
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

    else:
        total_dist = (row_dist + col_dist) * cell_size
    
    return total_dist * settings["minimum_cost"]


def reconstruct(parent_row, parent_col, start, goal):

    start = tuple(start)                  # so the comparison below works for lists too
    row, col = goal
    path = [(row, col)]
    max_steps = parent_row.size           # a path can't be longer than the grid

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


           



parent_row = np.full((3, 4), -1, dtype=np.int32)
parent_col = np.full((3, 4), -1, dtype=np.int32)

parent_row[0, 1], parent_col[0, 1] = 0, 0     # (0,1) came from (0,0)
parent_row[1, 2], parent_col[1, 2] = 0, 1     # (1,2) came from (0,1)
parent_row[2, 3], parent_col[2, 3] = 1, 2     # (2,3) came from (1,2)

print(reconstruct(parent_row, parent_col, (0, 0), (2, 3)))   # [(0,0), (0,1), (1,2), (2,3)]
print(reconstruct(parent_row, parent_col, (0, 0), (0, 0)))   # [(0,0)]

try:
    reconstruct(parent_row, parent_col, (0, 0), (2, 0))      # (2,0) has no parent
except ValueError as e:
    print(e)                                                 # Broken parent chain at cell (2, 0)