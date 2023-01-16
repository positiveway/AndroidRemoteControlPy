import socket

from code_map import code_map
from layout import load_layout, generate_hints, load_configs
from wsocket import server_ip, server_port


def resole_angle(angle):
    return (angle + 360) % 360


class Controller:
    def get_detailed_hints(self, direction):
        return self.detailed_hints[self.lang][direction]

    def get_preview_hints(self):
        return self.preview_hints[self.lang]

    def print_layout_error(self, typing_positions, error):
        print(f'no letter for this position: {typing_positions} or lang: {self.lang}, error key: {error}')

    def detect_letter(self):
        typing_positions = (self.typing_btn_1, self.typing_btn_2)

        try:
            letter = self.layout[typing_positions][self.lang]
        except KeyError as error:
            self.print_layout_error(typing_positions, error)
            return None

        return letter

    def update_zone(self, btn_num):
        if self.typing_btn_1 is None:
            self.typing_btn_1 = btn_num
            return None
        else:
            self.typing_btn_2 = btn_num
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
        self.release_all_pressed()

    def release_all(self):
        self.release_mouse()

        for button in self.pressed.keys():
            self.msg[0] = button
            self.sock.send(self.msg)
            self.pressed[button] = 0

    def send_sequence(self, seq):
        for button in seq:
            self.send_pressed(button)

        for button in reversed(seq):
            self.send_released(button)

    def send_type(self, button):
        self.send_pressed(button)
        self.send_released(button)

    def send_pressed(self, button):
        press_count = self.pressed[button]
        self.msg[0] = button + 128
        self.sock.send(self.msg)
        self.pressed[button] = press_count + 1

    def send_released(self, button):
        press_count = self.pressed[button]
        if press_count > 0:
            self.msg[0] = button
            self.sock.send(self.msg)
            self.pressed[button] = press_count - 1

            # gc.collect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((server_ip, server_port))

        # self.run_scheduler()

    def send_empty_msg(self):
        try:
            self.sock.send(self.empty_msg)
        except ConnectionRefusedError:
            pass

    def run_scheduler(self):
        self.empty_msg = bytes(1)

        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.send_empty_msg, 'interval', seconds=1)
        scheduler.start()

    def set_scroll_speed(self):
        self.scroll_every_n_pixels = self.scroll_speed_cfg[self.scroll_speed_profile]

    def toggle_speed(self, speed):
        return (speed + 1) % 2

    def toggle_scroll_speed(self):
        self.scroll_speed_profile = self.toggle_speed(self.scroll_speed_profile)
        self.set_scroll_speed()

    def __init__(self):
        self.connect()

        self.msg = bytearray(1)

        self.LeftMouse = code_map["LeftMouse"]
        self.RightMouse = code_map["RightMouse"]
        self.MiddleMouse = code_map["MiddleMouse"]
        self.mouse_buttons = (self.LeftMouse, self.RightMouse, self.MiddleMouse)

        self.Ctrl = code_map["Ctrl"]
        self.Shift = code_map["Shift"]

        self.is_shift_pressed = False

        self.layout = load_layout()
        configs = load_configs()

        self.detailed_hints, self.preview_hints = generate_hints(self.layout)

        for letters in self.layout.values():
            for lang, letter in letters.items():
                letters[lang] = code_map[letter]

        self.lang = 'en'

        typing_cfg = configs['typing']
        self.visuals_for_typing = typing_cfg['visuals']
        self.reset_typing()

        scroll_speed_cfg = configs['scroll']
        self.scroll_speed_cfg = {
            0: scroll_speed_cfg['normal']['move_every_n_pixels'],
            1: scroll_speed_cfg['fast']['move_every_n_pixels'],
        }
        self.scroll_speed_profile = 0
        self.set_scroll_speed()

        touchpad_cfg = configs['touchpad']
        self.hold_dist = touchpad_cfg["hold_dist"]
        hold_time_cfg = touchpad_cfg["hold_time"]
        self.hold_time_normal = hold_time_cfg['normal']
        self.hold_time_during_scroll = hold_time_cfg['during_scroll']
        self.visuals_for_touchpad = touchpad_cfg['visuals']

        font_size_cfg = configs['font']['size']
        self.font_size = font_size_cfg['normal']
        self.small_font_size = font_size_cfg['small']

        self.init_pressed()
