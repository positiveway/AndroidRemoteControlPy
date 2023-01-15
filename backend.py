import socket

from code_map import code_map
from layout import load_layout, generate_hints, load_configs
from wsocket import server_ip, server_port


def resole_angle(angle):
    return (angle + 360) % 360


class Controller:
    def get_direction_hints(self, direction):
        return self.direction_hints[self.lang][direction]

    def gen_boundary_mapping(self, angle_margin):
        base_mapping = {
            0: "🢂",
            45: "🢅",
            90: "🢁",
            135: "🢄",
            180: "🢀",
            225: "🢇",
            270: "🢃",
            315: "🢆",
        }
        angles_mapping = {}

        for base_angle, direction in base_mapping.items():
            for angle in range(base_angle - angle_margin, base_angle + angle_margin):
                angle = resole_angle(angle)
                angles_mapping[angle] = direction

        return angles_mapping

    def detect_zone(self, magnitude, angle):
        angle = int(angle)

        if magnitude > self.magnitude_threshold:
            return self.boundary_mapping.get(angle, self.UNMAPPED_ZONE)
        else:
            return self.NEUTRAL_ZONE

    def print_layout_error(self, stick_positions, error):
        print(f'no letter for this position: {stick_positions} or lang: {self.lang}, error key: {error}')

    def detect_letter(self):
        stick_positions = (self.stick_pos_1, self.stick_pos_2)

        try:
            letters = self.layout[stick_positions]
        except KeyError as error:
            self.print_layout_error(stick_positions, error)
            return None

        try:
            letter = letters[self.lang]
        except KeyError as error:
            self.print_layout_error(stick_positions, error)
            return None

        return letter

    def update_zone(self, magnitude, angle):
        if self.cur_stage < 1:  # self.cur_stage == 0 or self.cur_stage == 0.5:
            prev_zone = self.stick_pos_1
        else:  # elif self.cur_stage == 1 or self.cur_stage == 1.5:
            prev_zone = self.stick_pos_2

        new_zone = self.detect_zone(magnitude, angle)

        # print(f'1 not set: {self.stick_1_not_set}, prev: {prev_zone}, new: {new_zone}, pos 1: {self.stick_pos_1}, pos2: {self.stick_pos_2}')

        if new_zone == self.UNMAPPED_ZONE or new_zone == prev_zone:
            return None

        if new_zone == self.NEUTRAL_ZONE:
            self.awaiting_neutral_pos = False
            self.cur_stage += 0.5

            if self.cur_stage == 2:
                self.reset_typing()
        else:
            if self.awaiting_neutral_pos:
                return None
            else:
                self.awaiting_neutral_pos = True
                self.cur_stage += 0.5

                if self.cur_stage == 0.5:
                    self.stick_pos_1 = new_zone

                elif self.cur_stage == 1.5:
                    self.stick_pos_2 = new_zone
                    letter = self.detect_letter()
                    return letter

        return None

    def reset_typing(self):
        self.stick_pos_1 = self.NEUTRAL_ZONE
        self.stick_pos_2 = self.NEUTRAL_ZONE

        self.cur_stage = 0
        self.awaiting_neutral_pos = False

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

    def __init__(self):
        self.connect()

        self.NEUTRAL_ZONE = '⬤'
        self.UNMAPPED_ZONE = '❌'

        self.msg = bytearray(1)

        self.LeftMouse = code_map["LeftMouse"]
        self.RightMouse = code_map["RightMouse"]
        self.MiddleMouse = code_map["MiddleMouse"]
        self.mouse_buttons = (self.LeftMouse, self.RightMouse, self.MiddleMouse)

        self.layout = load_layout()
        configs = load_configs()

        self.direction_hints = generate_hints(self.layout)

        for letters in self.layout.values():
            for lang, letter in letters.items():
                letters[lang] = code_map[letter]

        self.lang = 'en'

        typing_cfg = configs['typing']
        self.magnitude_threshold = typing_cfg['thresholdPct'] / 100
        angle_margin = typing_cfg['angleMargin']

        self.boundary_mapping = self.gen_boundary_mapping(angle_margin)
        self.reset_typing()

        scroll_speed = configs['scroll']['speed']['normal']
        self.scroll_every_n_pixels = scroll_speed['move_every_n_pixels']

        self.hold_dist = 10
        self.hold_time = 0.25

        self.init_pressed()
