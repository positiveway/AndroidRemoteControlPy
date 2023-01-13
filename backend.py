import json
import socket

from code_map import code_map
from wsocket import server_ip, server_port


def load_layout():
    layout = {}
    with open("layout.csv", encoding="utf8") as layout_csv:
        content = layout_csv.readlines()

    content = content[2:]
    for line in content:
        line = line.replace(' ', '').replace('\n', '').lower()
        if line and not line.startswith(';'):
            stick_positions, letters = line.split('=>')
            stick_positions = tuple(stick_positions.split('&'))

            letters = letters.replace('none', '')
            letters = letters.split(',')
            letters = [letter.capitalize() for letter in letters]

            if stick_positions in layout:
                raise ValueError(f"Repeated: {letters}")

            layout[stick_positions] = {}
            if letters[0]:
                layout[stick_positions]['en'] = letters[0]
            if letters[1]:
                layout[stick_positions]['ru'] = letters[1]

    return layout


def generate_hints(layout):
    langs = ['en', 'ru']
    directions = ["🢂", "🢅", "🢁", "🢄", "🢀", "🢇", "🢃", "🢆"]
    lang_direction_hints = {}

    for lang in langs:
        lang_direction_hints[lang] = {}
        for direction1 in directions:
            lang_direction_hints[lang][direction1] = []

    for direction1 in directions:
        for direction2 in directions:
            pos = (direction1, direction2)
            if pos in layout:
                letters = layout[pos]
                for lang, letter in letters.items():
                    lang_direction_hints[lang][direction1].append(letter)

    for lang in langs:
        for direction1 in directions:
            hints = ', '.join(lang_direction_hints[lang][direction1])
            lang_direction_hints[lang][direction1] = hints

    return lang_direction_hints


def load_configs():
    with open("configs.json", encoding="utf8") as file:
        return json.load(file)


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

        if letter == '':
            letter = self.UNMAPPED_POSITION

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

    def reset_pressed(self):
        self.pressed = {self.LeftMouse: False, self.RightMouse: False, self.MiddleMouse: False}

    def release_all(self):
        for button in self.pressed.keys():
            self.sock.send(bytes(button))
            self.pressed[button] = False

    def send_type(self, button):
        self.send_pressed(button)
        self.send_released(button)

    def send_pressed(self, button):
        res = self.pressed.get(button, False)
        if res == False:
            self.pressed[button] = True
            self.sock.send(bytes(button + 128))

    def send_released(self, button):
        res = self.pressed.get(button, True)
        if res == True:
            self.pressed[button] = False
            self.sock.send(bytes(button))

    def __init__(self):
        self.NEUTRAL_ZONE = '⬤'
        self.UNMAPPED_ZONE = '❌'
        self.UNMAPPED_POSITION = "Unmapped"

        self.LeftMouse = code_map["LeftMouse"]
        self.RightMouse = code_map["RightMouse"]
        self.MiddleMouse = code_map["MiddleMouse"]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.sock.connect((server_ip, server_port))

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
        self.move_every_n_pixels = scroll_speed['move_every_n_pixels']
        self.move_by_n_pixels = scroll_speed['move_by_n_pixels']

        self.reset_pressed()
