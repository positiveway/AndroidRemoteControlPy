import gc
import socket
from time import sleep

from code_map import *
from common import *
from typing_layout import DIRECTIONS


def resole_angle(angle):
    return (angle + 360) % 360


class Controller:
    def connect(self, configs):
        connection_cfg = configs["connection"]

        from kivy.utils import platform
        if platform == 'android':
            if connection_cfg['via_wifi']:
                connection_cfg = connection_cfg['wifi']
            else:
                connection_cfg = connection_cfg['phone']
        else:
            connection_cfg = connection_cfg['test']

        network_num = connection_cfg["network_num"]
        device_num = connection_cfg["device_num"]

        server_ip = f'192.168.{network_num}.{device_num}'
        server_port = 5005

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((server_ip, server_port))

    def set_scroll_profile(self):
        if self.is_high_precision:
            profile = "normal"
        else:
            profile = "fast"

        self.scroll_every_n_pixels = self.scroll_cfg[profile]['move_every_n_pixels']
        print(self.scroll_every_n_pixels)
        exit()
        self.scroll_by = self.scroll_cfg[profile]['move_by']

    def get_detailed_hints(self):
        direction = self.typing_btn_1

        if self.is_left:
            hints = self.left_detailed_hints
        else:
            hints = self.right_detailed_hints

        return hints[self.lang][direction]

    def get_preview_hints(self, is_left):
        if is_left:
            hints = self.left_preview_hints
        else:
            hints = self.right_preview_hints

        return hints[self.lang]

    def detect_letter(self):
        if self.is_left:
            layout = self.left_first_layout
        else:
            layout = self.right_first_layout

        letter = layout[self.lang][self.typing_btn_1][self.typing_btn_2]
        if letter == '':
            print(f'no letter for this position: ({self.typing_btn_1}, {self.typing_btn_2}) or lang: {self.lang}')
            return None

        return letter

    def update_typing_state(self, btn_direction, is_left):
        if self.typing_btn_1 is None:
            self.typing_btn_1 = btn_direction
            self.is_left = is_left
            return None
        else:
            if self.is_left == is_left:
                if btn_direction == self.CentralDir:
                    self.reset_typing()
                    return self.Switch_code
                else:
                    self.reset_typing()
                    return None
            else:
                self.typing_btn_2 = btn_direction
                letter = self.detect_letter()
                self.reset_typing()
                return letter

    def reset_typing(self):
        self.typing_btn_1 = None
        self.typing_btn_2 = None
        self.is_left = None

    def mouse_mode_btn_pressed(self, btn_direction):
        command = self.mouse_mode_layout[btn_direction]
        if command == '':
            command = None

        return command

    def release_mouse(self):
        for button in self.mouse_buttons:
            self.force_release(button)

    def release_all_pressed(self):
        for button in self.btn_states.all_pressed():
            self.force_release(button)

    def release_mouse_and_pressed(self):
        self.release_mouse()
        self.force_release_modifiers()
        self.release_all_pressed()

    def release_all(self):
        self.release_mouse()
        self.force_release_modifiers()

        for button in self.btn_states.all:
            self.force_release(button)

        self.reset_typing()


    def double_click(self):
        self.send_type(self.LeftMouse)
        sleep(self.double_click_delay)
        self.send_type(self.LeftMouse)

    def __init__(self):
        from typing_layout import load_layout, generate_hints, generate_mouse_hints, load_configs

        self.CentralDir = 5 - 1

        self.mouse_mode_layout, self.left_first_layout, self.right_first_layout = load_layout()

        self.left_detailed_hints, self.left_preview_hints = generate_hints(self.left_first_layout)
        self.right_detailed_hints, self.right_preview_hints = generate_hints(self.right_first_layout)
        self.empty_hints = tuple(['' for _ in DIRECTIONS])
        self.mouse_hints = generate_mouse_hints(self.mouse_mode_layout)

        configs = load_configs()

        self.msg = bytearray(1)
        self.connect(configs)

        self.lang = 'en'

        self.LeftMouse = LeftMouse
        self.RightMouse = RightMouse
        self.MiddleMouse = MiddleMouse
        self.mouse_buttons = (self.LeftMouse, self.RightMouse, self.MiddleMouse)

        self.Ctrl = Ctrl
        self.Alt = Alt
        self.Shift = Shift
        self.Caps = Caps
        self.Switch_code = Switch_code
        self.Esc = Esc

        self.modifiers = ModifiersState()
        self.btn_states = BtnState()
        self.reset_typing()

        self.is_high_precision = True

        self.scroll_cfg = configs['scroll']
        self.set_scroll_profile()

        touchpad_cfg = configs['touchpad']
        self.double_click_delay = touchpad_cfg['double_click_delay']
        self.visuals_for_touchpad = touchpad_cfg['visuals']

        font_size_cfg = configs['font']['size']
        self.font_size = font_size_cfg['normal']
        self.small_font_size = font_size_cfg['small']

        self.is_game_mode = configs['is_game_mode']

        game_cfg = configs['game']
        self.game_button_delay = game_cfg['button_delay']
        self.arrows_mode = game_cfg['arrows_mode']

        self.is_mouse_mode = True
