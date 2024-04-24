import ctypes
import win32api
from ctypes.wintypes import MSG
from itertools import permutations

from .HiddenValues import *

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class KeyInterceptor():
    def __init__(self):
        self.KEY_TO_ID = KEY_TO_ID
        self.KEY_TO_VK = KEY_TO_VK

        self.hook_keysets = dict()

    def register_keyset(self, ID, keyset):
        if ID in self.hook_keysets.keys():
            print(f'Same ID Already Exists! hook_keysets["ID"]: {self.hook_keysets[ID]}')
            return
        self.hook_keysets[ID] = keyset

    def remove_keyset(self, ID):
        if ID not in self.hook_keysets.keys():
            print(f'ID {ID} Does Not Exist! Remove Failed!')
            return
        del self.hook_keysets[ID]

    def install_hook(self, pointer):
        self.hooked = user32.SetWindowsHookExA(
            13,
            pointer,
            None,
            0
        )
        if not self.hooked:
            return False
        return True

    def uninstall_hook(self):
        if self.hooked is None:
            return
        user32.UnhookWindowsHookEx(self.hooked)
        self.hooked = None
        return

    def start_session(self):
        HOOKPROTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        pointer = HOOKPROTYPE(self.hook_and_ignore)

        self.hooked = None
        if self.install_hook(pointer):
            try:
                msg = MSG()
                user32.GetMessageA(ctypes.byref(msg), 0, 0, 0)
            except:
                print(f'Error!')

    def hook_and_ignore(self, nCode, wParam, lParam):
        if nCode < 0:
            return user32.CallNextHookEx(self.hooked, nCode, wParam, lParam)

        if wParam == 256 or wParam == 257:
            for id in self.hook_keysets:
                keyset = self.hook_keysets[id]
                perm_keysets = list(permutations(keyset))

                for comb_keyset in perm_keysets:
                    query = comb_keyset[0]
                    rest = comb_keyset[1:]

                    if self.KEY_TO_ID[query] == lParam.contents.value:
                        pass_flag = 32768
                        for key in rest:
                            key_pressed = win32api.GetAsyncKeyState(self.KEY_TO_VK[key]) & 0x8000
                            pass_flag = pass_flag & key_pressed

                        if pass_flag:
                            return 1

        return user32.CallNextHookEx(self.hooked, nCode, wParam, lParam)

if __name__ == '__main__':
    interceptor = KeyInterceptor()
    interceptor.register_keyset('GoToDesktop', ['LEFT_WIN', 'D'])
    interceptor.register_keyset('Explorer', ['LEFT_WIN', 'E'])
    interceptor.register_keyset('Screenshot', ['LEFT_WIN', 'LSHIFT', 'S'])
    interceptor.start_session()