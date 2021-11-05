from functools import partial


def load_layout():
    layout = {}
    with open("layout.csv", encoding="utf8") as layout_csv:
        content = layout_csv.readlines()

    content = content[1:]
    for line in content:
        line = line.strip()
        if line:
            letter, leftStick, rightStick = line.split(',')
            position = (leftStick, rightStick)
            if position in layout:
                raise ValueError()

            layout[position] = letter

    return layout


class Controller:
    def detect_zone(self, magnitude, angle):
        angle = int(angle)
        if magnitude > self.magnitude_threshold:
            return self.boundary_mapping.get(angle, self.EDGE_ZONE)
        else:
            return self.NEUTRAL_ZONE

    def _gen_range(self, lower_bound, upper_bound, boundary_mapping, arrow):
        for cur_angle in range(lower_bound, upper_bound):
            boundary_mapping[cur_angle] = arrow

    def gen_boundary_mapping(self):
        mapping = {
            0: "🢂",
            45: "🢅",
            90: "🢁",
            135: "🢄",
            180: "🢀",
            225: "🢇",
            270: "🢃",
            315: "🢆",
        }
        boundary_mapping = {}

        for map_angle, arrow in mapping.items():
            gen_range = partial(self._gen_range, boundary_mapping=boundary_mapping, arrow=arrow)

            upper_bound = map_angle + self.angle_margin
            gen_range(map_angle, upper_bound)
            if map_angle == 0:
                lower_bound = 360 - self.angle_margin
                gen_range(lower_bound, 360)
            else:
                lower_bound = map_angle - self.angle_margin
                gen_range(lower_bound, map_angle)

        return boundary_mapping

    def detect_letter(self):
        cur_zones = (self.LeftStickZone, self.RightStickZone)
        for zone in cur_zones:
            if zone == self.NEUTRAL_ZONE:
                return None
            elif zone == self.EDGE_ZONE:
                raise ValueError()

        self.awaiting_neutral_pos = True
        try:
            return self.layout[cur_zones]
        except KeyError as error:
            print(error)
            return 'Undefined'

    def get_zone(self, attr_prefix):
        attr_name = attr_prefix + "StickZone"
        zone = getattr(self, attr_name)
        return zone

    def update_zone(self, magnitude, angle, attr_prefix):
        letter = self._update_zone(magnitude, angle, attr_prefix)
        if letter is None:
            letter = ""
        return letter

    def _update_zone(self, magnitude, angle, attr_prefix):
        angle = int(angle)
        attr_name = attr_prefix + "StickZone"
        prev_zone = getattr(self, attr_name)
        new_zone = self.detect_zone(magnitude, angle)
        if new_zone == self.EDGE_ZONE:
            return None

        if new_zone != prev_zone:
            setattr(self, attr_name, new_zone)
            if self.awaiting_neutral_pos:
                if new_zone == self.NEUTRAL_ZONE:
                    self.awaiting_neutral_pos = False
            else:
                return self.detect_letter()

        return None

    NEUTRAL_ZONE = '⬤'
    EDGE_ZONE = '❌'
    angle_margin = 15
    magnitude_threshold_pct = 75
    magnitude_threshold = magnitude_threshold_pct / 100

    def __init__(self) -> None:
        self.layout = load_layout()
        self.boundary_mapping = self.gen_boundary_mapping()

        self.LeftStickZone = self.NEUTRAL_ZONE
        self.RightStickZone = self.NEUTRAL_ZONE

        self.awaiting_neutral_pos = False


controller = Controller()
