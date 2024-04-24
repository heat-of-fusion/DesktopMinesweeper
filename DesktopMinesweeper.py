import os
import cv2
import threading
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from win32api import GetSystemMetrics

from utils import *


UPDATE_TIME = 20

class GUIBlock():
    def __init__(self, blockW, blockH, blockPosX, blockPosY, icon_dict, value, idxX, idxY, vailed = True):
        global state_matrix

        self.win = Tk()
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", 1)

        self.screenW = self.win.winfo_screenwidth()
        self.screenH = self.win.winfo_screenheight()

        self.win.geometry(f'{blockW}x{blockH}+{blockPosX - round(blockW / 2)}+{blockPosY - round(blockH / 2)}')

        self.blockW = blockW
        self.blockH = blockH
        self.blockPosX = blockPosX
        self.blockPosY = blockPosY

        self.icon_dict = icon_dict
        self.value = value
        self.vailed = state_matrix[idxY, idxX]
        self.flagged = False

        self.idxX = idxX
        self.idxY = idxY

    def check_availability(self):
        if state_matrix[self.idxY, self.idxX] == 0:
            self.on_Lclick(None)
            return
        self.win.after(UPDATE_TIME, self.check_availability)

    def on_Lclick(self, event):
        global state_matrix

        if self.flagged:
            return
        if self.vailed:
            self.vailed = False

            # state_matrix = bfs(self.idxY, self.idxX, icon_grid, game_map, state_matrix)
            state_matrix = state_matrix & bfs_new(self.idxY, self.idxX, icon_grid, game_map, np.ones_like(state_matrix))

            if self.value == '0':
                self.win.destroy()
                return

            image = self.icon_dict[self.value]
            image = cv2.resize(image, dsize=(self.blockW, self.blockH))
            image = ImageTk.PhotoImage(image = Image.fromarray(image), master = self.win)

            self.label.configure(image = image)
            self.label.image = image
        else:
            return

    def on_Rclick(self, event):
        if self.flagged:
            self.flagged = False
            image = self.icon_dict['vailed']
            image = cv2.resize(image, dsize=(self.blockW, self.blockH))
            image = ImageTk.PhotoImage(image = Image.fromarray(image), master = self.win)

            self.label.configure(image = image)
            self.label.image = image
            return

        if self.vailed:
            self.flagged = True
            image = self.icon_dict['flag']
            image = cv2.resize(image, dsize=(self.blockW, self.blockH))
            image = ImageTk.PhotoImage(image = Image.fromarray(image), master = self.win)

            self.label.configure(image = image)
            self.label.image = image

        return

    def setup(self):

        def disable_event():
            pass

        image = self.icon_dict['vailed'] if self.vailed else self.icon_dict[self.value]
        image = cv2.resize(image, dsize = (self.blockW, self.blockH))
        image = ImageTk.PhotoImage(image = Image.fromarray(image), master = self.win)

        self.label = Label(self.win, image = image)
        self.label.pack()

        self.label.bind('<Button-1>', self.on_Lclick)
        self.label.bind('<Button-3>', self.on_Rclick)

        self.win.protocol('WM_DELETE_WINDOW', disable_event)
        self.win.after(UPDATE_TIME, self.check_availability)
        self.win.mainloop()

def job(std_distX, std_distY, coordX, coordY, icon_dict, value, idxX, idxY):
    guiblock = GUIBlock(std_distX, std_distY, coordX, coordY, icon_dict, value, idxX, idxY)
    guiblock.setup()

resX, resY = GetSystemMetrics(0), GetSystemMetrics(1)
resize_factor = 4

icon_coords, icon_map, stdW, stdH = get_icon_idx(resize_factor = resize_factor, return_coords_only = False)
icon_map = icon_map.astype(np.float32)
icon_grid, grid_start_coord, grid_end_coord, std_distX, std_distY = grid_search(icon_coords, icon_map, resX, resY, stdW, stdH, resize_factor = resize_factor)

game_map = generate_map(icon_grid)
state_matrix = np.ones_like(icon_grid).astype(np.int8)

plt.imshow(game_map)
plt.show()

icon_dict = dict()
icon_path = './src/sprites/'
file_list = os.listdir(icon_path)
for file_name in file_list:
    icon_dict[file_name.split('.')[0]] = cv2.cvtColor(cv2.imread(icon_path + file_name, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)

std_distX = round((grid_end_coord[0] - grid_start_coord[0]) / (icon_grid.shape[1] - 1))
std_distY = round((grid_end_coord[1] - grid_start_coord[1]) / (icon_grid.shape[0] - 1))

count = 0
for y in range(icon_grid.shape[0]):
    for x in range(icon_grid.shape[1]):
        exec(f'thread_{count} = threading.Thread(target = job, args = (std_distX, std_distY, grid_start_coord[0] + x * std_distX, grid_start_coord[1] + y * std_distY, icon_dict, "{game_map[y, x]}", {x}, {y}))')
        count += 1
count = 0
for y in range(icon_grid.shape[0]):
    for x in range(icon_grid.shape[1]):
        exec(f'thread_{count}.start()')
        count += 1
count = 0
for y in range(icon_grid.shape[0]):
    for x in range(icon_grid.shape[1]):
        exec(f'thread_{count}.join()')
        count += 1