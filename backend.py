import socket

from code_map import *
from typing_layout import load_layout, generate_hints, load_configs


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

    def get_detailed_hints(self, direction):
        return self.detailed_hints[self.lang][direction]

    def get_preview_hints(self):
        return self.preview_hints[self.lang]

    def detect_letter(self):
        try:
            letter = self.layout[self.lang][self.typing_btn_1][self.typing_btn_2]
        except KeyError as error:
            print(
                f'no letter for this position: ({self.typing_btn_1}, {self.typing_btn_2}) or lang: {self.lang}, error key: {error}')
            return None

        return letter

    def update_typing_state(self, btn_direction):
        if self.typing_btn_1 is None:
            self.typing_btn_1 = btn_direction
            return None
        else:
            if btn_direction == self.CentralDir:
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
            if not isinstance(button, (tuple, list)):
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
                modifier = self.Shift
            else:
                modifier = button

            if modifier in self.modifiers:
                state = self.modifiers_state[modifier]

                if state == 0:
                    if button == self.Caps:
                        self.modifiers_state[modifier] = 2
                    else:
                        self.modifiers_state[modifier] = 1

                    self.msg[0] = modifier + 128
                    self.sock.send(self.msg)

                elif state == 1:
                    if button == self.Caps:
                        self.modifiers_state[modifier] = 0
                        self.msg[0] = modifier
                        self.sock.send(self.msg)
                    else:
                        self.modifiers_state[modifier] = 0
                        self.msg[0] = modifier
                        self.sock.send(self.msg)

                elif state == 2:
                    if button == self.Caps:
                        self.modifiers_state[modifier] = 0
                        self.msg[0] = modifier
                        self.sock.send(self.msg)
                else:
                    ValueError(f'incorrect state: {state}')
                return

        self.msg[0] = button + 128
        self.sock.send(self.msg)
        self.pressed[button] = 1

    def send_released(self, button):
        if button == self.Caps:
            modifier = self.Shift
        else:
            modifier = button

        if modifier in self.modifiers:
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
        self.modifiers = self.modifiers_state.keys()

    def release_modifiers(self):
        for modifier in self.modifiers:
            self.msg[0] = modifier
            self.sock.send(self.msg)
            self.modifiers_state[modifier] = 0

    def __init__(self):
        self.CentralDir = 5

        self.layout = load_layout()
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
        self.Enter = Enter
        self.Backspace = Backspace
        self.Esc = Esc

        self.init_modifiers()
        self.init_pressed()
        self.reset_typing()

        self.detailed_hints, self.preview_hints = generate_hints(self.layout)

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
