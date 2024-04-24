import os
import cv2
import pyautogui
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from win32api import GetSystemMetrics

from utils import *

class MinesweeperPrototype():
    def __init__(self, resX, resY, icon_path, random_seed = None, resize_factor = 4, icon_res = 128):
        icon_coords, icon_map, stdW, stdH = get_icon_idx(return_coords_only=False)

        self.icon_idx = icon_coords
        self.icon_grid, self.grid_start_coord, self.grid_end_coord, self.std_distX, std_distY = grid_search(icon_coords, icon_map, resX, resY, stdW, stdH, resize_factor = resize_factor)
        self.icon_grid = self.icon_grid.astype(np.int8)
        self.random_seed = random_seed
        self.visual_map = np.zeros([self.icon_grid.shape[0] * icon_res, self.icon_grid.shape[1] * icon_res, 3]).astype(np.uint8)

        self.icon_path = icon_path
        self.icon_dict = dict()
        self.load_icons()
        self.icon_res = icon_res

        self.game_map = self.icon_grid.astype(np.int8)
        self.game_map[np.where(self.game_map == 1)] = -1

        self.vail_map = np.ones_like(self.game_map).astype(np.int8) # 0: Open, 1: Vailed, 2: Flaged, 3: mine_bomb, 4: mine_wrong

        # self.game_map = np.zeros_like(self.icon_grid).astype(np.int8)

        self.generate_map()
        self.generate_visual_map()

        plt.figure(figsize = (10, 7))
        plt.imshow(self.visual_map)
        plt.title('Visual Map')
        plt.show()

    def load_icons(self):
        file_list = os.listdir(self.icon_path)
        for file_name in file_list:
            self.icon_dict[file_name.split('.')[0]] = cv2.cvtColor(cv2.imread(self.icon_path + file_name), cv2.COLOR_BGR2RGB)

    def generate_visual_map(self):
        gridX, gridY = self.icon_grid.shape[1], self.icon_grid.shape[0]
        for y in range(gridY):
            for x in range(gridX):
                if self.vail_map[y, x] == 1:
                    self.visual_map[y * self.icon_res : (y + 1) * self.icon_res, x * self.icon_res : (x + 1) * self.icon_res] = self.icon_dict['vailed']
                    continue
                elif self.vail_map[y, x] == 2:
                    self.visual_map[y * self.icon_res : (y + 1) * self.icon_res, x * self.icon_res : (x + 1) * self.icon_res] = self.icon_dict['flag']
                    continue
                elif self.vail_map[y, x] == 3:
                    self.visual_map[y * self.icon_res : (y + 1) * self.icon_res, x * self.icon_res : (x + 1) * self.icon_res] = self.icon_dict['mine_bomb']
                    continue
                if self.icon_grid[y, x] in list(range(-1, 9)):
                    self.visual_map[y * self.icon_res : (y + 1) * self.icon_res, x * self.icon_res : (x + 1) * self.icon_res] = self.icon_dict[f'{self.game_map[y, x]}']

    def generate_map(self):
        x_range = [0, len(self.icon_grid[1])]
        y_range = [0, len(self.icon_grid[0])]

        for y in range(self.icon_grid.shape[0]):
            for x in range(self.icon_grid.shape[1]):
                if self.game_map[y, x] == -1:
                    continue
                curr_box = self.game_map[max(y - 1, y_range[0]) : min(y + 2, y_range[1]), max(x - 1, x_range[0]) : min(x + 2, x_range[1])]
                self.game_map[y, x] = len(np.where(curr_box == -1)[0])

    def shuffle_icons(self):
        return

    def setup(self):
        return

    def bfs(self, y, x):
        check_list = np.zeros_like(self.icon_grid).astype(np.bool8)
        dy, dx = [0, 0, 1, -1], [1, -1, 0, 0]

        resY, resX = self.icon_grid.shape[0], self.icon_grid.shape[1]

        check_list[y][x] = True
        queue = deque()
        queue.appendleft((y, x))
        while queue:
            ey, ex = queue.pop()
            self.vail_map[ey, ex] = 0
            for i in range(4):
                ny, nx = ey + dy[i], ex + dx[i]
                if 0 <= ny < resY and 0 <= nx < resX:
                    if check_list[ny][nx] == True:
                        continue
                    if self.game_map[ny][nx] != -1:
                        check_list[ny][nx] = True
                        queue.appendleft((ny, nx))

    def place_flag(self, y, x):
        if self.vail_map[y, x] == 0:
            return
        elif self.vail_map[y, x] == 1:
            self.vail_map[y, x] = 2
        elif self.vail_map[y, x] == 2:
            self.vail_map[y, x] = 1

    def game_over(self, y, x):
        self.vail_map[np.where(self.game_map == -1)] = 0
        self.vail_map[y, x] = 3

    def click(self, x, y, order):
        if order == 'dig':
            if self.vail_map[y, x] == 2:
                return

            if self.game_map[y, x] == -1:
                self.game_over(y, x)
            else:
                self.bfs(y, x)

            self.generate_visual_map()
            plt.figure(figsize=(10, 7))
            plt.imshow(self.visual_map)
            plt.title('Visual Map')
            plt.show()

        elif order == 'flag':
            self.place_flag(y, x)
            self.generate_visual_map()
            plt.figure(figsize = (10, 7))
            plt.imshow(self.visual_map)
            plt.title('Visual Map')
            plt.show()
        else:
            return

resX, resY = GetSystemMetrics(0), GetSystemMetrics(1)
minesweeper = MinesweeperPrototype(resX, resY, icon_path = './src/sprites/')

while True:
    try:
        order_list = input('Order: ').split('.')
        order = order_list[0]
        x, y = [int(val) for val in order_list[1:]]
        minesweeper.click(y, x, order)
    except:
        continue