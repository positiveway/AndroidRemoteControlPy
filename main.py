from functools import partial
from time import sleep
import math

from collections import deque


class TriggerZone:
    Up = "Up"
    Middle = "Middle"
    Down = "Down"
    NoChange = "NoChange"


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


class JoysticksController:
    def __init__(self):
        self.layout = load_layout()

        self.LeftStickZone = TriggerZone.Middle
        self.RightStickZone = TriggerZone.Middle

        self.awaiting_full_neutral = False

        self.val_history = {
            "LeftAngle": self.init_val_history(),
            "LeftMagnitude": self.init_val_history(),
            "RightAngle": self.init_val_history(),
            "RightMagnitude": self.init_val_history(),
        }

    def init_val_history(self, stack_size=2):
        return deque(stack_size * [0], maxlen=stack_size)

    def get_stick_last_val(self, attr_name):
        return self.val_history[attr_name][-1]

    def get_stick_first_val(self, attr_name):
        return self.val_history[attr_name][0]

    def set_stick_val(self, attr_name, val):
        self.val_history[attr_name].append(val)

    def shift_stick_val(self, attr_name):
        self.set_stick_val(attr_name, self.get_stick_last_val(attr_name))

    def set_val_from_events(self, events):
        for attr_name in self.val_history.keys():
            self.shift_stick_val(attr_name)

        for attr_name, cur_val in events.items():
            self.set_stick_val(attr_name, cur_val)

        # print("Events")
        # print(events)
        # print("History")
        # print(self.val_history)
        # print('=' * 100)

    def motion_stopped(self):
        diff_detected = False
        for attr_name in self.val_history.keys():
            oldest_measure = self.get_stick_first_val(attr_name)
            newest_measure = self.get_stick_last_val(attr_name)

            if (diff_val := abs(newest_measure - oldest_measure)) > self.diff_threshold:
                diff_detected = True
                # print({attr_name: {"diff": diff_val, "cur": newest_measure, "old": oldest_measure}})

        return not diff_detected

    def convert_to_arrow(self, attr_name):
        x_zone, y_zone = self.InTriggerZone[attr_name + "X"], self.InTriggerZone[attr_name + "Y"]
        return {
            (TriggerZone.Middle, TriggerZone.Up): "🢁",
            (TriggerZone.Up, TriggerZone.Up): "🢅",
            (TriggerZone.Up, TriggerZone.Middle): "🢂",
            (TriggerZone.Up, TriggerZone.Down): "🢆",
            (TriggerZone.Middle, TriggerZone.Down): "🢃",
            (TriggerZone.Down, TriggerZone.Down): "🢇",
            (TriggerZone.Down, TriggerZone.Middle): "🢀",
            (TriggerZone.Down, TriggerZone.Up): "🢄",
            (TriggerZone.Middle, TriggerZone.Middle): self.FULL_NEUTRAL,
        }[(x_zone, y_zone)]

    def get_arrow_directions(self):
        return self.convert_to_arrow("LeftJoystick"), self.convert_to_arrow("RightJoystick")

    def detect_current_letter(self):
        left_stick_pos, right_stick_pos = self.get_arrow_directions()

        if left_stick_pos == self.FULL_NEUTRAL or right_stick_pos == self.FULL_NEUTRAL:
            # return "Only one stick is used"
            return None
        try:
            return self.layout[left_stick_pos, right_stick_pos]
        except KeyError:
            return "Not defined"

    FULL_NEUTRAL = '⬤'
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)
    TRIGGER_HIGH_DOWN_VAL = 14000
    diff_threshold = 800

    def detect_trigger_zone(self, value):
        if value > self.TRIGGER_HIGH_DOWN_VAL:
            return TriggerZone.Up
        elif value < -self.TRIGGER_HIGH_DOWN_VAL:
            return TriggerZone.Down
        else:
            return TriggerZone.Middle

    def zone_changed(self, attr_name, value):
        new_zone = self.detect_trigger_zone(value)
        return self.InTriggerZone[attr_name] != new_zone

    def returned_to_neutral(self, zone):
        return zone == TriggerZone.Middle

    def check_full_neutral(self):
        if self.awaiting_full_neutral:
            if self.convert_to_arrow("LeftJoystick") == self.FULL_NEUTRAL or \
                    self.convert_to_arrow("RightJoystick") == self.FULL_NEUTRAL:
                self.awaiting_full_neutral = False

    def update_state(self, read_events_func):
        events = read_events_func()
        if events:
            self.set_val_from_events(events)
            return None

        motion_stopped = self.motion_stopped()

        zone_not_neutral = False
        changed_zones = {}

        for attr_name in self.val_history.keys():
            last_val = self.get_stick_last_val(attr_name)
            cur_zone = self.detect_trigger_zone(last_val)
            if self.zone_changed(attr_name, last_val):
                if motion_stopped:
                    changed_zones[attr_name] = cur_zone
                    self.InTriggerZone[attr_name] = cur_zone
                    if not self.returned_to_neutral(cur_zone):
                        zone_not_neutral = True

        self.check_full_neutral()

        if changed_zones:
            print(self.get_arrow_directions())

        if not self.awaiting_full_neutral and zone_not_neutral:
            self.awaiting_full_neutral = True
            return self.detect_current_letter()
        return None


