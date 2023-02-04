import gc
import socket
from time import sleep

from code_map import *
from common import *
from typing_layout import DIRECTIONS


def resole_angle(angle):
    return (angle + 360) % 360


class _State(LockedMap):
    def release(self, button):
        state = self.map[button]
        if state != 0:
            self.put(button, 0)
            return True
        else:
            return False

    def is_pressed(self, button):
        return self.map[button]

    def all_pressed(self):
        return [button for button, value in self.map.items() if value != 0]


class BtnState(_State):
    def __init__(self) -> None:
        super().__init__()

        for button in code_map.values():
            if not is_iterable(button) and button > 0:
                self.put(button, 0)

        self.lock()

    def press(self, button):
        state = self.map[button]
        if state != 1:
            self.put(button, 1)
            return True
        else:
            return False


class ModifiersState(_State):
    def __init__(self) -> None:
        super().__init__()

        self.current = 0

        for code in [Shift, Ctrl, Alt]:
            self.put(code, 0)

        self.lock()

    def set_state(self, new_state):
        if not (0 <= new_state <= 2):
            raise ValueError(f'Incorrect state: {new_state}')

        if self.cur_state != new_state:
            self.put(self.current, new_state)
            return True
        else:
            return False

    @property
    def cur_state(self):
        return self.map[self.current]


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
        gc.collect()

    def send_type(self, seq):
        if not is_iterable(seq):
            self.send_pressed(seq)
            self.send_released(seq)
        else:
            for button in seq:
                self.send_pressed(button)

            for button in reverse(seq):
                self.send_released(button)

    def send_pressed(self, button):
        if button == self.Esc:
            self.release_mouse_and_pressed()

        elif not self.is_mouse_mode and button in self.mouse_buttons:
            return

        else:
            if button == self.Caps:
                self.modifiers.current = self.Shift
            else:
                self.modifiers.current = button

            if self.modifiers.current in self.modifiers.all:
                if self.modifiers.cur_state == 0:
                    if button == self.Caps:
                        self.press_modifier(2)
                    else:
                        self.press_modifier(1)

                elif self.modifiers.cur_state == 1:
                    if button == self.Caps:
                        self.release_modifier()
                    else:
                        self.release_modifier()

                elif self.modifiers.cur_state == 2:
                    if button == self.Caps:
                        self.release_modifier()
                else:
                    raise ValueError(f'incorrect state: {self.modifiers.cur_state}')
                return

        if self.btn_states.press(button):
            self._send_pressed(button)

    def send_released(self, button):
        if button == self.Caps:
            self.modifiers.current = self.Shift
        else:
            self.modifiers.current = button

        if self.modifiers.current in self.modifiers.all:
            return

        if self.btn_states.release(button):
            self._send_released(button)
            self.release_all_modifiers()
            gc.collect()

    def release_all_modifiers(self):
        for modifier, state in self.modifiers.all_pressed():
            self._send_released(modifier)
            self.modifiers.release(modifier)

    def force_release_modifiers(self):
        for modifier in self.modifiers.all:
            self._send_released(modifier)
            self.modifiers.release(modifier)

    def press_modifier(self, state):
        self._send_pressed(self.modifiers.current)
        self.modifiers.set_state(state)

    def release_modifier(self):
        self._send_released(self.modifiers.current)
        self.modifiers.release(self.modifiers.current)

    def _send_pressed(self, button):
        self.msg[0] = button + 128
        self.sock.send(self.msg)

    def _send_released(self, button):
        self.msg[0] = button
        self.sock.send(self.msg)

    def force_release(self, button):
        self._send_released(button)
        self.btn_states.release(button)

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

        self.modifiers = ModifiersState()
        self.btn_states = BtnState()
        self.reset_typing()

        self.scroll_cfg = configs['scroll']
        self.scroll_speed_profile = 0
        self.set_scroll_profile()

        touchpad_cfg = configs['touchpad']
        self.double_click_delay = touchpad_cfg['double_click_delay']
        self.hold_cfg = touchpad_cfg['hold']
        self.set_hold_profile(0)
        self.visuals_for_touchpad = touchpad_cfg['visuals']

        font_size_cfg = configs['font']['size']
        self.font_size = font_size_cfg['normal']
        self.small_font_size = font_size_cfg['small']

        self.is_game_mode = configs['is_game_mode']
