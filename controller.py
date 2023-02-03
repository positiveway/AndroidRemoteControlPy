import gc
import socket
from time import sleep

from code_map import *
from typing_layout import DIRECTIONS


def resole_angle(angle):
    return (angle + 360) % 360


class Controller:
    def connect(self, configs):
        connection_cfg = configs["connection"]
        if connection_cfg['via_wifi']:
            connection_cfg = connection_cfg['wifi']
        else:
            connection_cfg = connection_cfg['phone']

        network_num = connection_cfg["network_num"]
        device_num = connection_cfg["device_num"]

        server_ip = f'192.168.{network_num}.{device_num}'
        server_port = 5005

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((server_ip, server_port))

    def cycle_profile(self, profile):
        return (profile + 1) % 2

    def set_scroll_profile(self):
        if self.scroll_speed_profile == 0:
            profile = "normal"
        else:
            profile = "fast"

        self.scroll_every_n_pixels = self.scroll_cfg[profile]['move_every_n_pixels']

    def toggle_scroll_speed(self):
        self.scroll_speed_profile = self.cycle_profile(self.scroll_speed_profile)
        self.set_scroll_profile()

    def set_hold_profile(self, profile):
        if profile == 0:
            profile = "normal"
        else:
            profile = "during_scroll"

        self.hold_dist = self.hold_cfg[profile]["dist"]
        self.hold_time = self.hold_cfg[profile]["time"]

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

    def init_pressed(self):
        self.pressed = {}
        for button in code_map.values():
            self.pressed[button] = 0

    def release_mouse(self):
        for button in self.mouse_buttons:
            self.msg[0] = button
            self.sock.send(self.msg)
            self.pressed[button] = 0

    def release_all_pressed(self):
        for button in self.pressed.keys():
            if self.pressed[button] > 0:
                self.msg[0] = button
                self.sock.send(self.msg)
                self.pressed[button] = 0

    def release_mouse_and_pressed(self):
        self.release_mouse()
        self.release_modifiers()
        self.release_all_pressed()

    def release_all(self):
        self.release_mouse()
        self.release_modifiers()

        for button in self.pressed.keys():
            if not isinstance(button, (tuple, list)) and button > 0:
                self.msg[0] = button
                self.sock.send(self.msg)
                self.pressed[button] = 0

    def send_type(self, seq):
        if not isinstance(seq, (tuple, list)):
            self.send_pressed(seq)
            self.send_released(seq)
        else:
            for button in seq:
                self.send_pressed(button)

            for button in reversed(seq):
                self.send_released(button)

    def send_pressed(self, button):
        if button == self.Esc:
            self.release_mouse_and_pressed()

        elif not self.is_mouse_mode and button in self.mouse_buttons:
            return

        else:
            if button == self.Caps:
                self.cur_modifier = self.Shift
            else:
                self.cur_modifier = button

            if self.cur_modifier in self.modifiers:
                self.cur_modifier_state = self.modifiers_state[self.cur_modifier]

                if self.cur_modifier_state == 0:
                    if button == self.Caps:
                        self.modifiers_state[self.cur_modifier] = 2
                    else:
                        self.modifiers_state[self.cur_modifier] = 1

                    self.msg[0] = self.cur_modifier + 128
                    self.sock.send(self.msg)

                elif self.cur_modifier_state == 1:
                    if button == self.Caps:
                        self.modifiers_state[self.cur_modifier] = 0
                        self.msg[0] = self.cur_modifier
                        self.sock.send(self.msg)
                    else:
                        self.modifiers_state[self.cur_modifier] = 0
                        self.msg[0] = self.cur_modifier
                        self.sock.send(self.msg)

                elif self.cur_modifier_state == 2:
                    if button == self.Caps:
                        self.modifiers_state[self.cur_modifier] = 0
                        self.msg[0] = self.cur_modifier
                        self.sock.send(self.msg)
                else:
                    ValueError(f'incorrect state: {self.cur_modifier_state}')
                return

        self.msg[0] = button + 128
        self.sock.send(self.msg)
        self.pressed[button] = 1

    def send_released(self, button):
        if button == self.Caps:
            self.cur_modifier = self.Shift
        else:
            self.cur_modifier = button

        if self.cur_modifier in self.modifiers:
            return

        if self.pressed[button] == 1:
            self.msg[0] = button
            self.sock.send(self.msg)
            self.pressed[button] = 0

            for modifier, state in self.modifiers_state.items():
                if state == 1:
                    self.modifiers_state[modifier] = 0
                    self.msg[0] = modifier
                    self.sock.send(self.msg)

            # gc.collect()

    def init_modifiers(self):
        self.modifiers_state = {
            Shift: 0,
            Ctrl: 0,
            Alt: 0,
        }
        self.modifiers = tuple(self.modifiers_state.keys())
        self.cur_modifier = 0
        self.cur_modifier_state = 0

    def release_modifiers(self):
        for modifier in self.modifiers:
            self.msg[0] = modifier
            self.sock.send(self.msg)
            self.modifiers_state[modifier] = 0

    def double_click(self):
        self.send_type(self.LeftMouse)
        sleep(0.25)
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

        self.is_mouse_mode = True
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

        self.init_modifiers()
        self.init_pressed()
        self.reset_typing()

        self.scroll_cfg = configs['scroll']
        self.scroll_speed_profile = 0
        self.set_scroll_profile()

        touchpad_cfg = configs['touchpad']
        self.hold_cfg = touchpad_cfg['hold']
        self.set_hold_profile(0)
        self.visuals_for_touchpad = touchpad_cfg['visuals']

        font_size_cfg = configs['font']['size']
        self.font_size = font_size_cfg['normal']
        self.small_font_size = font_size_cfg['small']

        self.is_game_mode = configs['is_game_mode']