from kivy.app import App
from garden_joystick import Joystick
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class Controller:
    def detect_zone(self, magnitude, angle):
        if magnitude > self.magnitude_threshold:
            for boundary, arrow in self.boundary_mapping.items():
                for cur_angle in boundary:
                    if cur_angle == angle:
                        return arrow
            return self.EDGE_ZONE
        else:
            return self.NEUTRAL_ZONE

    def gen_range(self, lower_bound, upper_bound):
        return [cur_angle for cur_angle in range(lower_bound, upper_bound)]

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
            upper_bound = map_angle + self.angle_margin
            boundary_range = self.gen_range(map_angle, upper_bound)
            if map_angle == 0:
                lower_bound = 360 - self.angle_margin
                boundary_range += self.gen_range(lower_bound, 360)
            else:
                lower_bound = map_angle - self.angle_margin
                boundary_range += self.gen_range(lower_bound, map_angle)

            boundary_mapping[tuple(boundary_range)] = arrow

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
        return {
            "🢂": 1,
            "🢅": 2,
            "🢁": 3,
            "🢄": 4,
            "🢀": 5,
            "🢇": 6,
            "🢃": 7,
            "🢆": 8,
            "⬤": -1,
            "❌": -2,
        }[zone]

    def update_zone(self, magnitude, angle, attr_prefix):
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


class DemoApp(App):
    def build(self):
        self.root = BoxLayout()
        self.root.padding = 50

        left_joystick = Joystick()
        left_joystick.bind(pad=self.update_left)
        self.root.add_widget(left_joystick)
        self.left_label = Label()
        self.root.add_widget(self.left_label)

        right_joystick = Joystick()
        right_joystick.bind(pad=self.update_right)
        self.root.add_widget(right_joystick)
        self.right_label = Label()
        self.root.add_widget(self.right_label)

    def update_coordinates(self, joystick, pad, attr_prefix):
        x = str(pad[0])[0:5]
        y = str(pad[1])[0:5]
        radians = str(joystick.radians)[0:5]
        magnitude = str(joystick.magnitude)[0:5]
        angle = str(joystick.angle)[0:5]

        letter = controller.update_zone(joystick.magnitude, joystick.angle, attr_prefix)
        if letter:
            print(letter)

            letter = ord(letter[0])
        else:
            letter = ""

        text = "Zone: {}\nletter: {}\nx: {}\ny: {}\nradians: {}\nmagnitude: {}\nangle: {}"

        return text.format(controller.get_zone(attr_prefix), letter, x, y, radians, magnitude, angle)

    def update_left(self, joystick, pad):
        self.left_label.text = self.update_coordinates(joystick, pad, "Left")

    def update_right(self, joystick, pad):
        self.right_label.text = self.update_coordinates(joystick, pad, "Right")


if __name__ == '__main__':
    DemoApp().run()
