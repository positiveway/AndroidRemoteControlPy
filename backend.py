import json


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

            if stick_positions in layout:
                raise ValueError(f"Repeated: {letters}")

            layout[stick_positions] = {'en': letters[0], 'ru': letters[1]}

    return layout


def load_configs():
    with open("configs.json", encoding="utf8") as file:
        return json.load(file)


def resole_angle(angle):
    return (angle + 360) % 360


class Controller:
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
        print(f'no letter for this position: {stick_positions} or lang: {self.lang}, error: {error}')

    def detect_letter(self) -> str | None:
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
            letter = 'Undef'

        return letter

    def update_zone(self, magnitude, angle) -> str | None:
        if self.stick_1_not_set:
            prev_zone = self.stick_pos_1
        else:
            prev_zone = self.stick_pos_2

        new_zone = self.detect_zone(magnitude, angle)

        # print(f'1 not set: {self.stick_1_not_set}, prev: {prev_zone}, new: {new_zone}, pos 1: {self.stick_pos_1}, pos2: {self.stick_pos_2}')

        if new_zone == self.UNMAPPED_ZONE or new_zone == prev_zone:
            return None

        if new_zone == self.NEUTRAL_ZONE:
            self.awaiting_neutral_pos = False

            if self.stick_1_not_set:
                self.stick_1_not_set = False
                # print("set 1 full")
            else:
                self.reset()
        else:
            if self.awaiting_neutral_pos:
                return None
            else:
                self.awaiting_neutral_pos = True

            if self.stick_1_not_set:
                # print("set 1 init")
                self.stick_pos_1 = new_zone
            else:
                self.stick_pos_2 = new_zone
                letter = self.detect_letter()
                return letter

        return None

    def reset(self):
        self.stick_pos_1 = self.NEUTRAL_ZONE
        self.stick_pos_2 = self.NEUTRAL_ZONE

        self.stick_1_not_set = True
        self.awaiting_neutral_pos = False

    NEUTRAL_ZONE = '⬤'
    UNMAPPED_ZONE = '❌'

    def __init__(self):
        self.layout = load_layout()
        self.configs = load_configs()

        self.lang = 'en'

        typing_cfg = self.configs['typing']
        self.magnitude_threshold = typing_cfg['thresholdPct'] / 100
        angle_margin = typing_cfg['angleMargin']

        self.boundary_mapping = self.gen_boundary_mapping(angle_margin)

        self.reset()


controller = Controller()

if __name__ == '__main__':
    while True:
        input()
