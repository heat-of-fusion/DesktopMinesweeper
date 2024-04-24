import numpy as np
import matplotlib.pyplot as plt
from win32api import GetSystemMetrics
from utils.GridDistanceSearcher import grid_search
from utils.DesktopIconLayoutParser import get_icon_idx
from utils.KeyInterceptor import KeyInterceptor
from MinesweeperPrototype import MinesweeperPrototype

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

icon_grid = grid_search(icon_coords, icon_map, resX, resY, stdW, stdH, resize_factor = resize_factor)
plt.imshow(icon_grid)
plt.title('Icon Grid')
plt.show()

interceptor = KeyInterceptor()
interceptor.register_keyset('ShowDesktop', ['LEFT_WIN', 'D'])
interceptor.register_keyset('OpenExplorer', ['LEFT_WIN', 'E'])
interceptor.register_keyset('Copy', ['LCTRL', 'C'])
print('Key Interceptor Test')
interceptor.start_session()

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