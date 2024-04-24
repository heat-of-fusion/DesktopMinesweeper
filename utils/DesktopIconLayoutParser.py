import cv2
import pyautogui
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from win32api import GetSystemMetrics

check_list = None

def initial_move():
    pyautogui.hotkey('win', 'd')
    init_capture = np.array(pyautogui.screenshot())

    pyautogui.hotkey('ctrl', 'a')
    curr_capture = np.array(pyautogui.screenshot())

    pyautogui.click()
    pyautogui.hotkey('win', 'd')

    return init_capture, curr_capture


def bfs(y, x, thres_x, thres_y, diff, resX, resY):
    idx_list = [[], []]
    dy, dx = [0, 0, 1, -1], [1, -1, 0, 0]
    size = 1
    check_list[y][x] = True
    queue = deque()
    queue.appendleft((y, x))
    while queue:
        ey, ex = queue.pop()
        idx_list[0].append(ex)
        idx_list[1].append(ey)
        for i in range(4):
            ny, nx = ey + dy[i], ex + dx[i]
            if 0 <= ny < resY and 0 <= nx < resX:
                if check_list[ny][nx] == True:
                    continue
                if diff[ny][nx] == 1:
                    check_list[ny][nx] = True
                    size += 1
                    queue.appendleft((ny, nx))

    idx_list[0] = np.array(idx_list[0])
    idx_list[1] = np.array(idx_list[1])

    block_width = max(idx_list[0]) - min(idx_list[0])
    block_height = max(idx_list[1]) - min(idx_list[1])

    coord_00 = (min(idx_list[0]), min(idx_list[1]))
    coord_01 = (max(idx_list[0]), min(idx_list[1]))
    coord_10 = (min(idx_list[0]), max(idx_list[1]))
    coord_11 = (max(idx_list[0]), max(idx_list[1]))

    if resX / thres_x > block_width and resY / thres_y > block_height:
        return None

    return idx_list, coord_00, coord_01, coord_10, coord_11, block_width, round(block_height * 6 / 7)

def get_coord_center(coords):
    x, y = int(), int()
    for coord in coords[0]:
        x += coord
        y += coord
    return round(x / len(coords)), round(y / len(coords))

def get_window_info(diff, resX, resY):
   block_idx = list()
   block_coords = list()
   icon_coords = list()

   stdW, stdH, denominator = int(), int(), int()
   
   for y in range(resY):
       for x in range(resX):
           if check_list[y, x] or diff[y, x] == 0:
               continue
           else:
               if diff[y, x] == 1:
                   result = bfs(y, x, 20, 50, diff, resX, resY)
                   if result is not None:
                       block_idx.append(result[0])
                       block_coords.append(result[1:5])

                       coord_00, coord_01 = result[1], result[2]
                       coord_10, coord_11 = result[3], result[4]

                       block_center_x = round((coord_00[0] + coord_01[0] + coord_10[0] + coord_11[0]) / 4)
                       block_center_y = round((coord_00[1] + coord_01[1] + coord_10[1] + coord_11[1]) / 4)
                       block_x_start_axis = round((coord_00[0] + coord_10[0]) / 2)
                       block_width, block_height = result[5], result[6]

                       block_count = round(block_width / block_height)
                       block_space = round(block_width / (block_count * 2))

                       for i in range(block_count):
                           block_x = block_x_start_axis + ((i + 1) * 2 - 1) * block_space
                           block_y = block_center_y

                           icon_coords.append((block_x, block_y))

                           stdW += block_space * 2
                           stdH += block_height
                           denominator += 1

   return block_idx, block_coords, np.array(icon_coords), round(stdW / denominator), round(stdH / denominator)

def get_icon_idx(resize = True, resize_factor = 4, return_coords_only = True):
    global check_list
    
    pyautogui.FAILSAFE = False
    winX, winY = GetSystemMetrics(0), GetSystemMetrics(1)
    diff_thres = 0.5

    init_capture, curr_capture = initial_move()
    diff = np.abs(init_capture - curr_capture)
    resX, resY = winX, winY

    if resize:
        resX, resY = winX // resize_factor, winY // resize_factor
        diff = cv2.resize(diff, dsize = (resX, resY))
        resized_capture = cv2.resize(curr_capture, dsize = (resX, resY))

    diff[np.where(diff > diff_thres)] = 1
    diff[np.where(diff < diff_thres)] = 0

    diff = diff[:, :, 0] | diff[:, :, 1] | diff[:, :, 2]
    
    check_list = np.zeros_like(diff).astype(np.bool8)
    block_idx, block_coords, icon_coords, stdW, stdH = get_window_info(diff, resX, resY)

    icon_map = np.zeros_like(diff)
    for block_coord in block_coords:
        icon_map[block_coord[0][1]:block_coord[3][1] + 1, block_coord[0][0]:block_coord[3][0] + 1] = 1

    return icon_coords * 4 if return_coords_only else (icon_coords * 4, icon_map, stdW * 4, stdH * 4)

if __name__ == '__main__':
    icon_coords, icon_map, stdW, stdH = get_icon_idx(return_coords_only = False)
    plt.scatter(icon_coords[:, 0], icon_coords[:, 1])
    plt.title(f'Icon Count: {len(icon_coords)}\n StdW: {stdW}, StdH: {stdH}')
    plt.show()