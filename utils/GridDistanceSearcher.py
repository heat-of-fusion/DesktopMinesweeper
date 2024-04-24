import cv2
import numpy as np
import matplotlib.pyplot as plt
from itertools import permutations
from win32api import GetSystemMetrics

from .DesktopIconLayoutParser import get_icon_idx

def arrange_axis(coords, min_dist): # Remove Overlappings

    check_idx = 0
    while True:
        if check_idx >= len(coords):
            break

        dist_vector = np.abs(coords - coords[check_idx])

        dist_vector[check_idx] = 999.0
        remv_idxs = np.where(dist_vector < min_dist)

        remv_idxs = np.array(list(range(len(dist_vector))))[remv_idxs]

        coords = np.delete(coords, remv_idxs)

        check_idx += 1

    return coords

def grid_estimator_1D(coords, optim_rate = 0, return_std_dist = False):
    std_dist = np.array(list(permutations(coords, 2)))
    std_dist = min(np.abs(std_dist[:, 0] - std_dist[:, 1]))
    grid_list = [True]

    curr_axis = 0
    serial_flag = True
    while curr_axis + 1 < len(coords):
        dist = coords[curr_axis + 1] - coords[curr_axis]
        grid_dist = round(dist / std_dist)

        # Optimizing Standard Distance
        std_dist = int((1 - optim_rate) * std_dist + optim_rate * round(dist / grid_dist))

        for i in range(grid_dist - 1):
            grid_list.append(False)
        grid_list.append(True)

        curr_axis += 1

    grid_list = np.array(grid_list)

    return (grid_list, std_dist) if return_std_dist else grid_list

def grid_estimator_2D(icon_map, gridX, gridY, grid_start_coord, grid_end_coord, std_distX, std_distY, resize_factor = 4, tolerance = 0.5):
    grid = np.zeros([len(gridY), len(gridX)]).astype(np.bool8)

    resX, resY = icon_map.shape[1], icon_map.shape[0]
    icon_map = cv2.resize(icon_map, dsize = (resX * resize_factor, resY * resize_factor))

    x, y, idxX, idxY = grid_start_coord[0], grid_start_coord[1], 0, 0
    distX = round((grid_end_coord[0] - grid_start_coord[0]) / (len(gridX) - 1))
    distY = round((grid_end_coord[1] - grid_start_coord[1]) / (len(gridY) - 1))

    while idxY < len(gridY): # Y
        while idxX < len(gridX): # X
            curr_box = icon_map[y - distY // 4 : y + distY // 4, x - distX // 4 : x + distX // 4]
            if curr_box.mean() > tolerance:
                grid[idxY, idxX] = True

            x += distX
            idxX += 1

        x, idxX = grid_start_coord[0], 0
        y += distY
        idxY += 1

    return grid

def grid_search(icon_coords, icon_map, resX, resY, stdW, stdH, resize_factor = 4):

    coordX, coordY = icon_coords[:, 0], icon_coords[:, 1]
    min_dist_x, min_dist_y = stdW / 2, stdH / 2

    coordX = sorted(arrange_axis(coordX, min_dist_x)) # Grid X Search
    coordY = sorted(arrange_axis(coordY, min_dist_y)) # Grid Y Search

    grid_start_coord = (coordX[0], coordY[0])
    grid_end_coord = (coordX[-1], coordY[-1])

    gridX, std_distX = grid_estimator_1D(coordX, 0.7, return_std_dist = True)
    gridY, std_distY = grid_estimator_1D(coordY, 0.7, return_std_dist = True)

    grid = grid_estimator_2D(icon_map, gridX, gridY, grid_start_coord, grid_end_coord, std_distX, std_distY, resize_factor = resize_factor)

    return grid, grid_start_coord, grid_end_coord, std_distX, std_distY

if __name__ == '__main__':
    resX, resY = GetSystemMetrics(0), GetSystemMetrics(1)
    resize_factor = 4

    icon_coords, icon_map, stdW, stdH = get_icon_idx(resize_factor = resize_factor, return_coords_only = False)
    plt.subplot(1, 2, 1)
    plt.scatter(icon_coords[:, 0], icon_coords[:, 1])
    plt.title(f'StdW: {stdW}, StdH: {stdH}')
    plt.subplot(1, 2, 2)
    plt.imshow(icon_map)
    plt.show()

    icon_map = icon_map.astype(np.float32)

    grid, grid_start_coord, grid_end_coord, std_distX, std_distY = grid_search(icon_coords, icon_map, resX, resY, stdW, stdH, resize_factor = resize_factor)
    plt.imshow(grid)
    plt.title('Estimated Grid')
    plt.show()