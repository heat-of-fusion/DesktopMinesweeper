import numpy as np
from collections import deque

def generate_map(icon_grid):
    game_map = icon_grid.copy().astype(np.int8)
    game_map[np.where(game_map == 1)] = -1

    x_range = [0, len(icon_grid[1])]
    y_range = [0, len(icon_grid[0])]

    for y in range(icon_grid.shape[0]):
        for x in range(icon_grid.shape[1]):
            if game_map[y, x] == -1:
                continue
            curr_box = game_map[max(y - 1, y_range[0]): min(y + 2, y_range[1]), max(x - 1, x_range[0]): min(x + 2, x_range[1])]
            game_map[y, x] = len(np.where(curr_box == -1)[0])

    return game_map

def bfs(y, x, icon_grid, game_map, vail_map):

    if game_map[y][x] not in [-1, 0]:
        vail_map[y, x] = 0
        return vail_map

    check_list = np.zeros_like(icon_grid).astype(np.bool8)
    dy, dx = [0, 0, 1, -1], [1, -1, 0, 0]

    resY, resX = icon_grid.shape[0], icon_grid.shape[1]

    check_list[y][x] = True
    queue = deque()
    queue.appendleft((y, x))
    while queue:
        ey, ex = queue.pop()
        vail_map[ey, ex] = 0
        for i in range(4):
            ny, nx = ey + dy[i], ex + dx[i]
            if 0 <= ny < resY and 0 <= nx < resX:
                if check_list[ny][nx] == True:
                    continue
                if game_map[ny][nx] != -1:
                    check_list[ny][nx] = True
                    queue.appendleft((ny, nx))

    return vail_map

def bfs_new(y, x, icon_grid, game_map, vail_map):

    x_range = [0, len(icon_grid[1])]
    y_range = [0, len(icon_grid[0])]

    if game_map[y][x] not in [-1, 0]:
        vail_map[y, x] = 0
        return vail_map

    check_list = np.zeros_like(icon_grid).astype(np.bool8)
    dy, dx = [0, 0, 1, -1], [1, -1, 0, 0]

    resY, resX = icon_grid.shape[0], icon_grid.shape[1]

    check_list[y][x] = True
    queue = deque()
    queue.appendleft((y, x))
    while queue:
        ey, ex = queue.pop()
        # vail_map[ey, ex] = 0
        vail_map[max(ey - 1, y_range[0]): min(ey + 2, y_range[1]), max(ex - 1, x_range[0]): min(ex + 2, x_range[1])] = 0
        for i in range(4):
            ny, nx = ey + dy[i], ex + dx[i]
            if 0 <= ny < resY and 0 <= nx < resX:
                if check_list[ny][nx] == True:
                    continue
                if game_map[ny][nx] == 0:
                    check_list[ny][nx] = True
                    queue.appendleft((ny, nx))

    return vail_map